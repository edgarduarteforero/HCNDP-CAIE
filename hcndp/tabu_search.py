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
import operator
from hcndp import kpi
from hcndp import neighborhood_operator


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
    best_neighbor = initial_solution.initial_solution(current_solution,network_original)
    calcular_kpi_local_search(best_neighbor) #Mido KPI de solución inicial
    
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    best_neighbor = initial_solution.fix_initial_solution(best_neighbor)  
    
    # Defino la mejor solución encontrada
    calcular_kpi_local_search(best_neighbor)# Calculo KPIs
    if current_solution.objective == "1": # 1 Significa congestión rho
        qual_best=best_neighbor.network_copy.file['df_medidas']['rho_max'][0] 
    elif current_solution.objective == "2": # 1 Significa accesibilidad alpha
        qual_best=best_neighbor.network_copy.file['df_medidas']['alpha_min'][0] 
    elif current_solution.objective == "3": # 3 Significa continuidad delta
        qual_best=best_neighbor.network_copy.file['df_medidas']['delta_min'][0] 
        
    # Agrego solución a landscape
    agregar_solucion_landscape (landscape,best_neighbor,qual_best)
    
    # CODIFICACIÓN DE SOLUCIÓN
    # Codifico la solución inicial
    best_neighbor_codificado=codificar_solucion(best_neighbor,'sigma')
        
    print (f'Solución inicial construida')
    print (f"Vectores sigmas:")
    for i,j in best_neighbor_codificado.items():
        if 'sigmas' in j:
            print (i,j['sigmas']) 
    if current_solution.objective == "1": # 1 Significa congestión rho
         _best_rho=best_neighbor_codificado["k_rho_max"]
         print (f'Valor función objetivo inicial: {best_neighbor_codificado[_best_rho]["rho_max"][0]}')
    elif current_solution.objective == "2": # 2 Significa accesibilidad alpha
         _best_alpha=best_neighbor_codificado["k_alpha_min"]
         print (f'Valor función objetivo inicial: {best_neighbor_codificado[_best_alpha]["alpha_min"][0]}')
    elif current_solution.objective == "3": # 3 Significa continuidad delta
        _best_delta=best_neighbor_codificado["k_delta_min"]
        print (f'Valor función objetivo inicial: {best_neighbor_codificado[_best_delta]["delta_min"][0]}')


    # BUCLE PRINCIPAL
    
    # Condiciones de parada: https://www.sciencedirect.com/science/article/pii/S2214716023000180
    # N-rule: maximum number of iterations 
    stopping_condition_N_rule = False 
    iterations_to_do= 3 #Iteraciones de la búsqueda local. Criterio de parada.
    contador=1 
    
    # W-rule: maximum number of consecutive iterations without improvement in the value of the incumbent solution 
    stopping_condition_W_rule = False 
    iterations_without_improvement = 0
    max_iterations_without_improve = 3
    
    # Solución que ingresa al bucle
    neighbor = copy.deepcopy(best_neighbor)


    while stopping_condition_W_rule == False:
        
        print (f'Vecindario número = {contador}')       
        
        # Generar vecindario a partir de la mejor solución hallada
        # neighbor es un objeto solución (contiene matrices, nodos, arcos, etc)
        # neighbor_codificado es la codificación del objeto neighbor (diccionario)
        # neighborhood es el vecindario de neighbor
        
        # Defino la solución actual neighor
        neighbor_codificado = codificar_solucion(neighbor,'sigma')
               
        try: 
            operador=current_solution.local_search_operator
        except AttributeError :
            operador="incremento1_exhaust(vector_original_sigmas)"
            pass
        
        # Construyo el vecindario. Conjunto de soluciones codificadas según operador seleccionado
        neighborhood = neighborhood_exhaustive_codificado(neighbor_codificado,operador,current_solution) 
                
        # Tamizaje de soluciones
        neighborhood_feasible=tamizaje_soluciones(best_neighbor,neighborhood)
        
        # Si el vecindario factible está vacío
        if len(neighborhood_feasible) == 0:
             best_of_neighborhood = neighbor
             best_of_neighborhood_cod = neighbor_codificado
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
            solution_has_tabu = False

            for mvto in movimientos_realizados:

                # Comparar mvto con los los miembros de tabu_list
                # Recorro todo tabu_list para ver si item está allí    
                for sublista_tabu in tabu_list:
                    if mvto[:4] == sublista_tabu[:4]:
                        solution_has_tabu=True
                        break
                # Si el movto no es tabú, lo agrego a la lista tabu
                if solution_has_tabu == False:
                    tabu_list.append(mvto)
                    new_solution_ready = True

            # Si al menos uno de los movimientos es tabú verifico nivel de aspiración                     
            if solution_has_tabu == True:
                print ("TENGO UNA SOLUCIÓN TABU")
                # Seleccionar el operador basado en la variable (1 o 3 usan <, 2 usa >)
                comparacion = operator.lt if current_solution.objective in {"1"} else operator.gt                
                if comparacion (qual_best_of_neighborhood , qual_best): # Comparo las dos qual
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
        
        # Seleccionar el operador basado en la variable (1 o 3 usan <, 2 usa >)
        comparacion = operator.lt if current_solution.objective in {"1"} else operator.gt

        if comparacion (qual_best_of_neighborhood , qual_best): # Comparo las dos qual
            qual_best=qual_best_of_neighborhood 
            best_neighbor = copy.deepcopy(best_of_neighborhood)
            calcular_kpi_local_search(best_neighbor)# Calculo KPIs
            print (f'Mejor solución obtenida hasta ahora: {qual_best_of_neighborhood}')
            neighbor = best_of_neighborhood
            
            # Hubo mejora, el contador de mejoras se hace cero
            iterations_without_improvement = 0
            
            # Agrego una nueva línea a la lista de adyacencia del landscape
            agregar_solucion_landscape (landscape,best_neighbor,qual_best)
            
        else: #No hubo mejora
            neighbor = best_of_neighborhood
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
    calcular_kpi_local_search(best_neighbor) #Mido KPI de solución inicial
    print (best_neighbor.df_sigma.to_string())
    if current_solution.objective == "1": # 1 Significa congestión rho
        print (f"Valor función objetivo: {best_neighbor.value_optimal_solution['rho_max'] }")
    elif  current_solution.objective == "2": # 2 Significa accesibilidad alpha
        print (f"Valor función objetivo: {best_neighbor.value_optimal_solution['alpha_min'] }")
    elif current_solution.objective == "3": # 3 Significa continuidad delta
        print (f"Valor función objetivo: {best_neighbor.value_optimal_solution['delta_min'] }")
    
    print (f"Vecindario final número: {contador-1}")
    
    best_neighbor.landscape=landscape
    current_solution = copy.deepcopy(best_neighbor)
    
    return current_solution

