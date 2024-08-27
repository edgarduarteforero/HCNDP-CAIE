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
from hcndp import neighborhood_operator
import operator



def gvns_search(current_solution,network_original):
   
    
    # Basado en Gendrau y Potvin (2019). Capítulo 3
    # Definiciones:
    # current_solution: Objeto contenedor que agrupa: objetivo, red, datos, resultados, técnica, etc.
    # network_original: Objeto con datos originales de la red. No se modifica durante el código. Permance como referencia.
       
    # operadores VNS
    operadores = {
    #2:'incremento1_decremento1_exhaust', 
    1:'incremento1_exhaust',
    2:'incremento1_all',
    #2:'incremento2_decremento1_exhaust', 
    #2:'incremento2_decremento2_exhaust', 
    #3:'incremento3_decremento3_exhaust', 
    #2:'chain_reaction_exhaust_plus_minus',
    #8:'chain_reaction_exhaust_minus_plus'
    }
    
    operadoresVND = {
    #2:'incremento1_all',
    3:'incremento1_decremento1_exhaust', 
    #1:'incremento1_exhaust',
    #3:'incremento2_decremento1_exhaust', 
    1:'incremento2_decremento2_exhaust', 
    #6:'incremento3_decremento3_exhaust', 
    2:'incremento1_decremento1_parejas',
    #8:'chain_reaction_exhaust_minus_plus'
    }
    
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
    max_iterations_without_improve = 5

    # K-rule: maximum number of neighborhood operators
    stopping_condition_K_rule = False
    k_max=len(operadores)
    
    # Solución que ingresa al bucle
    neighbor = copy.deepcopy(best_neighbor)
    
    # Defino el primer operador
    operador=operadores[1]

    while stopping_condition_W_rule == False:
        
        
        # Inicio el orden de los operadores        
        num_operador=1
        
        # Examino todos los operadores
        while num_operador <= k_max:
            
            operador = operadores[num_operador]
            print (f'Operador GVNS = {operador}')       
            print (f'Vecindario GVNS número = {contador}')       
        
            # Generar vecindario a partir de la solución hallada
            # neighbor es un objeto solución (contiene matrices, nodos, arcos, etc)
            # neighbor_codificado es la codificación del objeto neighbor (diccionario)
            # neighborhood es el vecindario de neighbor
            
            #Construyo lista exhaustiva del vecindario
            neighbor_codificado = codificar_solucion(neighbor,'sigma')
            
            try: 
                operador=current_solution.local_search_operator
            except:
                pass
            
            # Construyo el vecindario. Conjunto de soluciones codificadas según operador seleccionado
            neighborhood = neighborhood_exhaustive_codificado(neighbor_codificado,operador,current_solution) 
                    
            # Tamizaje de soluciones
            neighborhood_feasible=tamizaje_soluciones(best_neighbor,neighborhood)
            
            # Calculo la solución crítica. sigma jk que genera el peor valor de la función objetivo
            critical_node_in_solution1 = find_critical_node(neighbor_codificado,neighbor,0)
            critical_node_in_solution2 = find_critical_node(neighbor_codificado,neighbor,1)
            critical_node_in_solution3 = find_critical_node(neighbor_codificado,neighbor,2)
            list_critical_nodes=[critical_node_in_solution1 ,critical_node_in_solution2 ,critical_node_in_solution3 ]
            
            # Depuracón de soluciones 
            # Se dejan solamente los vecinos que hagan cambios en la solución crítica
            neighborhood_feasible=pruning_neighborhood_feasible(neighborhood_feasible,list_critical_nodes)
            
            # Si el vecindario factible está vacío
            if len(neighborhood_feasible) == 0:
                 best_of_neighborhood = neighbor
                 best_of_neighborhood_cod = neighbor_codificado
                 best_of_neighborhood = optimizacion(best_of_neighborhood_cod ,best_of_neighborhood,current_solution)
                 qual_best_of_neighborhood=best_of_neighborhood.value_optimal_solution['Func_obj'] 
            else:
                # Aplico función shake para hallar una solución en el vecindario
                best_of_neighborhood,best_of_neighborhood_cod,qual_best_of_neighborhood =\
                    shake(neighborhood_feasible , neighbor, current_solution)
            
            
            # Aplico VND
            print (f"Inicio VND")
            best_of_neighborhood,qual_best_of_neighborhood =\
            VND (best_of_neighborhood,best_of_neighborhood_cod,
                     qual_best_of_neighborhood,best_neighbor, qual_best,
                     landscape,operadoresVND,current_solution)
            
            # Aplico neighborhood change
            neighbor, operador, iterations_without_improvement,landscape,\
            qual_best, best_neighbor, num_operador = \
            neighborhood_change(best_neighbor, qual_best , 
                                    best_of_neighborhood , qual_best_of_neighborhood, 
                                    landscape , operador, operadores,num_operador,
                                    iterations_without_improvement)
            
            
            print (f"Fin Operador GVNS: {operador}")
            
        # Actualizo el criterio de parada
        # Criterio de parada es W rule
        if iterations_without_improvement > max_iterations_without_improve:
            stopping_condition_W_rule = True
        
        # Criterio de parada es N rule
        if contador == iterations_to_do:
            stopping_condition_N_rule = True
            
        # Criterio de parada es K rule
        if num_operador == k_max:
            stopping_condition_K_rule = True
        
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
        try:     
            print (f"Valor función objetivo: {best_neighbor.value_optimal_solution['delta_min'] }")
        except:
            print ("No encontré mejora sobre la solución inicial")
        
    print (f"Vecindario final número: {contador-1}")   
    
    best_neighbor.landscape=landscape
    current_solution = copy.deepcopy(best_neighbor)
    
    return current_solution

