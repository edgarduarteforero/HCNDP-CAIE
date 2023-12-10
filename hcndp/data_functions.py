# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 07:13:12 2023
Generación de índices, parámetros, ubicaciones, distancias, cubrimiento de cobertura, función Decay Gaussian.
@author: edgar
"""

#Genero los índices para cualquier letra (I,J,K) y su cantidad.
def indices1(letra,cantidad): # Se generan listas tipo j1,j2,j3
    matr=[str("%s%d" % (letra.lower(),i+1)) for i in range (cantidad)]
    return matr

def indices(letra,cantidad): # Se generan listas tipo j01,j02,j03
    matr=[]
    for i in range (1,cantidad+1):
        matr.append(letra+f"{i:02d}")
    return matr

#Creo un parámetro llamado 'par' (h) con un solo subíndice y valores enteros aleatorios. Ej: h_i
def param_simple(par,letra,cantidad,lim): 
    matr=[np.random.randint(lim[0],lim[1]+1) for i in range (cantidad)]
    return matr

#Creo un parámetro llamado 'par' (d) con dos subíndices y valores enteros aleatorios. Ej:c_jk
def param_doble(par,letra1,letra2,cantidad1,cantidad2,lim): 
    matr=[np.random.randint(lim[0],lim[1]+1) for j in range (cantidad2) for i in range (cantidad1)]
    return matr
#param_doble("h","I","K",I,K,lim_h)

#Genero una lista "ubica" con coordenadas x e y.
def ubicaciones(letra,cantidad): 
    ubica=np.random.uniform(0,1,(cantidad,2)) #Coordenadas aleatorias
    return ubica

#Genero una matriz de distancias euclideanas entre dos listas de coordenadas
def distancias(par,matr1,matr2,letra1,letra2): 
    distancias = distance.cdist(matr1, matr2, 'euclidean')
    return distancias

#Genero una matriz de coberturas para cada par de nodos ij.
def cobertura(par,matr,maximo,letra1,letra2,cantidad1,cantidad2): 
    matr_cob=matr<=maximo
    return matr_cob*1

#Calculo decaimiento de distancias por método Gaussiano (Tao 2020 y Delamater 2013)
def decay_gauss(d_ij,do):
    import numpy as np
    if d_ij<do:
        f=np.exp((-1/2)*(d_ij/do)**2) - np.exp(-1/2)
        f=(f/(1-np.exp(-1/2)))
    else:
        f=0
    return f

if __name__ == "__main__":
    
    import numpy as np
    from scipy.spatial import distance
    print (decay_gauss(5,8))
