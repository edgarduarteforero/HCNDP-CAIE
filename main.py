# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:30:26 2023

@author: edgar
"""

#%%  Bienvenida
import textwrap
print ("#" * 60)
print (textwrap.dedent(''' \
       \nBienvenido a nuestra aplicación:
           HEALTHCARE NETWORK
               DESIGN PROBLEM
        
        Esta aplicación busca ayudar a la toma de decisiones 
        sobre diseño de redes en salud. 
       
       '''))
print ("#" * 60)

input ("\nPulsa cualquier tecla para continuar.")

#%% Borrar carpetas antiguas
def borrar_carpeta(prompt):
    while True:
        respuesta = input(prompt + " (y/n): ").lower()
        if respuesta in ["y", "n"]:
            return respuesta
        else:
            print("Por favor, ingresa 'y' o 'n'.")

_respuesta_usuario = borrar_carpeta("¿Quieres borrar los resultados de las últimas ejecuciones?")
if _respuesta_usuario == "y":
    from hcndp import data_functions
    import os
    data_functions.borrar_contenido_carpeta(os.getcwd()+'/output/')
    print("\nContenidos borrados. \nContinuando...")
else:
    print("\nContinuando...")



#%%  IJK y nombre archivo
from hcndp import read_data

networks_dict={} #Diccionario con las redes utilizadas en el programa
problems_dict={} #Diccionario con los problemas y las soluciones a la red del programa
multiobjective_dict={} #Diccionario con los problemas multiobjetivo del programa

# Indicamos origen de datos y definimos valores I,J,K
I,J,K,archivo = read_data.menu_select_file(I=0) #I=0 sirve para condicionar la salida del menú
I, J, K= map(int, [I, J, K])
#%%  Objeto network
from hcndp import network

# Creamos un objeto network
_name=input("\nIngresa el nombre de la red. Si pulsas enter se asigna 'red_original': ")
if not _name:  # Si la entrada está vacía
    _name="red_original"

networks_dict[_name] = network.Network(I,J,K,archivo,_name)
networks_dict[_name].create_folders()
_optimizar=False
print (f"\nSe ha creado exitosamente el objeto {_name}.")


#%%  Llenar objeto con datos de Excel

networks_dict[_name].read_file_excel(archivo)
networks_dict[_name].delete_surplus_data()

print ("#" * 60)
print (f"\nSe han cargado exitosamente los datos en el objeto {_name}.")


#%%  Menú tipo de problema (mono o multi)

import textwrap
while True:
    print("\n----------------------------------------------------------")
    print("Indica qué tipo de problema quieres estudiar.")
    print("main.py")
    print("----------------------------------------------------------\n")
    print("Selecciona una opción:")
    print("1. Problemas mono-objetivo")
    print("2. Problemas multi-objetivo")
    print("10. Salir")

    _opcion = input("Selecciona una opción: ")

     #%%  Menú problemas y soluciones mono_objetivo
    if _opcion =="1":
         from hcndp import solutions
         # Indicamos origen de datos y definimos valores I,J,K
         solutions.menu_solutions(network_original=networks_dict[_name],
                                  problems_dict=problems_dict
                                  )    

    #%% Menú problemas y soluciones multi-objetivo
    elif _opcion == "2":

        from hcndp import multiobjective
        # Indicamos origen de datos y definimos valores I,J,K
        multiobjective.menu_multiobjective(network_original=networks_dict[_name],
                                 problems_dict=problems_dict,
                                 multiobjective_dict=multiobjective_dict
                                 )
    
    #%%  Salir
    elif _opcion == "10":
            break
    else:
            print("Opción no válida. Inténtalo de nuevo.")