#%% Funciones de VNS
def VND (best_of_neighborhood, best_of_neighborhood_cod, qual_best_of_neighborhood, 
         best_neighbor, qual_best,
         landscape,operadores,current_solution):
    # best_of_neighborhood: Solución generada por el shake

    
    num_operador_VND=1
    
    # Defino el primer operador
    operador=operadores[1]
    k_max_VND=len(operadores)

    
    # Examino todos los oeradores
    while num_operador_VND <= k_max_VND:                
        operador = operadores[num_operador_VND]
        print (f'  Operador VND  = {operador}')       
        print (f'  Vecindario VND  = {num_operador_VND}')       
    
        # Generar vecindario a partir de la solución hallada
        # neighbor es un objeto solución (contiene matrices, nodos, arcos, etc)
        # neighbor_codificado es la codificación del objeto neighbor (diccionario)
        # neighborhood es el vecindario de neighbor
        
        #Construyo lista exhaustiva del vecindario
        neighbor = copy.deepcopy(best_of_neighborhood) # objeto solución
        #neighbor_codificado = copy.deepcopy(best_neighbor_codificado)
        neighbor_codificado = codificar_solucion(neighbor,'sigma')
        
        try: 
            operador=current_solution.local_search_operator
        except:
            pass
        
        # Construyo el vecindario. Conjunto de soluciones codificadas según operador seleccionado
        neighborhood = neighborhood_exhaustive_codificado(neighbor_codificado,operador,current_solution) 
                
        # Tamizaje de soluciones
        neighborhood_feasible=tamizaje_soluciones(best_neighbor,neighborhood)
        
        # Calculo la solución crítica. sigma jk que genera el peor valor de la función objetivo
        critical_node_in_solution1 = find_critical_node(neighbor_codificado,neighbor,0)
        critical_node_in_solution2 = find_critical_node(neighbor_codificado,neighbor,1)
        critical_node_in_solution3 = find_critical_node(neighbor_codificado,neighbor,2)
        list_critical_nodes=[critical_node_in_solution1 ,critical_node_in_solution2 ,critical_node_in_solution3 ]
        
        # Depuracón de soluciones 
        # Se dejan solamente los vecinos que hagan cambios en la solución crítica
        neighborhood_feasible=pruning_neighborhood_feasible(neighborhood_feasible,list_critical_nodes)
        
        
        # Si el vecindario factible está vacío
        if len(neighborhood_feasible) == 0:
             best_of_neighborhood = neighbor
             best_of_neighborhood_cod = codificar_solucion(best_of_neighborhood,'sigma')
             best_of_neighborhood = optimizacion(best_of_neighborhood_cod ,best_of_neighborhood,current_solution)
             qual_best_of_neighborhood=best_of_neighborhood.value_optimal_solution['Func_obj'] 
        
        # Encuentro mejor solución del vecindario
        else: 
            best_of_neighborhood , qual_best_of_neighborhood , landscape =\
            find_best_of_neighborhood (neighborhood_feasible,
                                        neighbor,
                                        landscape,current_solution)
        print (f'  Mejor solución del vecindario VND {num_operador_VND}: {qual_best_of_neighborhood}')
            

        # Comparo la mejor solución del vecindario con la mejor solución obtenida.
        iterations_without_improvement_VND=0
        
        neighbor, operador, iterations_without_improvement,landscape,\
        qual_best, best_neighbor, num_operador_VND = \
        neighborhood_change(best_neighbor, qual_best , 
                                best_of_neighborhood , qual_best_of_neighborhood, 
                                landscape , operador, operadores,num_operador_VND,
                                iterations_without_improvement_VND)
                
        print (f"  Fin operador VND: {operador}")
        
    return best_neighbor,qual_best