#%% Manipulación de vecindarios

def add_mvto_tabu_list(tabu_list,mvto):
    # Recorro todo tabu_list para ver si item está allí    
    for sublista_tabu in tabu_list:
        if mvto[:4] == sublista_tabu[:4]:
            solution_is_tabu=True
            break
    # Si no son tabú agrego los movimientos a la lista tabú 
    if solution_is_tabu == False:
        tabu_list.append(mvto)
        #new_solution_ready = True
    return tabu_list,solution_is_tabu

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

def neighborhood_exhaustive_codificado (neighbor_codificado,operador,current_solution): #
    neighborhood=[] # Vecindario de _solucion
    
    # Incluyo soluciones con los peores rho en cada vector de _k
    # Cálculo de cuartiles
    claves = []
    rho_max_contenido = []
    alpha_min_contenido = []
    delta_min_contenido= []

    # Iterar sobre el diccionario y extraer las claves y los contenidos de 'rho_max'
    for clave, contenido in neighbor_codificado.items():
        if 'sigmas' in contenido:
            claves.append(clave)
            if current_solution.objective == "1": # 1 Significa congestión rho
                rho_max_contenido.append(contenido['rho_max'][0])
            elif current_solution.objective == "2": # 2 Significa accesibilidad alpha:
                alpha_min_contenido.append(contenido['alpha_min'][0])
            elif current_solution.objective == "3": # 3 Significa continuidad delta:
                delta_min_contenido.append(contenido['delta_min'][0])
    
    # Crear un DataFrame de pandas
    if current_solution.objective == "1": # 1 Significa congestión rho
        grouped_max = pd.DataFrame({'servicio_K': claves, 'rho': rho_max_contenido})
    elif current_solution.objective == "2": # 2 Significa accesibilidad alpha:
        grouped_max = pd.DataFrame({'servicio_K': claves, 'alpha': alpha_min_contenido})
    elif current_solution.objective == "3": # 3 Significa continuidad delta:
        grouped_max = pd.DataFrame({'servicio_K': claves, 'delta': delta_min_contenido})
    
    # Verificar el número de cuartiles
    q = 4  # Intentar dividir en 4 cuartiles
    
    # Verificar el número de etiquetas
    labels = ['Q1', 'Q2', 'Q3', 'Q4']  # 4 etiquetas para 4 cuartiles
    
    # Si hay menos valores únicos, ajustar los cuartiles
    while True: 
        if current_solution.objective in {"1"}: 
            # 1 Significa congestión rho
            try:
                grouped_max['cuartil_b'] = pd.qcut(grouped_max['rho'], q=q, 
                                                   labels=labels, duplicates='drop')
                break
            except ValueError as e:
                print("Error:", e)
                # Ajustar el número de cuartiles y etiquetas si hay error
                labels.pop(0)
                q-=1
        
        elif current_solution.objective in {"2"}: 
            # 2 Significa accesibilidad alpha 
            try:
                grouped_max['cuartil_b'] = pd.qcut(grouped_max['alpha'], q=q, 
                                                   labels=labels, duplicates='drop')
                break
            except ValueError as e:
                print("Error:", e)
                # Ajustar el número de cuartiles y etiquetas si hay error
                labels.pop(-1)
                q-=1
        
        elif current_solution.objective in {"3"}: 
            # 3 significa continuidad delta
            try:
                grouped_max['cuartil_b'] = pd.qcut(grouped_max['delta'], q=q, 
                                                   labels=labels, duplicates='drop')
                break
            except ValueError as e:
                print("Error:", e)
                # Ajustar el número de cuartiles y etiquetas si hay error
                labels.pop(-1)
                q-=1
        
    # Para cada servicio k procedo a aplicar operador
    for key in neighbor_codificado:
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
        
        if current_solution.objective in {"1"} : 
            # 1 Significa congestión rho
            # Si _k no está en Q4, significa que no está congestionado y por lo tanto no lo agrego al vecindario
            if (key in grouped_max[grouped_max['cuartil_b'] == 'Q4']['servicio_K'].values): #or\
               #(_k in grouped_max[grouped_max['cuartil_b'] == 'Q3']['servicio_K'].values):
                    
                vector_original_sigmas = neighbor_codificado[key]['sigmas']
                #print (f'Servicio del vector sigmas: {key}')
                #print (f'Vector sigmas original: {vector_original_sigmas}')
                
                # Si se ejecuta desde __name__ == "__main__" aplico un operador específico
                if __name__ == "__main__":
                    neighborhood_sigmas_k = neighborhood_operator.incremento1_decremento1_exhaust(vector_original_sigmas)
                else: # Aplico operador seleccionado por el usuario
                    # Ejecuta la función con el argumento necesario
                    neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)                
            
                # Agrego solución permutada al vecindario
                for permutacion in neighborhood_sigmas_k:
                    neighbor_modificado_cod = copy.deepcopy(neighbor_codificado)
                    neighbor_modificado_cod[key]['sigmas']=permutacion
                    
                    #Devuelve un listado de soluciones (listas de nodes_K) para cada _k        
                    neighborhood.append(neighbor_modificado_cod)

                # Si logro permutar una solución, me salgo del bucle
                break

        elif current_solution.objective in {"2","3"}: 
            # 2 Significa accesibilidad alpha , 3 significa continuidad delta
            # Si _k no está en Q1, significa que no está congestionado y por lo tanto no lo agrego al vecindario
            if (key in grouped_max[grouped_max['cuartil_b'] == 'Q1']['servicio_K'].values): #or\
               #(_k in grouped_max[grouped_max['cuartil_b'] == 'Q2']['servicio_K'].values):
                    
                vector_original_sigmas = neighbor_codificado[key]['sigmas']
                #print (f'Servicio del vector sigmas: {key}')
                #print (f'Vector sigmas original: {vector_original_sigmas}')
                
                # Si se ejecuta desde __name__ == "__main__" aplico un operador específico
                if __name__ == "__main__":
                    neighborhood_sigmas_k = neighborhood_operator.incremento1_decremento1_exhaust(vector_original_sigmas)
                else: # Aplico operador seleccionado por el usuario
                    # Ejecuta la función con el argumento necesario
                    neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)                
            
                # Agrego solución permutada al vecindario
                for permutacion in neighborhood_sigmas_k:
                    neighbor_modificado_cod = copy.deepcopy(neighbor_codificado)
                    neighbor_modificado_cod[key]['sigmas']=permutacion
                    
                    #Devuelve un listado de soluciones (listas de nodes_K) para cada _k        
                    neighborhood.append(neighbor_modificado_cod)

                # Si logro permutar una solución, me salgo del bucle
                break

    return neighborhood

