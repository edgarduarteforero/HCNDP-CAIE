# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:04:10 2023

@author: edgar
"""

def read_parameters(network):
    #from hcndp.network_data  import I,J,K, archivo
    archivo=network.archivo
    I=network.I
    J=network.J
    K=network.K
    # Indica el archivo fuente
    print (f"El archivo por defecto es {archivo}.") 
    nuevo_archivo= input("Ingresa el nombre del archivo: ") or archivo
    
    # Indica la cantidad de nodos de origen
    print (f"La cantidad de nodos origen por defecto es {I}")
    nuevo_I= input("Ingresa la cantidad de nodos origen: ") or I
    
    # Indica la cantidad de nodos de oferta
    print (f"La cantidad de nodos oferta por defecto es {J}")
    nuevo_J= input("Ingresa la cantidad de nodos oferta: ") or J
    
    #Indica la cantidad de nodos de servicio
    print (f"La cantidad de servicios por defecto es {K}")
    nuevo_K= input("Ingresa la cantidad de servicios: ") or K
    
    update_parameters(nuevo_archivo,nuevo_I,nuevo_J,nuevo_K,network)
    
    print (nuevo_archivo,nuevo_I,nuevo_J,nuevo_K)

def update_parameters(nuevo_archivo,nuevo_I,nuevo_J,nuevo_K,network):
    print ("update_parameters")
    network.archivo=nuevo_archivo
    network.I=int(nuevo_I)
    network.J=int(nuevo_J)
    network.K=int(nuevo_K)
    
def read_file_excel(network,path):
    print ("read_file_excel")
    import pandas as pd
    import os
    network.file = pd.read_excel(path, sheet_name=None)

def data_by_hand():
    print ("hola")

def delete_surplus_data(network):
    from hcndp.data_functions import indices
    
    items=indices("i",network.I)
    network.file['df_demanda']=network.file['df_demanda'].query('nombre_I in @items')
    network.file['df_dist_ij']=network.file['df_dist_ij'].query('nombre_I in @items')
    network.file['df_w_ij']=network.file['df_w_ij'].query('nombre_I in @items')
    network.file['df_flujos_ijk']=network.file['df_flujos_ijk'].query('nombre_I in @items')

    items=indices("j",network.J)
    network.file['df_oferta']=network.file['df_oferta'].query('nombre_J in @items')
    network.file['df_capac']=network.file['df_capac'].query('nombre_J in @items')
    network.file['df_dist_ij']=network.file['df_dist_ij'].query('nombre_J in @items')
    network.file['df_w_ij']=network.file['df_w_ij'].query('nombre_J in @items')
    network.file['df_flujos_ijk']=network.file['df_flujos_ijk'].query('nombre_J in @items')

    items=indices("k",network.K)
    network.file['df_niveles']=network.file['df_niveles'].query('servicio_K in @items')
    network.file['df_capac']=network.file['df_capac'].query('servicio_K in @items')
    network.file['df_flujos_ijk']=network.file['df_flujos_ijk'].query('servicio_K in @items')


def merge_niveles_capac(network):
    #Agrego las columna nivel de atención y ubicaciones
    import pandas as pd
    network.file['df_capac']=pd.merge(network.file['df_capac'],network.file['df_niveles'],on='servicio_K',how='left')
    network.file['df_capac']=pd.merge(network.file['df_capac'],network.file['df_oferta'],on='nombre_J',how='inner')
    network.file['df_capac']=network.file['df_capac'].set_index(['nombre_J','servicio_K'],drop=True)
    
    if network.file['df_capac']['s_jk'].sum() < network.file['df_capac']['sigma_jk'].sum():
        print ("""Hay un error en la capacidad.
               La suma de los s_jk es menor a la suma de los sigma_jk asignados.
               """)
        raise SystemExit("Stop right there!")
        
def create_df_asignacion(network):
    import pandas as pd
    from hcndp.data_functions import decay_gauss
    
    # Creo la matriz df_asignación para construir los arcos de la red
    # En la matriz df_asignacion creamos las columnas para incorporar la función de decaimiento de la distancia
    network.file['df_asignacion']=pd.DataFrame()
    network.file['df_asignacion']=network.file['df_capac'].reset_index().set_index('nombre_J')

    #Fusiono matrices de oferta y distancia creando arcos
    network.file['df_asignacion']=\
            (pd.merge(network.file['df_asignacion'], \
            network.file['df_dist_ij'].set_index(['nombre_J']),
            left_index=True,right_index=True,how='outer').sort_values('dist_IJ').reset_index())
    
    #Creo una matriz con las distancias de cobertura que se digitaron como parámetros
    network.file['df_asignacion']=pd.merge(network.file['df_asignacion'], 
            network.file['df_demanda'].reset_index()[['nombre_I','ubicacionesI_x','ubicacionesI_y']] 
            ,on='nombre_I',how='inner').drop_duplicates()
     
    # Calculo las distancias ajustadas por la función de decaimiento con el título f_dij
    network.file['df_asignacion']['f_dij']=network.file['df_asignacion']. \
                apply(lambda row: decay_gauss(row["dist_IJ"],row["d_o_k"]),axis='columns')
    network.file['df_asignacion']=network.file['df_asignacion']. \
                set_index(['nombre_J','servicio_K'])

    network.file['df_flujos_ijk']=network.file['df_flujos_ijk'].set_index(['nombre_I','nombre_J','servicio_K']).sort_index()
    network.file['df_asignacion']=network.file['df_asignacion'].drop(['tao_ijk','z_ijk'], axis=1, errors='ignore')
    network.file['df_asignacion']=network.file['df_asignacion'].reset_index()
    network.file['df_asignacion']=network.file['df_asignacion'].set_index(['nombre_I','nombre_J','servicio_K'])
    network.file['df_asignacion']=pd.merge(network.file['df_asignacion'], network.file['df_flujos_ijk'],left_index=True, right_index=True)
def create_df_probs_kk(network):
    import numpy as np
    import pandas as pd
    from hcndp.data_functions import indices
    
    # Obtengo las probabilidades de transferencia entre servicios y lo covierto en un df kk'
    data1 = network.file['prob_serv']
    data1=data1.drop(['Unnamed: 0'], axis=1)
    data1=data1.loc[np.arange(network.K)]
    data1=data1[np.arange(network.K)+1]
    data1=np.nan_to_num(data1) 
    
    # Obtengo los flujos habilitados entre j y j'
    data2 = network.file['flujos_jj']
    data2=data2.loc[np.arange(network.J)]
    data2=data2.iloc[:,np.arange(network.J)+1]
    data2=np.nan_to_num(data2) 
    
    #Convierto data1 a un dataframe con títulos
    network.file['df_probs_kk'] = pd.DataFrame(data = data1, 
                                               index = indices("k",network.K), 
                                               columns = indices("k",network.K))
    network.file['df_probs_kk'] = network.file['df_probs_kk']. \
                                melt(ignore_index=False).reset_index(). \
                                rename(columns={"index": "servicio_K", "variable": "servicio_Kp","value":"p_kkp"})
    network.file['df_probs_kk']['bin']=(network.file['df_probs_kk']['p_kkp']!=0).astype(int)
    
    #Convierto data2 a un dataframe con títulos
    network.file['df_flujos_jj'] = pd.DataFrame(data = data2, index = indices("j",network.J), 
                                                columns = indices("j",network.J))
    network.file['df_flujos_jj'] = network.file['df_flujos_jj'].\
                                melt(ignore_index=False).\
                                reset_index().\
                                rename(columns={"index": "nombre_J", "variable": "nombre_Jp","value":"x_jjp"})


def create_df_arcos(network): 
    # Creo df_arcos con los índices de j y de k. Es un df con [j j' k k']
    # Explicación en p- 9B Notas del doctorado
    
    from hcndp.data_functions import indices
    import pandas as pd
    import numpy as np
    
    lista=[]
    j=indices("j",network.J)
    k=indices("k",network.K)
    for a in j:
      for b in j:
        for c in k: # range (1,K+1):
          for d in k: #range(1,K+1):
            lista.append([a,c,b,d])
    
    network.file['df_arcos']=pd.DataFrame(lista,columns=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'])
    network.file['df_arcos'].sort_values(by=['nombre_J','servicio_K'], inplace=True)
    
    # Construyo la matriz a partir de las probabilidades de transferencia entre servicios kk' y 
    # los flujos habilitados jj'
    # Obtengo las probabilidades de transferencia entre servicios y lo covierto en un df kk'
    data1 = network.file['prob_serv'].drop(['Unnamed: 0'], axis=1)
    data1 = data1.loc[np.arange(network.K)]
    data1 = data1[np.arange(network.K)+1]
    data1 = np.nan_to_num(data1) 

    # Obtengo los flujos habilitados entre j y j'
    data2 = network.file['flujos_jj']
    data2=data2.loc[np.arange(network.J)]
    data2=data2.iloc[:,np.arange(network.J)+1]
    data2=np.nan_to_num(data2) 

    # Construyo una matriz con las probabilidades 
    matriz=network.file['df_capac'].loc[:]['sigma_jk'].to_numpy().reshape(network.J,network.K) #Matriz con los valores de sigma_jk. 
    matriz=np.where(matriz == 0, 0, 1) #Convierto matriz a binario
    probs=[]
    for j_ in range (network.J):
        for k_ in range (network.K):
            #data1:probabilidades entre servicios k
            #data2:enlaces entre instalaciones j
            #matriz: capacidad de recibir en jk
            data4=np.where(data1== 0, 0, 1) #Convierto matriz de data1 a binario
            data4=np.tile(data4[k_], (network.J, 1)) #Construyo una matriz de J filas y k columnas 
            # Cada fila indica si puedo enviar desde cada j y k_ a cualquier otro k
            data4=np.multiply(data4,matriz) # Combino matrices. 
            # Data4 indica si puedo enviar desde J y K1 a cualquier destino k de acuerdo con las probabilidades
            # Matriz indica si la combinación j k puede recibir de acuerdo con la capacidad sigma_jk
            # Estoy en un bucle. La matriz indica desde j_ y k_ a qué j__ y k__ puedo remitir
            data4=np.multiply(data4,np.transpose(np.tile(data2[j_],(network.K,1)))) #Combino con los enlaces entre j1 y j2
            #La suma de cada columna en j4 indica a cuántos destinos puedo enviar desde j1 y k1
            for j__ in range (network.J):
                for k__ in range (network.K):
                    a = data2[j_,j__]*data1[k_,k__]*matriz[j__,k__]/np.sum(data4[:,k__]) if np.sum(data4[:,k__])!=0 else 0
                    #probs.append([j_,k_,j__,k__,data2[j_,j__],data1[k_,k__],matriz[j__,k__],np.sum(data4[:,k__]),a])
                    
                    probs.append(a)
                    # Probs depende de si existe p_kk (data1), si existe x_jj (data2), si hay capacidad sigma_jk (matriz) y el número de destinos
                    # Probs de ir de jk a j'k'. Se divide por el número de destinos para
                    # no incurrir en que la suma de las probabilidades sea mayor a 1.

    probs = np.reshape(probs,([len(data1)*len(data2),len(data1)*len(data2)]))
    
    # Cada fila es un par jk y cada columna es un par j'k'
    # Con base en la matriz de probabilidades construyo los arcos
    network.file['df_arcos']['p_jjkk']=probs.flatten()
    
    # Agrego las coordenadas de cada servidor j y jp
    network.file['df_arcos']=network.file['df_arcos'].set_index(['nombre_Jp'])
    network.file['df_arcos']=pd.merge(network.file['df_arcos'],
                                      network.file['df_oferta'].set_index('nombre_J'),
                                      left_index=True,right_index=True,how='outer')
    network.file['df_arcos']=network.file['df_arcos'].reset_index()
    network.file['df_arcos']=network.file['df_arcos'].rename(columns={"ubicacionesJ_x":"ubicacionesJp_x",
                                                                      "ubicacionesJ_y":"ubicacionesJp_y",
                                                                      "index":"nombre_Jp"})
    network.file['df_arcos']=network.file['df_arcos'].set_index(['nombre_J'])
    network.file['df_arcos']=pd.merge(network.file['df_arcos'],network.file['df_oferta'].set_index('nombre_J'),
                                      left_index=True,right_index=True,how='outer')
    
    
if __name__ == "__main__":

    
    #read_parameters()    
    #df_niveles=read_data_from_file()
    from hcndp import network_data
    from hcndp.network_data import _I,_J,_K,_archivo 
    import os
    network=network_data.Network(_I,_J,_K,_archivo)
    #path=os.getcwd()+'\\data\'+network.archivo
    path=os.path.dirname(os.getcwd())+'/data/'+network.archivo
    read_file_excel(network,path)
    delete_surplus_data(network)
    merge_niveles_capac(network)
    create_df_asignacion(network)
    #create_df_probs_kk(network)
    #create_df_arcos(network)