def shake(neighborhood_feasible, neighbor,current_solution):
    
    valor_aleatorio = random.choice(neighborhood_feasible)
    
    best_of_neighborhood_cod = valor_aleatorio

    best_of_neighborhood = optimizacion(best_of_neighborhood_cod, neighbor , current_solution)
    calcular_kpi_local_search(best_of_neighborhood)# Calculo KPIs
    qual_best_of_neighborhood=best_of_neighborhood.value_optimal_solution['Func_obj'] 
    best_of_neighborhood_cod= codificar_solucion(best_of_neighborhood,'sigma')
    print (f'Solución del vecindario obtenida por shake: {qual_best_of_neighborhood}')
    
    return best_of_neighborhood,best_of_neighborhood_cod,qual_best_of_neighborhood



def neighborhood_change(best_neighbor, qual_best , 
                        best_of_neighborhood , qual_best_of_neighborhood, 
                        landscape , operador, operadores,num_operador,
                        iterations_without_improvement):
   
    # Comparo la mejor solución del vecindario con la mejor solución obtenida.
    #print ("Comparación de mejor solución de vecindario con mejor solución obtenida")
    
    # Seleccionar el operador basado en la variable (1 o 3 usan <, 2 usa >)
    comparacion = operator.lt if best_neighbor.objective in {"1"} else operator.gt
    

    #print ("Comparación de mejor solución de vecindario con mejor solución obtenida")
    if comparacion (qual_best_of_neighborhood , qual_best): # Comparo las dos qual
        qual_best=qual_best_of_neighborhood 
        best_neighbor = copy.deepcopy(best_of_neighborhood)
        calcular_kpi_local_search(best_neighbor)# Calculo KPIs
        print (f'Mejor solución obtenida hasta ahora: {qual_best_of_neighborhood}')
        neighbor = best_of_neighborhood
        
        # Actualizo el operador de vecindario
        num_operador = 1
        operador = operadores[num_operador]
        
        # Hubo mejora, el contador de mejoras se hace cero
        iterations_without_improvement = 1
        
        # Agrego una nueva línea a la lista de adyacencia del landscape
        agregar_solucion_landscape (landscape,best_neighbor,qual_best)
        
    else: #No hubo mejora
        neighbor = best_of_neighborhood    
        #neighbor = best_neighbor
        iterations_without_improvement += 1
        
        # Actualizo el operador de vecindario
        num_operador += 1
        
    
    return neighbor, operador,\
            iterations_without_improvement,\
            landscape, qual_best, best_neighbor, num_operador

#%% Manipulación de vecindario

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
                #print("Error:", e)
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
                #print("Error:", e)
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
                #print("Error:", e)
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
                    neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)    
                else: # Aplico operador seleccionado por el usuario
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
                    neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)    
                else: # Aplico operador seleccionado por el usuario
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
    for vecino_codificado in neighborhood_feasible: #Para cada solucion del vecindario factible
        
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
            
    return best_of_neighborhood , qual_best_of_neighborhood, landscape
            
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