def agregar_solucion_landscape (landscape,best_neighbor,qual_best):
    lista = [_j.capac_instal_sigma for _i, _j in best_neighbor.network_repr.nodes_supply.items() if _j.service != 'k00']
    lista_sigma_y_fo=[lista,qual_best] # Vector de sigmas y su función objetivo 
    landscape.append([lista_sigma_y_fo]) #Guardo primer elemento del landscape


def find_best_of_neighborhood(neighborhood_feasible,neighbor,
                              landscape,current_solution):
    # Inicio valor extremo de la mejor solución del vecindario    
    best_of_neighborhood=neighbor
    if current_solution.objective in {"1"} : 
        # 1 Significa congestión rho, 
        qual_best_of_neighborhood=1000.0
    elif current_solution.objective in {"2","3"}: 
        # 2 Significa accesibilidad alpha 3 significa continuidad delta
        qual_best_of_neighborhood=0.0
    
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
        if current_solution.objective == "1": # 1 Significa congestión rho
            func_obj = neighbor_copy.network_copy.file['df_capac']['rho'].max() #Obtengo el rho max
        elif current_solution.objective == "2": # 2 Significa accesibilidad alpha
            func_obj = neighbor_copy.network_copy.file['df_accesibilidad']['R'].min() #Obtengo el alpha min
        elif current_solution.objective == "3": # 3 Significa continuidad delta
            func_obj = neighbor_copy.network_copy.file['df_continuidad']['delta_i'].min() #Obtengo el delta min
        
        landscape[-1].append([lista,func_obj]) ##Guardo vecinos de best_neighbor
        
        # Busco la mejor solución en neighborhood_feasible
        # Seleccionar el operador basado en la variable
        comparacion = operator.lt if current_solution.objective in {"1"} else operator.gt
        # Si uso rho, comparacion es <, de lo contrario es > (Para accesibilidad)    
        #if neighbor_copy.state=="Optimizado" and neighbor_copy.value_optimal_solution['Func_obj'] < qual_best_of_neighborhood:
        if neighbor_copy.state=="Optimizado" and comparacion (neighbor_copy.value_optimal_solution['Func_obj'] , qual_best_of_neighborhood): # Comparo las dos qual
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
    current_solution=neighbor


    if current_solution.objective == "1": # 1 Significa congestión rho
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

    if current_solution.objective == "2": # 2 Significa accesibilidad lambda
        for key in _lista_k:
            if contenido_variable == "sigma":
                lista_sigmas=[_j.capac_instal_sigma for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
                
                minimo_par = min([[_node_i.access_ik,_node_i.place] for _index, 
                                  _node_i in neighbor.network_repr.nodes_supply.items() if _node_i.service == key], 
                                 key=lambda x: x[0])
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'alpha_min':minimo_par}
            
            elif contenido_variable == "s_jk":
                lista_sigmas=[_j.capac_instal_max for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
                
                minimo_par = min([[_node_i.access_ik,_node_i.place] for _index, 
                                  _node_i in neighbor.network_repr.nodes_supply.items() if _node_i.service == key], 
                                 key=lambda x: x[0])
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'alpha_min':minimo_par}
        # Encontrar la clave con el valor de 'alpha_min' más bajo
        clave_min_alpha = min(solucion_codificada, key=lambda x: solucion_codificada[x]['alpha_min'][0])
        
        # Crear una nueva clave 'alpha_min' en el diccionario
        solucion_codificada['k_alpha_min'] = clave_min_alpha  #solucion_codificada['rho_max'] = [elemento if not isinstance(elemento, list) else subelemento for elemento in solucion_codificada['rho_max'] for subelemento in (elemento if isinstance(elemento, list) else [elemento])]
    
    if current_solution.objective == "3": # 3 Significa continuidad delta
        for key in _lista_k:
            if contenido_variable == "sigma":
                lista_sigmas=[_j.capac_instal_sigma for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
                
                minimo_par = min([[_node_i.continuidad,_node_i.node_id] for _index, 
                                  _node_i in neighbor.network_repr.nodes_demand.items() ], 
                                 key=lambda x: x[0])
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'delta_min':minimo_par}
            
            elif contenido_variable == "s_jk":
                lista_sigmas=[_j.capac_instal_max for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key]
                
                minimo_par = min([[_node_i.continuidad,_node_i.node_id] for _index, 
                                  _node_i in neighbor.network_repr.nodes_demand.items() ], 
                                 key=lambda x: x[0])
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'delta_min':minimo_par}
        
        # Encontrar la clave con el valor de 'delta_min' más bajo
        clave_min_delta = min(solucion_codificada, key=lambda x: solucion_codificada[x]['delta_min'][0])
        
        # Crear una nueva clave 'rho_max' en el diccionario
        solucion_codificada['k_delta_min'] = clave_min_delta #solucion_codificada['rho_max'] = [elemento if not isinstance(elemento, list) else subelemento for elemento in solucion_codificada['rho_max'] for subelemento in (elemento if isinstance(elemento, list) else [elemento])]



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

