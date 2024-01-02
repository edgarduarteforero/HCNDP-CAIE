# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:30:26 2023

@author: edgar
"""

#%% <codecell> Bienvenida
import textwrap
print ("#" * 60)
print (textwrap.dedent(''' \
       Bienvenido a nuestra aplicación:
           HEALTHCARE NETWORK
               DESIGN PROBLEM
        
        Esta aplicación busca ayudar a la toma de decisiones 
        sobre diseño de redes en salud. 
       
       '''))
print ("#" * 60)

input ("\nPulsa cualquier tecla para continuar.")


#%% <codecell> IJK y nombre archivo
from hcndp import read_data

# Indicamos origen de datos y definimos valores I,J,K
I,J,K,archivo = read_data.menu_select_file()
I, J, K= map(int, [I, J, K])
#%% <codecell> Objeto network
from hcndp import network

# Creamos un objeto network
_name=input("\nIngresa el nombre de la red. Si pulsas enter se asigna 'red_original': ")
if not _name:  # Si la entrada está vacía
    _name="red_original"

networks_dict={} #Diccionario con las redes utilizadas en el programa
solutions_dict={} #Diccionario con las soluciones a las redes del programa
networks_dict[_name] = network.Network(I,J,K,archivo,_name)
networks_dict[_name].create_folders()
_optimizar=False
print (f"\nSe ha creado exitosamente el objeto {_name}.")


#%% <codecell> Llenar objeto con datos de Excel

networks_dict[_name].read_file_excel(archivo)
networks_dict[_name].delete_surplus_data()
print (f"\nSe han creado exitosamente los datos en el objeto {_name}.")


#%% <codecell> Menú soluciones

from hcndp import solutions
# Indicamos origen de datos y definimos valores I,J,K
solutions.menu_solutions(network_original=networks_dict[_name],
                         solutions_dict=solutions_dict,
                         )

#%% <codecell> Menú análisis