def find_critical_node(neighbor_codificado,neighbor,position):
    # Recupera el nodo crítico de la solución actual
    # El nodo crítico tien el sigma (con su jk) que está generando las peores soluciones posibles
    if neighbor.objective == "1": 
        critical_node=neighbor_codificado['k_rho_max']
        critical_node=[neighbor_codificado[critical_node]['lista_ordenada'][position][1],critical_node]
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].rho)
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].capac_instal_sigma)
    elif neighbor.objective == "2":
        critical_node=neighbor_codificado['k_alpha_min']
        critical_node=[neighbor_codificado[critical_node]['lista_ordenada'][position][1],critical_node]
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].access_ik)
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].capac_instal_sigma)
    elif neighbor.objective == "3":
        critical_node=neighbor_codificado['k_delta_min']
        critical_node=[neighbor_codificado[critical_node]['lista_ordenada'][position][1],critical_node]
        critical_node[0] = critical_node[0].replace('i', 'j')
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].cont_i)
        critical_node.append(neighbor.network_repr.nodes_supply[critical_node[0]+critical_node[1]].capac_instal_sigma)
    return critical_node

def pruning_neighborhood_feasible(neighborhood_feasible,list_critical_nodes):
    lista_temporal=[]
    for critical_node in list_critical_nodes: #Comparo nodos críticos con los que están en el vecindario factible
        for _j in neighborhood_feasible:
            critical_k=_j[critical_node[1]]['sigmas'] #k donde está el sigma jk crítico
            position_j=int(critical_node[0][-2:])-1 # j donde está el sigma jk crítico
            critical_sigma_jk=critical_k[position_j] # sigma jk 
            #print (position_j,critical_sigma_jk)
            if critical_sigma_jk != critical_node[3] and _j not in lista_temporal: # Si sigma_jk es igual al crítico
                lista_temporal.append(_j) # Lo agrego al nuevo vecindario factible
    return lista_temporal



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
                lista_ordenada = sorted([[_j.rho,_j.place] for _i, _j in neighbor.network_repr.nodes_supply.items() if _j.service == key],
                                        key=lambda x: x[0], reverse=True)
                 
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'rho_max':maximo_par,
                                          'lista_ordenada':lista_ordenada}
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
                lista_ordenada = sorted([[_node_i.access_ik,_node_i.place] for _index,
                                    _node_i in neighbor.network_repr.nodes_supply.items() if _node_i.service == key],
                                        key=lambda x: x[0], reverse=False)
                 
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'alpha_min':minimo_par,
                                          'lista_ordenada':lista_ordenada} 
            
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
                lista_ordenada = sorted([[_node_i.continuidad,_node_i.node_id] for _index,
                                    _node_i in neighbor.network_repr.nodes_demand.items()],
                                        key=lambda x: x[0], reverse=False)
                                          
                solucion_codificada[key]={'sigmas':lista_sigmas,
                                          'delta_min':minimo_par,
                                          'lista_ordenada':lista_ordenada}
            
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

#%% Calcular kpi



def calcular_kpi_local_search(current_solution):
    current_solution

    # Creo carpetas para current solution
    current_solution.create_folders_problem()
    # Si hay función objetivo (resultado de optimización)
    # Actualizo las matrices de solution.network_copy
    current_solution.network_copy.tecnica=current_solution.tecnica
    current_solution.network_copy.problem=current_solution #Creo una referencia al objeto padre Problem
    
    current_solution.network_copy.merge_niveles_capac(_post_optima=True,current_solution=current_solution)
    current_solution.network_copy.create_df_asignacion(_post_optima=True,current_solution=current_solution)
    current_solution.network_copy.create_df_probs_kk()
    current_solution.network_copy.create_df_arcos(_post_optima=True,current_solution=current_solution)
                      
    kpi.calculate_kpi(current_solution,_post_optima=True)
    #print (f"Se calcularon los KPI para la solución {current_solution.description_objective}.")

    if current_solution.objective == "1": 
        # Calculo los rho para cada nodo jk y lo almaceno en nodes_supply
        for _i,_j in current_solution.network_repr.nodes_supply.items():
            if _j.service != 'k00':
                if _j.matriz_λ['λ_ijk'].sum() == 0 or _j.capac_instal_sigma == 0:
                    _j.rho=0
                else: 
                    _j.rho = _j.matriz_λ['λ_ijk'].sum()/(_j.capac_instal_sigma*_j.rate)
    
    elif current_solution.objective =="2":
        # Calculo los alpha para cada nodo ik y lo almaceno en nodes_demand
        for _i,_j in current_solution.network_repr.nodes_demand.items():
            lista_access=current_solution.network_copy.file['df_accesibilidad'][current_solution.network_copy.file['df_accesibilidad']['nombre_I']==_i]
            lista_access=lista_access[['servicio_K','R']]
            _j.lista_accesibilidad= lista_access.set_index('servicio_K')['R'].to_dict()

           
        # Cargo los alpha para cada nodo ik y lo almaceno en nodes_supply
        for i,j in current_solution.network_repr.nodes_demand.items():
            for k,acc in j.lista_accesibilidad.items():
                current_solution.network_repr.nodes_supply['j'+i[-2:]+k].access_ik=acc
    
    elif current_solution.objective == "3":
        # Calculo los delta para cada nodo i y lo almaceno en nodes_demand
        for _i,_j in current_solution.network_repr.nodes_demand.items():
            lista_contin=current_solution.network_copy.file['df_continuidad'][current_solution.network_copy.file['df_continuidad']['nombre_I']==_i]
            lista_contin=lista_contin[['nombre_I','delta_i']]
            _j.continuidad= lista_contin.iloc[0]['delta_i']
            
        #Cargo los delta para cada nodo ik y lo almaceno en nodes_supply
        lista_k=data_functions.indices("k",current_solution.network_copy.K)
        for index_j,j in current_solution.network_repr.nodes_demand.items():
            cont=j.lista_continuidad[index_j]
            for k in lista_k:
                current_solution.network_repr.nodes_supply['j'+index_j[-2:]+k].cont_i=cont