#%% Cálculo de kpi



def calcular_kpi_local_search(current_solution):
    current_solution

    # Creo carpetas para current solution
    current_solution.create_folders_problem()
    # Si hay función objetivo (resultado de optimización)
    # Actualizo las matrices de solution.network_copy
    current_solution.network_copy.tecnica=current_solution.tecnica
    #current_solution.network_copy.problem=current_solution #Creo una referencia al objeto padre Problem
    
    current_solution.network_copy.merge_niveles_capac(_post_optima=True,current_solution=current_solution)
    current_solution.network_copy.create_df_asignacion(_post_optima=True,current_solution=current_solution)
    current_solution.network_copy.create_df_probs_kk()
    current_solution.network_copy.create_df_arcos(_post_optima=True,current_solution=current_solution)
                     
                     
    kpi.calculate_kpi(current_solution,_post_optima=True)
    #print (f"Se calcularon los KPI para la solución {current_solution.description_objective}.")

    # Calculo los rho para cada nodo jk y lo almaceno en nodes_supply
    for _i,_j in current_solution.network_repr.nodes_supply.items():
        if _j.service != 'k00':
            if _j.matriz_λ['λ_ijk'].sum() == 0 or _j.capac_instal_sigma == 0:
                _j.rho=0
            else: 
                _j.rho = _j.matriz_λ['λ_ijk'].sum()/(_j.capac_instal_sigma*_j.rate)

   
    # Calculo los alpha para cada nodo ik y lo almaceno en nodes_demand
    for _i,_j in current_solution.network_repr.nodes_demand.items():
        lista_access=current_solution.network_copy.file['df_accesibilidad'][current_solution.network_copy.file['df_accesibilidad']['nombre_I']==_i]
        lista_access=lista_access[['servicio_K','R']]
        _j.lista_accesibilidad= lista_access.set_index('servicio_K')['R'].to_dict()
   
           
    # Cargo los alpha para cada nodo ik y lo almaceno en nodes_supply
    for i,j in current_solution.network_repr.nodes_demand.items():
        for k,acc in j.lista_accesibilidad.items():
            current_solution.network_repr.nodes_supply['j'+i[-2:]+k].access_ik=acc
            
    # Calculo los delta para cada nodo i y lo almaceno en nodes_demand
    for _i,_j in current_solution.network_repr.nodes_demand.items():
        lista_contin=current_solution.network_copy.file['df_continuidad'][current_solution.network_copy.file['df_continuidad']['nombre_I']==_i]
        lista_contin=lista_contin[['nombre_I','delta_i']]
        _j.continuidad= lista_contin.iloc[0]['delta_i']
        
    # Cargo los delta para cada nodo i y lo almaceno en nodes_demand
    # for i,j in current_solution.network_repr.nodes_demand.items():
    #     for _i,cont in j.lista_continuidad.items():
    #         current_solution.network_repr.nodes_demand['i'+i[-2:]+k].cont_i=cont

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
        #_objective_and_description =['1', 'Minimizar congestión máxima (rho)']
        #_objective_and_description =['2', 'Maximizar accesibilidad mínima (alpha)']
        _objective_and_description =['3', 'Maximizar continuidad mínima (delta)']
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
        
        