# -*- coding: utf-8 -*-
"""
Created on Mon May 27 12:20:54 2024

@author: edgar
"""
import random


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

