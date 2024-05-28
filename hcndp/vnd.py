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



def vnd_search(current_solution,network_original):
   
    
    # Basado en Gendrau y Potvin (2019). Capítulo 3
    # Definiciones:
    # current_solution: Objeto contenedor que agrupa: objetivo, red, datos, resultados, técnica, etc.
    # network_original: Objeto con datos originales de la red. No se modifica durante el código. Permance como referencia.
       
    # operadores VNS
    operadores = {
    1:'incremento1_decremento1_exhaust', 
    2:'incremento1_exhaust',
    3:'incremento1_all',
    4:'incremento2_decremento1_exhaust', 
    5:'incremento2_decremento2_exhaust', 
    6:'incremento3_decremento3_exhaust', 
    7:'chain_reaction_exhaust_plus_minus',
    8:'chain_reaction_exhaust_minus_plus'
    }
    num_operador=1
    
    landscape=[] # Vector para guardar la información del landscape construido
    
    # Cálculo de solución inicial
    best_neighbor = initial_solution.initial_solution(current_solution,network_original)
    calcular_kpi_local_search(best_neighbor) #Mido KPI de solución inicial
    
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    best_neighbor = initial_solution.fix_initial_solution(best_neighbor)  
    
    # Defino la mejor solución encontrada
    calcular_kpi_local_search(best_neighbor)# Calculo KPIs
    qual_best=best_neighbor.network_copy.file['df_medidas']['rho_max'][0] 
    
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
    _best_rho=best_neighbor_codificado["k_rho_max"]
    print (f'Valor función objetivo inicial: {best_neighbor_codificado[_best_rho]["rho_max"][0]}')

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

    # K-rule: maximum number of neighborhood operators
    stopping_condition_K_rule = False
    k_max=8
    
    # Solución que ingresa al bucle
    neighbor = copy.deepcopy(best_neighbor)
        
    # Defino el primer operador
    operador=operadores[1]

    while stopping_condition_K_rule == False:
        
        print (f'Vecindario número = {contador}')       
        
        # Generar vecindario a partir de la mejor solución hallada
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
        neighborhood = neighborhood_exhaustive_codificado(neighbor_codificado,operador) 
                
        # Tamizaje de soluciones
        neighborhood_feasible=tamizaje_soluciones(best_neighbor,neighborhood)
        
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
        print (f'Mejor solución del vecindario {contador}: {qual_best_of_neighborhood}')
        
        
        # Comparo la mejor solución del vecindario con la mejor solución obtenida.
        current_neighbor, operador, iterations_without_improvement,landscape,\
        qual_best, best_neighbor, num_operador = \
        neighborhood_change(best_neighbor, qual_best , 
                                best_of_neighborhood , qual_best_of_neighborhood, 
                                landscape , operador, operadores,num_operador,
                                iterations_without_improvement)
        print (f"Operador: {operador}")
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
    print (best_neighbor.df_sigma.to_string())
    print (f"Valor función objetivo: {best_neighbor.network_copy.file['df_medidas']['rho_max'][0] }")
    print (f"Vecindario final número: {contador-1}")   
    
    best_neighbor.landscape=landscape
    current_solution = copy.deepcopy(best_neighbor)
    
    return current_solution

#%% Funciones de VNS
def neighborhood_change(best_neighbor, qual_best , 
                        best_of_neighborhood , qual_best_of_neighborhood, 
                        landscape , operador, operadores,num_operador,
                        iterations_without_improvement):
    # Comparo la mejor solución del vecindario con la mejor solución obtenida.
    print ("Comparación de mejor solución de vecindario con mejor solución obtenida")
    if qual_best_of_neighborhood < qual_best:
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
        iterations_without_improvement += 1
        
        # Actualizo el operador de vecindario
        num_operador += 1
        operador = operadores[num_operador]
    
    return neighbor, operador,\
            iterations_without_improvement,\
            landscape, qual_best, best_neighbor, num_operador

#%% Manipulación de vecindario

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
                #neighborhood_sigmas_k = globals()[operador](vector_original_sigmas)
                neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)    
            else: # Aplico operador seleccionado por el usuario
                #neighborhood_sigmas_k = globals()[operador](vector_original_sigmas)
                neighborhood_sigmas_k = getattr(neighborhood_operator, operador)(vector_original_sigmas)    
                
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
    for vecino_codificado in neighborhood_feasible: #Para cada solucion del vecindario factible
        
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

#%% Cálculo de kpi

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
        I,J,K= [5,5,5]
        
        
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
        current_solution= vnd_search(current_solution,networks_dict['red_original'])
        
        