# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 10:29:00 2023

@author: edgar
"""

# <codecell> Variables
_I=4
_J=4
_K=4

_archivo="datos_i16_j10_k10_base.xlsx"

_name_network="red_original"

_models={}
# <codecell> Clase red
class Network:
    def __init__(self,I,J,K,archivo,name,models):
        self.I=I
        self.J=J
        self.K=K
        self.archivo=archivo
        self.name=name
        self.models=models
        
    def create_folders(self):
        import os

        # Comprueba si el directorio no existe antes de intentar crearlo
        if not os.path.exists(os.getcwd()+'/data/'+self.name+'/'):
            # Crea el directorio
            os.makedirs(os.getcwd()+'/data/'+self.name+'/')
            print(f"Directorio /data/'{self.name}' creado con éxito.")
        else:
            print(f"El directorio /data/'{self.name}' ya existe.")
            
        
        if not os.path.exists(os.getcwd()+'/output/'+self.name+'/'):
            # Crea el directorio
            os.makedirs(os.getcwd()+'/output/'+self.name+'/')
            print(f"Directorio /output/'{self.name}' creado con éxito.")
        else:
            print(f"El directorio /output/'{self.name}' ya existe.")
        
# <codecell> Clase modelo
class Model_pyomo:
    def __init__(self,model_abstract,instance,data_dat,solution,nombre_modelo):
        self.model_abstract=model_abstract
        self.instance=None
        self.data_dat=None
        self.solution=None
        self.nombre_modelo=None
