# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 07:21:16 2024

@author: edgar
"""

import copy
import random
from hcndp import initial_solution
from hcndp import data_functions
import pandas as pd
from hcndp import kpi


def tabu_search(current_solution,network_original):
    # Basado en Glover (https://www.researchgate.net/publication/242527226_Tabu_Search_A_Tutorial)
    # Definiciones:
    # current_solution: Objeto contenedor que agrupa: objetivo, red, datos, resultados, técnica, etc.
    # network_original: Objeto con datos originales de la red. No se modifica durante el código. Permance como referencia.
    # tabu_list: conjunto de movimientos tabú
    
    tabu_list=[]   
    tennure = 5
    landscape=[] # Vector para guardar la información del landscape construido
    
    # Cálculo de solución inicial
    current_neighbor = initial_solution.initial_solution(current_solution,network_original)
    calcular_kpi_local_search(current_neighbor) #Mido KPI de solución inicial
    
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    current_neighbor = initial_solution.fix_initial_solution(current_neighbor)  
    
    # Defino la mejor solución encontrada
    best_neighbor = copy.deepcopy(current_neighbor)
    calcular_kpi_local_search(best_neighbor)# Calculo KPIs
    qual_best=best_neighbor.network_copy.file['df_medidas']['rho_max'][0] 
    
    # Agrego solución a landscape
    agregar_solucion_landscape (landscape,best_neighbor,qual_best)
    
    # CODIFICACIÓN DE SOLUCIÓN
    # Codifico la solución inicial
    current_neighbor_codificado=codificar_solucion(best_neighbor,'sigma')
        
    print (f'Solución inicial construida')
    print (f"Vectores sigmas:")
    for i,j in current_neighbor_codificado.items():
        if 'sigmas' in j:
            print (i,j['sigmas']) 
    _best_rho=current_neighbor_codificado["k_rho_max"]
    print (f'Valor función objetivo inicial: {current_neighbor_codificado[_best_rho]["rho_max"][0]}')



    # BUCLE PRINCIPAL
    
    # Condiciones de parada: https://www.sciencedirect.com/science/article/pii/S2214716023000180
    # N-rule: maximum number of iterations 
    stopping_condition_N_rule = False 
    contador=1 
    iterations_to_do= 3 #Iteraciones de la búsqueda local. Criterio de parada.
    
    # W-rule: maximum number of consecutive iterations without improvement in the value of the incumbent solution 
    stopping_condition_W_rule = False 
    iterations_without_improvement = 0
    max_iterations_without_improve = 3

    while stopping_condition_W_rule == False:
        
        print (f'Vecindario número = {contador}')       
        
        # Generar vecindario a partir de la mejor solución hallada
        # neighbor es un objeto solución (contiene matrices, nodos, arcos, etc)
        # neighbor_codificado es la codificación del objeto neighbor (diccionario)
        # neighborhood es el vecindario de neighbor
        
        # Defino la solución actual neighor
        neighbor = copy.deepcopy(current_neighbor) # objeto solución
        neighbor_codificado = codificar_solucion(neighbor,'sigma')
               
        try: 
            operador=current_solution.local_search_operator
        except AttributeError :
            operador="incremento1_exhaust(vector_original_sigmas)"
            pass
        
        # Construyo el vecindario. Conjunto de soluciones codificadas según operador seleccionado
        neighborhood = neighborhood_exhaustive_codificado(neighbor_codificado,operador) 
                
        # Tamizaje de soluciones
        neighborhood_feasible=tamizaje_soluciones(best_neighbor,neighborhood)
        # Si el vecindario factible está vacío
        if len(neighborhood_feasible) == 0:
             best_of_neighborhood = neighbor
             best_of_neighborhood_cod = codificar_solucion(best_of_neighborhood,'sigma')
             best_of_neighborhood = optimizacion(best_of_neighborhood_cod ,best_of_neighborhood,current_solution)
             qual_best_of_neighborhood=best_of_neighborhood.value_optimal_solution['Func_obj'] 

        # Selecciono la nueva solución del vecindario 
        # para comparar con best_neighbor
        new_solution_ready=False
        
        while new_solution_ready == False and len(neighborhood_feasible) != 0:
            # Encuentro mejor solución del vecindario

            best_of_neighborhood , qual_best_of_neighborhood , landscape, neighborhood_feasible =\
            find_best_of_neighborhood (neighborhood_feasible,
                                       neighbor,
                                       landscape,current_solution)
            print (f'Mejor solución del vecindario {contador}: {qual_best_of_neighborhood}')
            
            # Determino los movimientos realizados     
            # Movimiento_tabu=[servicioK,nodoJ,sigma_nuevo,sigma_original,tennure]
            best_of_neighborhood_cod=codificar_solucion(best_of_neighborhood, 'sigma')
            movimientos_realizados = movimiento_realizado (best_of_neighborhood_cod, neighbor_codificado, tennure)
            
            # Actualizo lista tabú
            if len(tabu_list) != 0:
                for i in tabu_list:
                    i[4]-=1 
                tabu_list = [i for i in tabu_list if i[4] != 0]                  
            
            # Verifico si los movimientos son tabú o no
            solution_is_tabu = False
            for item in movimientos_realizados:
            # Comparar item con los los miembros de tabu_list
                # Recorro todo tabu_list para ver si item está allí    
                for sublista_tabu in tabu_list:
                    if item[:4] == sublista_tabu[:4]:
                        solution_is_tabu=True
                        break
                # Si no son tabú agrego los movimientos a la lista tabú 
                if solution_is_tabu == False:
                    tabu_list.append(item)
                    new_solution_ready = True

            # Si al menos uno de los movimientos es tabú verifico nivel de aspiración                     
            if solution_is_tabu == True:
                print ("TENGO UNA SOLUCIÓN TABU")
                if qual_best_of_neighborhood < qual_best:
                    new_solution_ready = True
                else: # Actualizo el vecindario factible y repito
                    # Extraigo los sigmas de best_of_neighborhood
                    matriz_best_of_neighborhood=extraer_variable_de_solucion_codificada(best_of_neighborhood_cod,'sigmas')
                    
                    # Crear una nueva lista de soluciones factibles no tabu
                    nueva_lista_feasible = []
                    for solution in neighborhood_feasible:
                        matriz_soluc_feasible = extraer_variable_de_solucion_codificada(solution, 'sigmas')
                        if matriz_soluc_feasible != matriz_best_of_neighborhood:
                            nueva_lista_feasible.append(solution)
                    
                    # Reemplazar la lista original con la nueva lista
                    neighborhood_feasible = nueva_lista_feasible
        
        # Comparo la mejor solución del vecindario con la mejor solución obtenida.
        print ("Comparación de mejor solución de vecindario con mejor solución obtenida")
        if qual_best_of_neighborhood < qual_best:
            qual_best=qual_best_of_neighborhood 
            best_neighbor = copy.deepcopy(best_of_neighborhood)
            calcular_kpi_local_search(best_neighbor)# Calculo KPIs
            print (f'Mejor solución obtenida hasta ahora: {qual_best_of_neighborhood}')
            current_neighbor = best_of_neighborhood
            
            # Hubo mejora, el contador de mejoras se hace cero
            iterations_without_improvement = 0
            
            # Agrego una nueva línea a la lista de adyacencia del landscape
            agregar_solucion_landscape (landscape,best_neighbor,qual_best)
            
        else: #No hubo mejora
            current_neighbor = best_of_neighborhood
            iterations_without_improvement += 1
        
        # Actualizo el criterio de parada
        # Criterio de parada es W rule
        if iterations_without_improvement > max_iterations_without_improve:
            stopping_condition_W_rule = True
        
        # Criterio de parada es N rule
        if contador == iterations_to_do:
            stopping_condition_N_rule = True
            
        contador +=1
    
    print ("Resultado final")
    
    print (f"Operador: {operador}")
    print (f"Mejor solución alcanzada: ")
    print (best_neighbor.df_sigma.to_string())
    print (f"Valor función objetivo: {best_neighbor.network_copy.file['df_medidas']['rho_max'][0] }")
    print (f"Vecindario final número: {contador-1}")   
    
    best_neighbor.landscape=landscape
    current_solution = copy.deepcopy(best_neighbor)
    
    return current_solution

#%% Manipulación de vecindario

def extraer_variable_de_solucion_codificada(solucion_cod,contenido_variable):
    # Extraigo los sigmas de best_of_neighborhood
    matriz_sigmas=[]
    for key,value in solucion_cod.items():
        if 'sigmas' in value:
            matriz_sigmas.append(value[contenido_variable])
    return matriz_sigmas


def movimiento_realizado (best_of_neighborhood_cod, neighbor_codificado, tennure):
    # Movimiento_tabu=[servicioK,nodoJ,sigma_nuevo,sigma_viejo,tennure]
    for index,servicio in best_of_neighborhood_cod.items():
        if 'sigmas' in servicio:
            lista1 = best_of_neighborhood_cod[index]['sigmas']
            lista2 = neighbor_codificado[index]['sigmas']
            # Comparación directa de las listas
            if lista1 == lista2:
                #print(f"No hay diferencias en k {index}.")
                #movimientos_tabu=[]
                pass
            else:
                #print(f"Las listas son diferentes en k {index}.")
            
                # Identificar y mostrar las diferencias
                movimientos_tabu= [[index, i+1, lista1[i], lista2[i],tennure] for i in range(len(lista1)) if lista1[i] != lista2[i]]
                #print("Elementos diferentes (índice, valor en lista1, valor en lista2):")    
    
    return movimientos_tabu

def neighborhood_exhaustive_codificado (neighbor_codificado,operador): #
    neighborhood=[] # Vecindario de _solucion
    
    # Incluyo soluciones con los peores rho en cada vector de _k
    # Cálculo de cuartiles
    claves = []
    rho_max_contenido = []
    
    # Iterar sobre el diccionario y extraer las claves y los contenidos de 'rho_max'
    for clave, contenido in neighbor_codificado.items():
        if 'sigmas' in contenido:
            claves.append(clave)
            rho_max_contenido.append(contenido['rho_max'][0])
    
    # Crear un DataFrame de pandas
    grouped_max = pd.DataFrame({'servicio_K': claves, 'rho': rho_max_contenido})
    
    # Verificar el número de cuartiles
    q = 4  # Intentar dividir en 4 cuartiles
    
    # Verificar el número de etiquetas
    labels = ['Q1', 'Q2', 'Q3', 'Q4']  # 4 etiquetas para 4 cuartiles
    
    # Si hay menos valores únicos, ajustar los cuartiles
    while True: 
        try:
            grouped_max['cuartil_b'] = pd.qcut(grouped_max['rho'], q=q, 
                                               labels=labels, duplicates='drop')
            break
        except ValueError as e:
            print("Error:", e)
            # Ajustar el número de cuartiles y etiquetas si hay error
            labels.pop(0)
            q-=1
        
    # Para cada servicio k procedo a aplicar operador
    for key in neighbor_codificado:
        
        # Si _k no está en Q4, significa que no está congestionado y por lo tanto no lo agrego al vecindario
        if (key in grouped_max[grouped_max['cuartil_b'] == 'Q4']['servicio_K'].values): #or\
           #(_k in grouped_max[grouped_max['cuartil_b'] == 'Q3']['servicio_K'].values):
    
            # Aplico el operador de perturbación para generar nuevos vecindarios
            #Posibles operadores:
            #--------------------
            #neighborhood_k = incremento1_decremento1_exhaust(vector_original_sigmas) 
            #neighborhood_k = incremento1_exhaust (vector_original_sigmas)
            #neighborhood_k = incremento1_all (vector_original_sigmas)
            #neighborhood_k = incremento2_decremento1_exhaust(vector_original_sigmas) 
            #neighborhood_k = incremento2_decremento2_exhaust(vector_original_sigmas) 
            #neighborhood_k = incremento3_decremento3_exhaust(vector_original_sigmas) 
            #neighborhood_k = chain_reaction_exhaust_plus_minus(vector_original_sigmas)
            #neighborhood_k = chain_reaction_exhaust_minus_plus(vector_original_sigmas)
            
            vector_original_sigmas = neighbor_codificado[key]['sigmas']
            #print (f'Servicio del vector sigmas: {key}')
            #print (f'Vector sigmas original: {vector_original_sigmas}')
            
            # Si se ejecuta desde __name__ == "__main__" aplico un operador específico
            if __name__ == "__main__":
                neighborhood_sigmas_k = incremento1_decremento1_exhaust(vector_original_sigmas)
            else: # Aplico operador seleccionado por el usuario
                neighborhood_sigmas_k = globals()[operador](vector_original_sigmas)
        
            # Agrego solución permutada al vecindario
            for permutacion in neighborhood_sigmas_k:
                neighbor_modificado_cod = copy.deepcopy(neighbor_codificado)
                neighbor_modificado_cod[key]['sigmas']=permutacion
                
                #Devuelve un listado de soluciones (listas de nodes_K) para cada _k        
                neighborhood.append(neighbor_modificado_cod)
        
    
    return neighborhood

def agregar_solucion_landscape (landscape,best_neighbor,qual_best):
    lista = [_j.capac_instal_sigma for _i, _j in best_neighbor.network_repr.nodes_supply.items() if _j.service != 'k00']
    lista_sigma_y_fo=[lista,qual_best] # Vector de sigmas y su función objetivo 
    landscape.append([lista_sigma_y_fo]) #Guardo primer elemento del landscape
    
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

    # Agrupa por 'servicio_K' y luego obtiene el valor máximo de 'rho' en cada k
    grouped_max = df_capac1.set_index('servicio_K').groupby('servicio_K')['rho'].max()
    grouped_max=grouped_max.reset_index()
       
    # Verificar el número de cuartiles
    q = 4  # Intentar dividir en 4 cuartiles
    
    # Verificar el número de etiquetas
    labels = ['Q1', 'Q2', 'Q3', 'Q4']  # 4 etiquetas para 4 cuartiles
    
    # Si hay menos valores únicos, ajustar los cuartiles
    while True: 
        try:
            grouped_max['cuartil_b'] = pd.qcut(grouped_max['rho'], q=q, 
                                               labels=labels, duplicates='drop')
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
        
        # Si _k no está en Q4, significa que no está congestionado y por lo tanto no lo agrego al vecindario
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
            
            # Codifico el contenido de nodes_k
            # Codificación. Paso de los objetos nodes a un vector con sigmas. 
            vector_original_sigmas = [nodo.capac_instal_sigma for nodo in nodes_k]
            print (f'Servicio del vector sigmas: {nodes_k[0].service}')
            #print (f'Vector sigmas original: {vector_original_sigmas}')
            
            # Si se ejecuta desde __name__ == "__main__"
            if __name__ == "__main__":
                neighborhood_sigmas_k = incremento1_decremento1_exhaust(vector_original_sigmas,
                                                                  _k,_solucion)
                _solucion.local_search_operator="incremento1_decremento1_exhaust (nodes_k,_k,_solucion)"

            else:
                neighborhood_sigmas_k = eval(_solucion.local_search_operator)
                
            # Decodifico copia_vector_original_sigmas en nodes
            lista_nodes_perturbados=[]
            for vector in neighborhood_sigmas_k:                    

                copia_nodes=copy.deepcopy(nodes_k)
                
                for index, value in enumerate(copia_nodes):
                    value.capac_instal_sigma = vector[index]
                
                lista_nodes_perturbados.append(copia_nodes)    
        
    
            #Devuelve un listado de soluciones (listas de nodes_K) para cada _k        
            neighborhood.append(lista_nodes_perturbados)
        
    
    return neighborhood


def find_best_of_neighborhood(neighborhood_feasible,neighbor,
                              landscape,current_solution):
    # Inicio valor extremo de la mejor solución del vecindario    
    best_of_neighborhood=neighbor    
    qual_best_of_neighborhood=10.0
    
    # Para los vecinos factibles, construyo un modelo de optimización
    # Que genere las variables adicionales tao y phi (flujos). Sigma es un parámetro y no una variable
    
    #print ("Optimización para hallar flujos")
    # Actualizo los valores sigma de cada solución factible en nodes supply.capac_instal_sigma
    # DECODIFICACIÓN. Llevo desde diccionario codificado a objeto neighbor       
    for index_vecino, vecino_codificado in enumerate(neighborhood_feasible): #Para cada solucion del vecindario factible
        
        # Hago optimización de vecino codificado para tener flujos
        neighbor_copy=optimizacion(vecino_codificado,neighbor,current_solution)
    
        # Guardo neighbor_copy como vecino de best_neighbor en la lista de adyacencia.
        lista = [_j.capac_instal_sigma for _i, _j in neighbor_copy.network_repr.nodes_supply.items() if _j.service != 'k00']
        calcular_kpi_local_search(neighbor_copy) # Actualizo KPI
        func_obj = neighbor_copy.network_copy.file['df_capac']['rho'].max() #Obtengo el rho max
        landscape[-1].append([lista,func_obj]) ##Guardo vecinos de best_neighbor
    
        # Busco la mejor solución en neighborhood_feasible
        if neighbor_copy.state=="Optimizado" and neighbor_copy.value_optimal_solution['Func_obj'] < qual_best_of_neighborhood:
            qual_best_of_neighborhood=neighbor_copy.value_optimal_solution['Func_obj']
            best_of_neighborhood=neighbor_copy
        
        # Retiro vecino_codificado de neighborhood feasible
        elemento = neighborhood_feasible.pop(index_vecino)
            
        # Insertar el vecino_codificado que se retiró, en la posición 0
        neighborhood_feasible.insert(0, elemento)
            
    return best_of_neighborhood , qual_best_of_neighborhood, landscape, neighborhood_feasible
            
def tamizaje_soluciones(best_neighbor,neighborhood):
    # Las soluciones no pueden tener sigmas negativos o que superen s_jk o cuya suma sea mayor a sigma_max       
    # CODIFICACIÓN DE SOLUCIÓN. Creo una solución codificada con los valores máximos de sigma, es decir, los s_jk
    neighbor_codificado_with_max_s_jk=codificar_solucion(best_neighbor,'s_jk')
    
    neighborhood_feasible=[]
    
    # Comparo cada vector 'sigmas' del vecino codificado con el vector 'sigma' de best_neighbor_sjk
    # Si se viola la restricción, se elimina el vecino del vecindario
    for vecino in neighborhood: # Para cada vecindario de k
        vecino_factible=True
        for index, values in vecino.items():
            if 'sigmas' in values:
                vector_sigmas_vecino=values['sigmas']
                vector_sigmas_s_jk = neighbor_codificado_with_max_s_jk[index]['sigmas']
                if (all(x<=y for x,y in zip (vector_sigmas_vecino,vector_sigmas_s_jk)) and
                   (all(x>=0 for x in vector_sigmas_vecino))):
                    pass
                else:
                    vecino_factible=False
                    
        if vecino_factible == True:
            neighborhood_feasible.append(vecino)
    
    return neighborhood_feasible


#%% Operadores para codificación y decodificación




def codificar_solucion (neighbor,contenido_variable):
    # Convierte un objeto solucion en una solución codificada
    # Es un diccionario con los sigmas de cada k
    solucion_codificada={}
    _lista_k=data_functions.indices('k',neighbor.network_copy.K) 
    for key in _lista_k:
        if contenido_variable == "sigma":
            lista_sigmas=[_j.capac_instal_sigma for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
            maximo_par = max([[_j.rho,_j.place] for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key], 
                             key=lambda x: x[0]) 
            solucion_codificada[key]={'sigmas':lista_sigmas,
                                      'rho_max':maximo_par}
        elif contenido_variable == "s_jk":
            lista_sigmas=[_j.capac_instal_max for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
            maximo_par = max([[_j.rho,_j.place] for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key], 
                             key=lambda x: x[0]) 
            solucion_codificada[key]={'sigmas':lista_sigmas,
                                      'rho_max':maximo_par}
    # Encontrar la clave con el valor de 'rho_max' más alto
    clave_max_rho = max(solucion_codificada, key=lambda x: solucion_codificada[x]['rho_max'][0])
    
    # Crear una nueva clave 'rho_max' en el diccionario
    solucion_codificada['k_rho_max'] = clave_max_rho  #solucion_codificada['rho_max'] = [elemento if not isinstance(elemento, list) else subelemento for elemento in solucion_codificada['rho_max'] for subelemento in (elemento if isinstance(elemento, list) else [elemento])]

    return solucion_codificada   

def decodificar_solucion (vecino_codificado,neighbor):
    # Convierto una solución codificada (diccionario) en un objeto solution
    neighbor_copy=copy.deepcopy(neighbor) #neighbor es un objeto solution
    lista_nodos_j = data_functions.indices('j',neighbor.network_copy.J) #[j01, j02, ...]
                
    for key_vecino_cod , value_vecino_cod in vecino_codificado.items(): #k01:dict, k02:dict
        if 'sigmas' in value_vecino_cod:
            for index , jk in enumerate(lista_nodos_j): # (0,j01) (1, j02)...
                indice_nuevo_sigma=jk+key_vecino_cod #j01k01 j02k01 
                nuevo_sigma=value_vecino_cod['sigmas'][index]  #80
                neighbor_copy.network_repr.nodes_supply[indice_nuevo_sigma].capac_instal_sigma=nuevo_sigma
    return neighbor_copy

#%% Operadores para generar vecindarios


def incremento1_decremento1_exhaust (vector_original_sigmas):
    # # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
    
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
                #print (f'Sigma {i} era {vector_original_sigmas[i]} y sigma {j} era {vector_original_sigmas[j]}, Nuevo vector es {copia_vector_original_sigmas}')
                
                lista_sigmas_perturbados.append(copia_vector_original_sigmas)
    return lista_sigmas_perturbados 
    #return lista_nodes_perturbados

def incremento1_exhaust (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]

    
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
            
            lista_sigmas_perturbados.append(copia_vector_original_sigmas)
            
    return lista_sigmas_perturbados

def incremento1_all (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
    # Aplico operador al vector codificado
    # Sumo 1 a todos los sigma del elemento.
    # Este operador SÍ CAMBIA la cantidad total de servidores asignados.
    # Por lo tanto debo verificar que no supere el sigma_max_k. 
    # Esta verificación se hace posteriormente en el tamizaje de soluciones.
    
    copia_vector_original_sigmas=vector_original_sigmas.copy()

    copia_vector_original_sigmas = [x+1 for x in copia_vector_original_sigmas]
                
    print (f'Vector sigmas original era {vector_original_sigmas}. Nuevo vector sigmas es {copia_vector_original_sigmas}')
    
    lista_sigmas_perturbados.append(copia_vector_original_sigmas)
            
    return lista_sigmas_perturbados

def incremento2_decremento1_exhaust (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
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
                
                lista_sigmas_perturbados.append(copia_vector_original_sigmas)
                
    return lista_sigmas_perturbados

def incremento2_decremento2_exhaust (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
        
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
                
                lista_sigmas_perturbados.append(copia_vector_original_sigmas)
                
    return lista_sigmas_perturbados

def incremento3_decremento3_exhaust (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
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
                
                lista_sigmas_perturbados.append(copia_vector_original_sigmas)
                
    return lista_sigmas_perturbados

def chain_reaction_exhaust_plus_minus (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
    # Aplico operador al vector codificado
    # Creo un vectorcadena  +1 -1 +1 -1 ... del mismo tamaño de vector sigmas
    # Sumo vector sigmas a vectorcadena
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    vectorcadena = [1 if i % 2 == 0 else -1 for i in range(len(vector_original_sigmas))]

    copia_vector_original_sigmas=vector_original_sigmas.copy()
    copia_vector_original_sigmas = [x + y for x, y in zip(copia_vector_original_sigmas, vectorcadena)]
    
    print (f'Vector original era {vector_original_sigmas}. Nuevo vector es {copia_vector_original_sigmas}')
    
    lista_sigmas_perturbados.append(copia_vector_original_sigmas)
            
    return lista_sigmas_perturbados

def chain_reaction_exhaust_minus_plus (vector_original_sigmas):
    # Obtengo los nodos perturbados para el servicio _k
    lista_sigmas_perturbados=[]
    
    # Aplico operador al vector codificado
    # Creo un vectorcadena  +1 -1 +1 -1 ... del mismo tamaño de vector sigmas
    # Sumo vector sigmas a vectorcadena
    # Este operador no cambia la cantidad total de servidores asignados.
    # Por lo tanto no supera el valor de sigma_max.
    
    vectorcadena = [-1 if i % 2 == 0 else 1 for i in range(len(vector_original_sigmas))]

    copia_vector_original_sigmas=vector_original_sigmas.copy()
    copia_vector_original_sigmas = [x + y for x, y in zip(copia_vector_original_sigmas, vectorcadena)]
    
    print (f'Vector original era {vector_original_sigmas}. Nuevo vector es {copia_vector_original_sigmas}')
    
    lista_sigmas_perturbados.append(copia_vector_original_sigmas)
            
    return lista_sigmas_perturbados



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


# %% Optimización

def optimizacion(vecino_codificado,neighbor,current_solution):
    
    neighbor_copy = decodificar_solucion (vecino_codificado,neighbor)           
                
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
    
    return neighbor_copy
    
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
        I,J,K= [4,4,4]
        
        
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
                
        # Ejecuto algoritmo
        current_solution= tabu_search(current_solution,networks_dict['red_original'])
        
        