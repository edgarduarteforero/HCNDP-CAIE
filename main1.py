# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:30:26 2023

@author: edgar
"""

#%% <codecell> Libraries
from hcndp import menu
from hcndp import network_data
from hcndp.network_data import _I,_J,_K,_archivo,_name_network,_models
import os
_output=os.getcwd()+'/output/'

#%% <codecell> Execution

_name=input(f"Ingresa el nombre de la red. Por defecto se llama {_name_network}: ")
if not _name:  # Si la entrada está vacía
    _name=_name_network

    
networks={} #Diccionario con las redes utilizadas en el programa

#networks.append(network_data.Network(_I,_J,_K,_archivo,_name))
networks[_name] = network_data.Network(_I,_J,_K,_archivo,_name,_models)
networks[_name].create_folders()
menu.show_menu_main(networks[_name],networks)
