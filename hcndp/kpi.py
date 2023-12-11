# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 12:20:02 2023

@author: edgar
"""

def set_lambda_jk (network):
    import numpy as np
    from hcndp.data_functions import reshape_matrix
    
    
    # Matriz de arribos externos g
    g=np.array(network.file['df_asignacion']['tao_ijk']) # Lista de arribos externos ijk
    g=reshape_matrix(g, network.I, network.J*network.K)
    g=np.sum(g,axis=0) #Lista de suma por cada jk. Son los gamma jk
    # Nótese que se hace la suma de los g en el eje 0 para obtener los g_jk a partir de la suma en i de los g_ijk

    # SEGUNDO BLOQUE
    # Cálculo de lambdas y rho para cada par j k
    df_capac=network.file['df_capac']
    probs=network.file['df_arcos']['p_jjkk']
    probs=reshape_matrix(probs, network.J*network.K, network.J*network.K)
    df_capac['lambdas']=np.matmul(g,np.linalg.inv(np.identity(len(probs))-(probs)))
    df_capac.replace([np.inf,-np.inf], 0, inplace=True)
    df_capac['r']=df_capac['lambdas']/df_capac['c_jk'] #c_jk es la tasa de atención, es decir mu
    df_capac['rho']=df_capac['lambdas']/(df_capac['c_jk']*df_capac['sigma_jk']) # 
    df_capac.replace([np.inf,-np.inf], 0, inplace=True)
    df_capac.fillna(0,inplace=True)
    
def set_lambda_ijk (network):
    import numpy as np
    from hcndp.data_functions import reshape_matrix

    # Calculo los lambdas para cada ijk
    # Se calculan a través de un loop asumiendo que solo hay arribos en cada i
    g=np.array(network.file['df_asignacion']['tao_ijk']) # Lista de arribos externos ijk
    g=reshape_matrix(g, network.I, network.J*network.K)# Matriz de arribos externos de i por (jk)    


    # Puedo calcular los lambda ijk basado en redes de Jackson
    network.file['df_asignacion']["lambda_ijk"] = 0.0
    probs=network.file['df_arcos']['p_jjkk']
    probs=reshape_matrix(probs, network.J*network.K, network.J*network.K)
    
    #Para cada i calculo el lambda ijk
    _i=0
    for i in network.file['df_asignacion'].index.levels[0]: 
        #df_asignacion.loc[i,'lambda_ijk']=1
        network.file['df_asignacion'].loc[i,'lambda_ijk']=np.matmul(g[_i],np.linalg.inv(np.identity(len(probs))-(probs)))
        _i+=1

if __name__ == "__main__":
    import hcndp
    from hcndp import network_data
    from hcndp.read_data import read_file_excel
    from hcndp.network_data import _I,_J,_K,_archivo 
    from hcndp.figures import figure_network_cartesian
    import os
    network=network_data.Network(_I,_J,_K,_archivo)
    path=os.path.dirname(os.getcwd())+'/data/'+network.archivo
    read_file_excel(network,path)
    #read_data.read_parameters(network)
    read_file_excel(network,path)
    hcndp.read_data.delete_surplus_data(network)
    hcndp.read_data.merge_niveles_capac(network)
    hcndp.read_data.create_df_asignacion(network)
    hcndp.read_data.create_df_probs_kk(network)
    hcndp.read_data.create_df_arcos(network)