# %% Optimización


def optimizacion(vecino_codificado,neighbor,current_solution):
    # Hace parte de la decodificación
    # Construye un objeto problem a partir de un vecino codificado
    neighbor_copy = decodificar_solucion (vecino_codificado,neighbor)           
                
    for _i,_j in neighbor_copy.network_repr.nodes_supply.items():
        a = _j.place
        b = _j.service
        c = _j.capac_instal_sigma
    
        fila = neighbor_copy.network_copy.file['df_capac'].query('nombre_J == @a and servicio_K == @b')
        
        if not fila.empty:
            # Si hay coincidencias, remplazar el sigma existente por c
            neighbor_copy.network_copy.file['df_capac'].loc[fila.index, 'sigma_jk'] = c
            # La actualización de los sigmas se da dentro de df_capac
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
        
        #archivo=directorio_padre+'/data/red_original/'+"datos_i16_j10_k10_base.txt"
        archivo=directorio_padre+'/data/red_original/'+"datos_i16_j10_k10_base.xlsx"
        #archivo = r"C:\Users\edgar\OneDrive - Universidad Libre\Doctorado\Códigos Python\HcNDP\Health-Care-Network-Design-Problem\hcndp/data/red_original/datos_i16_j10_k10_base.xlsx"
        
        # Borro carpeta con resultados de ejecuciones previas 
        data_functions.borrar_contenido_carpeta(os.getcwd()+'/output/')
        #print("\nContenidos borrados. \nContinuando...")
        
        # Creo los diccionarios de trabajo
        from hcndp import read_data
        networks_dict={} #Diccionario con las redes utilizadas en el programa
        problems_dict={} #Diccionario con los problemas y las soluciones a la red del programa

        # Definimos valores I,J,K
        I,J,K= [3,3,3]
        
        
        # Creamos un objeto network
        from hcndp import network
        _name="red_original"
        networks_dict[_name] = network.Network(I,J,K,archivo,_name)
        networks_dict[_name].create_folders()
        #print (f"\nSe ha creado exitosamente el objeto {_name}.")


        # Llenar objeto con datos (En este caso, datos .txt)
        #networks_dict[_name].read_file_txt(archivo)
        networks_dict[_name].read_file_excel(archivo)
        networks_dict[_name].delete_surplus_data() #Borro los datos que sobren
        networks_dict[_name]=read_data.fix_sigma_max(networks_dict, _name) #Corrijo errores en sigma_max

        #print ("#" * 60)
        #print (f"\nSe han cargado exitosamente los datos en el objeto {_name}.")
    

        # Creo el objeto solucion
        from hcndp import solutions
        solutions.create_problem_object(networks_dict['red_original'], problems_dict, name_problem="temporal")
        current_solution = problems_dict["temporal"]

        # Defino objetivo y método
        current_solution.optimizar=True
        current_solution.tecnica="GVNS"
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
        #print (f"Se ha actualizado el objeto {problems_dict[_solucion_temporal.name_problem].name_problem}")
                
        # Ejecuto algoritmo
        current_solution= gvns_search(current_solution,networks_dict['red_original'])
        
        