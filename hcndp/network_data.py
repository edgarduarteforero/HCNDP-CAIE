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

# <codecell> Clase red
class Network:
    def __init__(self,I,J,K,archivo):
        self.I=I
        self.J=J
        self.K=K
        self.archivo=archivo
        
