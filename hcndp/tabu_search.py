# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 07:21:16 2024

@author: edgar
"""

import copy
import random
from hcndp import initial_solution
from itertools import permutations
import pandas as pd
from hcndp import kpi


def local_search(current_solution,network_original):
    # Basado en Talbin (2009). Algoritmo 2.2
    # Definiciones:
    # current_solution: Objeto contenedor que agrupa: objetivo, red, datos, resultados, técnica, etc.
    # current_Solution se modifica durante el código. 
    # network_original: Objeto con datos originales de la red. No se modifica durante el código. Permance como referencia.
        
    landscape=[] # Vector para guardar la información del landscape construido
    
    # Cálculo de solución inicial
    current_neighbor = initial_solution.initial_solution(current_solution,network_original)
    calcular_kpi_local_search(current_neighbor) #Mido KPI de solución inicial
    
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    current_neighbor = initial_solution.fix_initial_solution(current_neighbor)  
    
    # Inicializar el valor de la mejor solución encontrada
    best_neighbor = copy.deepcopy(current_neighbor)
    calcular_kpi_local_search(best_neighbor)# Calculo KPIs
    
    #qual_best = Función objetivo. En este caso rho_max
    qual_best=best_neighbor.network_copy.file['df_medidas']['rho_max'][0] 
    
    # Construyo lista para almacenar representaciones de soluciones (landscape)
    # lista es el vector de sigmas de best_neighbor
    lista = [_j.capac_instal_sigma for _i, _j in best_neighbor.network_repr.nodes_supply.items() if _j.service != 'k00']
    lista_sigma_y_fo=[lista,qual_best] # Vector de sigmas y su función objetivo 
    landscape.append([lista_sigma_y_fo]) #Guardo primer elemento del landscape
    
    print (f'Solución inicial')
    print (f"Vector sigmas: {best_neighbor.df_sigma['sigma_jk'].tolist()}")
    print (f'Valor función objetivo inicial: {qual_best}')
    #print (best_neighbor.network_copy.file['df_medidas']['rho_max'][0])

    # Bucle principal
    # Mientras no se cumpla el criterio de parada
    # Condiciones de parada: https://www.sciencedirect.com/science/article/pii/S2214716023000180
    
    stopping_condition_N_rule = False # N-rule: maximum number of iterations 
    contador=1 
    i= 3 #Iteraciones de la búsqueda local. Criterio de parada.
    
    stopping_condition_W_rule = False # W-rule: maximum number of consecutive iterations without improvement in the value of the incumbent solution 
    iterations_without_improvement = 0
    max_iterations_without_improve = 5
        
    qual_best_of_neighborhood=10.0

    
    #while contador <=  i:
    
    while stopping_condition_W_rule == False:
        
        print (f'Vecindario número = {contador}')       
        
        # Generar vecindario a partir de la mejor solución hallada
        # neighbor es un objeto solución (contiene matrices, nodos, arcos, etc)
        # neighborhood es el vecindario del objeto neighbor
        # neighborhood es una lista que contiene sublistas. Una para cada k
        # Cada sublista de k contiene las permutaciones posibles para sus sigma
        # Las sublistas representan los sigma asignados para cada j y para cada k
        # Ej: neighborhood = [sublista1, sublista2, sublista3]
        # sublista1 = [nodej1,nodej2,nodej3,nodej4] Nodos de servicio para servicio k=1
        # sublista2 = [nodej1,nodej2,nodej3,nodej4] Nodos de servicio para servicio k=2
        
        #Construyo lista exhaustiva del vecindario
        neighbor = copy.copy(best_neighbor) # objeto solución
        neighborhood = neighborhood_exhaustive(neighbor) # Lista de k sublistas. Cada sublista contiene objetos nodos de servicio
        # Ver neighborhood_exhaustive para cambiar operador de generación de vecindario
        
        neighborhood_size=len(neighborhood)*len(neighborhood[0]) #Tamaño del vecindario
        
        # Tamizaje de soluciones
        # Las soluciones no pueden tener sigmas negativos o que superen s_jk o cuya suma sea mayor a sigma_max
        print ("Tamizaje de soluciones")
        neighborhood_feasible=[]
        neighborhood_infeasible=[]
        for _k in neighborhood: # Para cada vecindario de k
            for _solucion in _k:
                if (all(x.capac_instal_sigma <= x.capac_instal_max for x in _solucion) and
                   all(x.capac_instal_sigma >= 0 for x in _solucion) and
                   sum(x.capac_instal_sigma for x in _solucion) <= neighbor.network_copy.file['df_s_jk_max'].set_index('servicio_K').loc[_solucion[0].service,'s_jk_total']):
                       neighborhood_feasible.append(_solucion) #Vecindario donde se hará la búsqueda
                else:
                       neighborhood_infeasible.append(_solucion)
        
        # Para los vecindarios factibles, construyo un modelo de optimización
        # Que genere las variables adicionales tao y phi (flujos)
        # En este modelo, sigma es un parámetro y no una variable
        
        print ("Optimización para hallar flujos")
        # Actualizo los valores sigma de cada solución factible en nodes supply.capac_instal_sigma
        
        
        for _vector_changed in neighborhood_feasible: #Para cada solucion del vecindario factible
            neighbor_copy=copy.deepcopy(neighbor) #neighbor es un objeto solution
            
            for _i,_j in neighbor_copy.network_repr.nodes_supply.items():
                for _k in _vector_changed:
                    if _j.node_id == _k.node_id:
                        _j.capac_instal_sigma=_k.capac_instal_sigma
                        _j.capac_instal_disponible = _j.capac_instal_max-_j.capac_instal_sigma
            
            for _i,_j in neighbor_copy.network_repr.nodes_supply.items():
                a = _j.place
                b = _j.service
                c = _j.capac_instal_sigma
            
                fila = neighbor_copy.network_copy.file['df_capac'].query('nombre_J == @a and servicio_K == @b')
                
                if not fila.empty:
                    # Si hay coincidencias, remplazar el sigma existente por c
                    neighbor_copy.network_copy.file['df_capac'].loc[fila.index, 'sigma_jk'] = c
            
            # Procedo a aplicar modelo de optimización para hallar flujos
            # Creo el modelo abstracto en pyomo - Gurobi
            neighbor_copy.construct_model()
            # Creo el archivo datos.dat para ejecutar pyomo - Gurobi
            current_solution.network_copy.create_data_dat()
            neighbor_copy.construct_instance()
            
            # Fijo los nuevos valores de sigma en la instancia
            # Con esta estrategia no tengo que construir un nuevo modelo abstracto
            #print (f"Solucionando modelo de optimización para {[x.node_id for x in _vector_changed]}")
            for _i,_j in neighbor_copy.network_repr.nodes_supply.items():
                _new_sigma=_j.capac_instal_sigma
                if _j.service != 'k00':
                 neighbor_copy.pyo_model.instance.sigma[_j.place,_j.service].fix(_new_sigma)
            
            neighbor_copy.execute_solver() # Ejecuto pyomo Gurobi

            # Guardo neighbor_copy como vecino de best_neighbor en la lista de adyacencia.
            lista = [_j.capac_instal_sigma for _i, _j in neighbor_copy.network_repr.nodes_supply.items() if _j.service != 'k00']
            calcular_kpi_local_search(neighbor_copy) # Actualizo KPI
            func_obj = neighbor_copy.network_copy.file['df_capac']['rho'].max() #Obtengo el rho max
            landscape[-1].append([lista,func_obj]) ##Guardo vecinos de best_neighbor

            # Busco la mejor solución en neighborhood_feasible
            if neighbor_copy.state=="Optimizado" and neighbor_copy.value_optimal_solution['Func_obj'] < qual_best_of_neighborhood:
                qual_best_of_neighborhood=neighbor_copy.value_optimal_solution['Func_obj']
                best_of_neighborhood=neighbor_copy
                
        print (f'Vecindario número = {contador}, mejor solución del vecindario: {qual_best_of_neighborhood}')
        
        print ("Comparación de resultados")
        # Comparo la mejor solución del vecindario con la mejor solución obtenida.
        if qual_best_of_neighborhood < qual_best:
            qual_best=qual_best_of_neighborhood 
            best_neighbor = copy.deepcopy(best_of_neighborhood)
            calcular_kpi_local_search(best_neighbor)# Calculo KPIs
            
            # Hubo mejora, el contador de mejoras se hace cero
            iterations_without_improvement = 0
            
            #landscape.append([best_neighbor]) # Agrego una nueva línea a la lista de adyacencia del landscape
            lista = [_j.capac_instal_sigma for _i, _j in best_neighbor.network_repr.nodes_supply.items() if _j.service != 'k00']
            lista_sigma_y_fo=[lista,qual_best]
            landscape.append([lista_sigma_y_fo]) # Agrego una nueva línea a la lista de adyacencia del landscape
            
        else: #No hubo mejora
            iterations_without_improvement += 1
        
        # Actualizo el criterio de parada
        if iterations_without_improvement > max_iterations_without_improve:
            stopping_condition_W_rule = True
        
        if contador == i:
            stopping_condition_N_rule = True
            
        contador +=1
    
    print ("Resultado final")
    
    print (f"Operador: {best_neighbor.local_search_operator}")
    print (f"Mejor solución alcanzada: {best_neighbor.df_sigma['sigma_jk'].tolist()}")
    print (f"Valor función objetivo: {best_neighbor.network_copy.file['df_medidas']['rho_max'][0] }")
    print (f"Vecindario final número: {contador-1}")
    best_neighbor.landscape=landscape
    current_solution = copy.deepcopy(best_neighbor)
    
    return current_solution
    
def neighborhood_exhaustive(_solucion): #_solucion es un objeto
    neighborhood=[] # Vecindario de _solucion
    
    # Determino si obtengo soluciones teniendo en cuenta los valores de rho en cada vector de _k
    # Solamente hago permutaciones en los vectores de los peores servicio k
    
    # Asegúrate de tener el DataFrame que estás manipulando
    df_capac1 = _solucion.network_copy.file['df_capac']

    # Establece 'servicio_K' como índice
    #df_capac1.set_index('servicio_K', inplace=True)

    # Asegúrate de que 'rho' esté en el DataFrame
    if 'rho' not in df_capac1.set_index('servicio_K').columns:
        raise KeyError("'rho' no se encuentra en el DataFrame")

    # Agrupa por 'servicio_K' y luego obtiene el valor máximo de 'rho'
    grouped_max = df_capac1.set_index('servicio_K').groupby('servicio_K')['rho'].max()
    grouped_max=grouped_max.reset_index()
    
    
    # Verificar el número de cuartiles
    q = 4  # Intentar dividir en 4 cuartiles
    
    # Verificar el número de etiquetas
    labels = ['Q1', 'Q2', 'Q3', 'Q4']  # 4 etiquetas para 4 cuartiles
    
    # Si hay menos valores únicos, ajustar los cuartiles
    while True: 
        try:
            grouped_max['cuartil_b'] = pd.qcut(grouped_max['rho'], q=q, labels=labels, duplicates='drop')
            break
        except ValueError as e:
            print("Error:", e)
            
            # Ajustar el número de cuartiles y etiquetas si hay error
            #q = grouped_max['rho'].nunique()  # Ajustar al número de valores únicos
            #labels = labels[q-1:]  # Ajustar el número de etiquetas
        
            # Intentar de nuevo con el número correcto de cuartiles y etiquetas
            #grouped_max['cuartil_b'] = pd.qcut(grouped_max['rho'], q=q, labels=labels, duplicates='drop')    
            #grouped_max['cuartil_b']='Q4'
            labels.pop(0)
            q-=1
        
    # Para cada servicio k 
    for _k in _solucion.network_copy.file['df_niveles']['servicio_K']:
        
        # Si el servicio _k está en el cuartil q2, Q3 o Q4. 
        # Si no está, significa que no está congestionado y por lo tanto no lo agrego al vecindario
        if (_k in grouped_max[grouped_max['cuartil_b'] == 'Q4']['servicio_K'].values): #or\
           #(_k in grouped_max[grouped_max['cuartil_b'] == 'Q3']['servicio_K'].values):

            nodes_k = [] # Lista con nodos del servicio _k. Es la lista de los nodos de servicio jk
            
            # Crear una lista con nodos del servicio _k 
            for _i, _j in _solucion.network_repr.nodes_supply.items():
                if _j.service == _k:
                    # Agregar los elementos a la lista
                    nodes_k.append((_j))
            
            #print("\n".join(str(obj) for obj in nodes_k))
    
            # Aplico el operador de perturbación para generar nuevos vecindarios
            # nodes_k: lista de objetos nodos en el servicio _k
            # _k: servicio o vector k
            # _solución: solución desde la que se construye el vecindario
            
            #Posibles operadores:
            #--------------------
            #neighborhood_k = incremento1_decremento1_exhaust(nodes_k,_k,_solucion) 
            #neighborhood_k = incremento1_exhaust (nodes_k,_k,_solucion)
            #neighborhood_k = incremento1_all (nodes_k,_k,_solucion)
            #neighborhood_k = incremento2_decremento1_exhaust(nodes_k,_k,_solucion) 
            #neighborhood_k = incremento2_decremento2_exhaust(nodes_k,_k,_solucion) 
            #neighborhood_k = incremento3_decremento3_exhaust(nodes_k,_k,_solucion) 
            #neighborhood_k = chain_reaction_exhaust_plus_minus(nodes_k,_k,_solucion)
            #neighborhood_k = chain_reaction_exhaust_minus_plus(nodes_k,_k,_solucion)
            
            # Si se ejecuta desde __name__ == "__main__"
            if __name__ == "__main__":
                neighborhood_k = incremento1_exhaust (nodes_k,_k,_solucion)
                _solucion.local_search_operator="incremento1_exhaust (nodes_k,_k,_solucion)"

            else:
                neighborhood_k = eval(_solucion.local_search_operator)
    
            
            #Devuelve un listado de soluciones (listas de nodes_K) para cada _k        
            neighborhood.append(neighborhood_k)
        
    
    return neighborhood


#%% Operadores para generar vecindarios
   

def incremento1_decremento1_exhaust (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    #print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Selecciono todas las permutaciones de dos elementos de vector_original.
    # Cada permutación es de dos elementos sigma_1 y sigma_2.
    # Sumo 1 a sigma_1 y resto 1 a sigma_2.
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    for i in range(len(vector_original_sigmas)):
        
        for j in range(len(vector_original_sigmas)):
            copia_vector_original_sigmas=vector_original_sigmas.copy()
            if i != j:
                copia_vector_original_sigmas[i]= vector_original_sigmas[i]+1
                copia_vector_original_sigmas[j]= vector_original_sigmas[j]-1
                print (f'Sigma {i} era {vector_original_sigmas[i]} y sigma {j} era {vector_original_sigmas[j]}, Nuevo vector es {copia_vector_original_sigmas}')
            
                # Decodifico copia_vector_original_sigmas en nodes
                copia_nodes=copy.deepcopy(nodes)
                for index, value in enumerate(copia_nodes):
                    value.capac_instal_sigma = copia_vector_original_sigmas[index]
                
                lista_nodes_perturbados.append(copia_nodes)
                
    return lista_nodes_perturbados

def incremento1_exhaust (nodes,_k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Selecciono cada elemento de vector_original.
    # Sumo 1 al sigma de ese elemento.
    # Este operador SÍ CAMBIA la cantidad total de servidores asignados.
    # Por lo tanto debo verificar que no supere el sigma_max_k. 
    # Esta verificación se hace posteriormente en el tamizaje de soluciones.
    
    for i in range(len(vector_original_sigmas)):
        
            copia_vector_original_sigmas=vector_original_sigmas.copy()

            copia_vector_original_sigmas[i]= vector_original_sigmas[i]+1
                
            print (f'Sigma {i} era {vector_original_sigmas[i]}. Nuevo vector es {copia_vector_original_sigmas}')
            
            # Decodifico copia_vector_original_sigmas en nodes
            copia_nodes=copy.deepcopy(nodes)
            for index, value in enumerate(copia_nodes):
                value.capac_instal_sigma = copia_vector_original_sigmas[index]
            
            lista_nodes_perturbados.append(copia_nodes)
            
    return lista_nodes_perturbados

def incremento1_all (nodes,_k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Sumo 1 a todos los sigma del elemento.
    # Este operador SÍ CAMBIA la cantidad total de servidores asignados.
    # Por lo tanto debo verificar que no supere el sigma_max_k. 
    # Esta verificación se hace posteriormente en el tamizaje de soluciones.
    
    copia_vector_original_sigmas=vector_original_sigmas.copy()

    copia_vector_original_sigmas = [x+1 for x in copia_vector_original_sigmas]
                
    print (f'Vector sigmas original era {vector_original_sigmas}. Nuevo vector sigmas es {copia_vector_original_sigmas}')
            
    # Decodifico copia_vector_original_sigmas en nodes
    copia_nodes=copy.deepcopy(nodes)
    for index, value in enumerate(copia_nodes):
        value.capac_instal_sigma = copia_vector_original_sigmas[index]
    
    lista_nodes_perturbados.append(copia_nodes)
            
    return lista_nodes_perturbados

def incremento2_decremento1_exhaust (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Selecciono todas las permutaciones de dos elementos de vector_original.
    # Cada permutación es de dos elementos sigma_1 y sigma_2.
    # Sumo a sigma_1 y resto a sigma_2.
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    for i in range(len(vector_original_sigmas)):
        
        for j in range(len(vector_original_sigmas)):
            copia_vector_original_sigmas=vector_original_sigmas.copy()
            if i != j:
                copia_vector_original_sigmas[i]= vector_original_sigmas[i]+2
                copia_vector_original_sigmas[j]= vector_original_sigmas[j]-1
                print (f'Sigma {i} era {vector_original_sigmas[i]} y sigma {j} era {vector_original_sigmas[j]}, Nuevo vector es {copia_vector_original_sigmas}')
            
                # Decodifico copia_vector_original_sigmas en nodes
                copia_nodes=copy.deepcopy(nodes)
                for index, value in enumerate(copia_nodes):
                    value.capac_instal_sigma = copia_vector_original_sigmas[index]
                
                lista_nodes_perturbados.append(copia_nodes)
                
    return lista_nodes_perturbados

def incremento2_decremento2_exhaust (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Selecciono todas las permutaciones de dos elementos de vector_original.
    # Cada permutación es de dos elementos sigma_1 y sigma_2.
    # Sumo a sigma_1 y resto a sigma_2.
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    for i in range(len(vector_original_sigmas)):
        
        for j in range(len(vector_original_sigmas)):
            copia_vector_original_sigmas=vector_original_sigmas.copy()
            if i != j:
                copia_vector_original_sigmas[i]= vector_original_sigmas[i]+2
                copia_vector_original_sigmas[j]= vector_original_sigmas[j]-2
                print (f'Sigma {i} era {vector_original_sigmas[i]} y sigma {j} era {vector_original_sigmas[j]}, Nuevo vector es {copia_vector_original_sigmas}')
            
                # Decodifico copia_vector_original_sigmas en nodes
                copia_nodes=copy.deepcopy(nodes)
                for index, value in enumerate(copia_nodes):
                    value.capac_instal_sigma = copia_vector_original_sigmas[index]
                
                lista_nodes_perturbados.append(copia_nodes)
                
    return lista_nodes_perturbados

def incremento3_decremento3_exhaust (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Selecciono todas las permutaciones de dos elementos de vector_original.
    # Cada permutación es de dos elementos sigma_1 y sigma_2.
    # Sumo a sigma_1 y resto a sigma_2.
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    for i in range(len(vector_original_sigmas)):
        
        for j in range(len(vector_original_sigmas)):
            copia_vector_original_sigmas=vector_original_sigmas.copy()
            if i != j:
                copia_vector_original_sigmas[i]= vector_original_sigmas[i]+3
                copia_vector_original_sigmas[j]= vector_original_sigmas[j]-3
                print (f'Sigma {i} era {vector_original_sigmas[i]} y sigma {j} era {vector_original_sigmas[j]}, Nuevo vector es {copia_vector_original_sigmas}')
            
                # Decodifico copia_vector_original_sigmas en nodes
                copia_nodes=copy.deepcopy(nodes)
                for index, value in enumerate(copia_nodes):
                    value.capac_instal_sigma = copia_vector_original_sigmas[index]
                
                lista_nodes_perturbados.append(copia_nodes)
                
    return lista_nodes_perturbados

def chain_reaction_exhaust_plus_minus (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Creo un vectorcadena  +1 -1 +1 -1 ... del mismo tamaño de vector sigmas
    # Sumo vector sigmas a vectorcadena
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    vectorcadena = [1 if i % 2 == 0 else -1 for i in range(len(vector_original_sigmas))]

    copia_vector_original_sigmas=vector_original_sigmas.copy()
    copia_vector_original_sigmas = [x + y for x, y in zip(copia_vector_original_sigmas, vectorcadena)]
    
    print (f'Vector original era {vector_original_sigmas}. Nuevo vector es {copia_vector_original_sigmas}')
           
    # Decodifico copia_vector_original_sigmas en nodes
    copia_nodes=copy.deepcopy(nodes)
    for index, value in enumerate(copia_nodes):
        value.capac_instal_sigma = copia_vector_original_sigmas[index]
    
    lista_nodes_perturbados.append(copia_nodes)
            
    return lista_nodes_perturbados

def chain_reaction_exhaust_minus_plus (nodes, _k,_solucion):
    # Obtengo los nodos perturbados para el servicio _k
    lista_nodes_perturbados=[]
    
    # Codificación. Paso de los objetos nodes a un vector con sigmas. 
    vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes]
    print (f'Servicio del vector sigmas: {nodes[0].service}')
    print (f'Vector sigmas original: {vector_original_sigmas}')
    
    # Aplico operador al vector codificado
    # Creo un vectorcadena  +1 -1 +1 -1 ... del mismo tamaño de vector sigmas
    # Sumo vector sigmas a vectorcadena
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    vectorcadena = [-1 if i % 2 == 0 else 1 for i in range(len(vector_original_sigmas))]

    copia_vector_original_sigmas=vector_original_sigmas.copy()
    copia_vector_original_sigmas = [x + y for x, y in zip(copia_vector_original_sigmas, vectorcadena)]
    
    print (f'Vector original era {vector_original_sigmas}. Nuevo vector es {copia_vector_original_sigmas}')
           
    # Decodifico copia_vector_original_sigmas en nodes
    copia_nodes=copy.deepcopy(nodes)
    for index, value in enumerate(copia_nodes):
        value.capac_instal_sigma = copia_vector_original_sigmas[index]
    
    lista_nodes_perturbados.append(copia_nodes)
            
    return lista_nodes_perturbados



def incremento_decremento_prob (vector_original, vector_constraint,selected_service,_solucion):
    # Recorro el vector y para cada posición con un valor no cero 
    # calculo una probabilidad. Si se supera un valor base 
    # se decide aumentarlo o disminuirlo en una unidad. 
    #Se basa en el algoritmo Random Walk Mutation del libro de Luke (Algoritmo 42).     
    
    #p = 1/len(vector_original) # Probabilidad de perturbar un sigma
    p = 0.4
    #b = 0.5 # Probabilidad lanzar moneda
        
    copia_vector_original=vector_original.copy()
    
    # Repito perturbación hasta que la suma del vector sea menor a sigma_max del servicio "selected_service"
    sum_copia_vector=100000000
    while sum_copia_vector > _solucion.network_copy.file['df_s_jk_max'].set_index('servicio_K').loc[selected_service,'s_jk_total']:
        for i in range (len(copia_vector_original)):
            if p >= random.random() and vector_constraint[i]!=0: # Decido si perturbo sigma_i
            #if p >= random.random() and copia_vector_original[i]!=0: # Decido si perturbo sigma_i
                n = random.choice([1, -1]) 
                if copia_vector_original[i] + n <= vector_constraint[i]:
                    copia_vector_original[i]=copia_vector_original[i]+n
                elif copia_vector_original[i] - n >= vector_constraint[i]:
                    copia_vector_original[i]=copia_vector_original[i]-n
        sum_copia_vector = sum(copia_vector_original)
            
    return copia_vector_original



def calcular_kpi_local_search(current_solution):
    current_solution

    # Creo carpetas para current solution
    current_solution.create_folders_problem()
    # Si hay función objetivo (resultado de optimización)
    # Actualizo las matrices de solution.network_copy
    current_solution.network_copy.tecnica=current_solution.tecnica
    current_solution.network_copy.problem=current_solution #Creo una referencia al objeto padre Problem
    
    current_solution.network_copy.merge_niveles_capac(_post_optima=True)
    current_solution.network_copy.create_df_asignacion(_post_optima=True)
    current_solution.network_copy.create_df_probs_kk()
    current_solution.network_copy.create_df_arcos(_post_optima=True)
                     
    kpi.calculate_kpi(current_solution,_post_optima=True)
    #print (f"Se calcularon los KPI para la solución {current_solution.description_objective}.")

    # Calculo los rho para cada nodo jk y lo almaceno en nodes_supply
    for _i,_j in current_solution.network_repr.nodes_supply.items():
        if _j.service != 'k00':
            if _j.matriz_λ['λ_ijk'].sum() == 0:
                _j.rho=0
            else: 
                _j.rho = _j.matriz_λ['λ_ijk'].sum()/(_j.capac_instal_sigma*_j.rate)


    
# %% <codecell> main
if __name__ == "__main__":

        from hcndp import data_functions
        import os
        
        # Obtener el directorio de trabajo actual
        directorio_actual = os.getcwd()
        
        # Obtener el directorio padre (un nivel más arriba)
        directorio_padre = os.path.dirname(directorio_actual)
        
        archivo=directorio_padre+'/data/red_original/'+"datos_i16_j10_k10_base.txt"
        #archivo = r"C:\Users\edgar\OneDrive - Universidad Libre\Doctorado\Códigos Python\HcNDP\Health-Care-Network-Design-Problem\hcndp/data/red_original/datos_i16_j10_k10_base.xlsx"
        
        # Borro carpeta con resultados de ejecuciones previas 
        data_functions.borrar_contenido_carpeta(os.getcwd()+'/output/')
        print("\nContenidos borrados. \nContinuando...")
        
        # Creo los diccionarios de trabajo
        from hcndp import read_data
        networks_dict={} #Diccionario con las redes utilizadas en el programa
        problems_dict={} #Diccionario con los problemas y las soluciones a la red del programa

        # Definimos valores I,J,K
        I,J,K= [3,3,5]
        
        
        # Creamos un objeto network
        from hcndp import network
        _name="red_original"
        networks_dict[_name] = network.Network(I,J,K,archivo,_name)
        networks_dict[_name].create_folders()
        print (f"\nSe ha creado exitosamente el objeto {_name}.")


        # Llenar objeto con datos (En este caso, datos .txt)
        networks_dict[_name].read_file_txt(archivo)
        networks_dict[_name].delete_surplus_data() #Borro los datos que sobren
        networks_dict[_name]=read_data.fix_sigma_max(networks_dict, _name) #Corrijo errores en sigma_max

        print ("#" * 60)
        print (f"\nSe han cargado exitosamente los datos en el objeto {_name}.")
    

        # Creo el objeto solucion
        from hcndp import solutions
        solutions.create_problem_object(networks_dict['red_original'], problems_dict, name_problem="temporal")
        current_solution = problems_dict["temporal"]

        # Defino objetivo y método
        current_solution.optimizar=True
        current_solution.tecnica="Local_Search"
        _objective_and_description =['1', 'Minimizar congestión máxima (rho)']
        current_solution.objective = _objective_and_description[0]
        current_solution.description_objective = _objective_and_description[1]
        current_solution.name_problem = _objective_and_description[1]+" "+current_solution.tecnica
        
        # Actualizo nombre de la solución en solution_dict (Ya no es "temporal")
        _clave_temporal = 'temporal'
        _solucion_temporal = problems_dict[_clave_temporal]
        problems_dict[_solucion_temporal.name_problem] = problems_dict.pop(_clave_temporal)
        problems_dict[_solucion_temporal.name_problem].network_copy.name_problem = \
            problems_dict[_solucion_temporal.name_problem].name_problem
        print (f"Se ha actualizado el objeto {problems_dict[_solucion_temporal.name_problem].name_problem}")
                
        # Ejecuto local search
        current_solution= local_search(current_solution,networks_dict['red_original'])
        
        