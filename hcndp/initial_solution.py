# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:19:25 2024

@author: edgar
"""

def initial_solution(solution,network_original):
    #Creo la representación de la red
    import pandas as pd
    import numpy as np
    from hcndp import network
    import copy
    
    
    network_repr=network.Network_representation(network_original.I,
                                                network_original.J,
                                                network_original.K,
                                                network_original.archivo,
                                                network_original.file)
    path_repr=network.Path_representation(network_original.K, 
                                          network_original.archivo,
                                          network_original.file)
    
    # Asignación de recurso σ_k para cada nodo de oferta j 
    for _k in path_repr.nodes_services.keys():
        if _k !=  'k00':
            #print ("Asignación de recursos para: ", _k)
            network_repr.asignacion_recursos(path_repr,_k)
            #for _i,_j in network.nodes_supply.items():
             #   if _j.capac_instal_sigma != 0:
                    #print (_i,_j.capac_instal_sigma)


    # Construyo el df_sigma con los resultados de la asignacion
    # Crear listas vacías para almacenar los datos
    places = []
    services = []
    capac_instal_sigma = []

    # Iterar a través del diccionario nodes_supply y extraer los datos
    for node in network_repr.nodes_supply.values():
        places.append(node.place)
        services.append(node.service)
        capac_instal_sigma.append(node.capac_instal_sigma)

    # Crear el DataFrame
    network_repr.df_sigma = pd.DataFrame({
        'place': places,
        'service': services,
        'capac_instal_sigma': capac_instal_sigma
         })            
    network_repr.df_sigma = network_repr.df_sigma.dropna(subset=['capac_instal_sigma'])
    solution.df_sigma=network_repr.df_sigma
    # Para k=0 creo valores de λ_ijk0 
    # El valor de λ_ijk0 es igual a la demanda que hay en cada nodo ik0.
    for _,_j in network_repr.nodes_supply.items():
        for _p,_i in _j.matriz_λ.iterrows():
            if _i['nombre_I'].replace('i','j')==_i['nombre_J'] and _i['servicio_K']=='k00':
                _j.matriz_λ.loc[_p, 'λ_ijk'] = network_repr.nodes_demand[_i['nombre_I']].demand
    # Construyo primera solución 
    # Ordeno el diccionario de ser_ser_R
    path_repr.edges_ser_ser_R=dict(sorted(path_repr.edges_ser_ser_R.items()))
    
    for _i in path_repr.edges_ser_ser_R.values():
        k=_i.source
        kp=_i.target
    
        #if k < kp:
            # Obtengo los delta ijkk
        network_repr.asignacion_flujos_δ(network_repr,path_repr,k,kp) 
        
            # Solución entre k y kp* obtengo los phi ijkjk
        network_repr.solucion_entre_k_kp(network=network_repr,_k=k,
                                             _kp=kp,
                                             archivo=network_original.file)
            
            # Obtengo las aproximaciones de lambda
        network_repr.construyo_λ(network_repr,kp)
        
        
        #if k == kp:
            # Obtengo los delta ijkk
        #    network_repr.asignacion_flujos_δ(network_repr,path_repr,k,kp) 
        
        
    # Porcentajes de flujo. Obtengo los pi jk jk
    network_repr.obtencion_π(network_repr)
        
    
    
    # for _i in path_repr.edges_ser_ser_R.values():
    #     k=_i.source
    #     kp=_i.target
    #     network_repr.construyo_λ(network_repr,kp)
    
        #elif k == kp:
        #    network_repr.asignacion_π_ciclos(network_repr,k,kp)
    
        #elif k > kp:
        #    network_repr.asignacion_π_ciclos(network_repr,kp,k)
        
    
    
    # Construyo una matriz g con los arribos externos, es decir los ϕi.j.k0jk
    from hcndp.data_functions import indices

    _lista_i=indices("i",network_original.I)
    _lista_j=indices("j",network_original.J)
    _lista_k=indices("k",network_original.K)
    
    #_lista_k_00=_lista_k
    #_lista_k_00.append('k00')
    from itertools import product
    _lista = list(product(_lista_i, _lista_j,_lista_k))
    _g=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
    _g['tao_ijk'] = 0.0
    _g=_g.sort_values(by=['nombre_I', 'nombre_J','servicio_K'])
    solution.df_f_ijk=_g
    
    def arribos_externos(poblacion_origen,servicio_origen,nodo_destino):
        suma_acumulativa=0
        for clave,valor in network_repr.edges_sup_sup_X.items():
            if valor.node_demand_pop == poblacion_origen and valor.service_source==servicio_origen and valor.target==nodo_destino :
                suma_acumulativa += valor.flow_sup_sup_phi
        return suma_acumulativa
        
    _g['tao_ijk']=_g.apply (lambda row: arribos_externos(row['nombre_I'],'k00',row['nombre_J']+row['servicio_K']),axis=1)
    _g=np.array(_g['tao_ijk']) # Lista de arribos externos ijk
    _g=np.reshape(_g,([network_original.I,network_original.J*(network_original.K)])) # Matriz de arribos externos de i por (jk)
    
    
    # Construyo las matrices con las probabilidades π  
    _lista = list(product(_lista_i, _lista_j,_lista_k,_lista_j,_lista_k))
    _π=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K', 'nombre_Jp','servicio_Kp'])
    _π['π_ijkjk'] = 0.0   
    _π=_π.sort_values(by=['nombre_I','nombre_J', 'servicio_K','nombre_Jp','servicio_Kp'])
    _π['p*π'] = 0.0
    
    for _,_fila in _π.iterrows():
        _i=_fila['nombre_I']
        _j=_fila['nombre_J']
        _k=_fila['servicio_K']
        _jp=_fila['nombre_Jp']
        _kp=_fila['servicio_Kp']
        for _nombre,_arco in network_repr.edges_sup_sup_X.items():
            if  _nombre == _i+_j+_k+_jp+_kp:
                _π.loc[_,'π_ijkjk'] = _arco.flow_sup_sup_perc
        
        for _nombre,_arco in path_repr.edges_ser_ser_R.items():
            if  _nombre == _k+_kp:
                _π.loc[_,'p*π'] = _arco.transfer_percentage  * _π.loc[_,'π_ijkjk']
   
        
   
    # Calculo los flujos entrantes lambda ijk basado en redes de Jackson
    _lista = list(product(_lista_i, _lista_j,_lista_k))
    _df_asignacion=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
    _df_asignacion["lambda_ijk"] = 0.0
    _df_asignacion=_df_asignacion.sort_values(by=['nombre_I','nombre_J', 'servicio_K'])
    _df_asignacion.set_index(['nombre_I', 'nombre_J','servicio_K'],inplace=True)
    
    
    
    #Para cada i calculo el lambda ijk usando Jackson
    _fila=0
    for i in _lista_i:
        probs=_π.loc[(_π['nombre_I']==_lista_i[_fila])]
        probs=probs.sort_values(by=['nombre_J', 'servicio_K','nombre_Jp','servicio_Kp'])
        probs=np.array(probs['π_ijkjk'])
        #probs=np.array(probs['p*π'])
        probs=np.reshape(probs,([network_original.J*(network_original.K),network_original.J*(network_original.K)]))
        _df_asignacion.loc[i,'lambda_ijk']=np.matmul(_g[_fila],np.linalg.inv(np.identity(len(probs))-(probs)))
        _fila+=1
    # Actualizo los valores de lambda en las matrices en cada nodo oferta
    for _,_j in network_repr.nodes_supply.items():
        if _j.service!='k00':
            _j.matriz_λ=_df_asignacion.loc[(slice(None),_j.place,_j.service),:]
            _j.matriz_λ.reset_index(inplace=True)
            _j.matriz_λ = _j.matriz_λ.rename(columns={'lambda_ijk': 'λ_ijk'})
    
    # Actualizo los delta con base en los nuevos lambda
    for _i in path_repr.edges_ser_ser_R.values():
        k=_i.source
        kp=_i.target
    
        # Obtengo los delta ijkk
        network_repr.asignacion_flujos_δ(network_repr,path_repr,k,kp) 
        
    # Actualizo los phi con base en los nuevos lambda
    network_repr.solucion_flujos_phi_post_Jackson(network_repr)
            
           
    # Actualizo el df_asignacion en network
    
    solution.df_asignacion=_df_asignacion
    network_repr.df_asignacion=_df_asignacion
    solution.df_l_jk = network_repr.df_asignacion.groupby(level=['nombre_J', 'servicio_K']).sum()
    
    # Llevar solución a un df_solucion
    _lista=[] 
    for _i,_j in network_repr.edges_sup_sup_X.items():
        _lista.append([_j.node_demand_pop,
                       _j.source,_j.target,
                       _j.flow_sup_sup_perc_ijkjk,
                       _j.flow_sup_sup_phi,
                       _j.flow_sup_sup_perc_jkjk])
    df_solucion = pd.DataFrame(_lista, columns=['nombre_I', 'origen', 'destino','π_ijkjk','ϕ','π_jkjk'])
    
    solution.solution=df_solucion
    
    # Preparo los df_prob_fi_jkjk y df_fi_ijkjk
    df_solucion['nombre_J'] = df_solucion['origen'].str[:3]
    df_solucion['servicio_K'] = df_solucion['origen'].str[3:]
    df_solucion['nombre_Jp'] = df_solucion['destino'].str[:3]
    df_solucion['servicio_Kp'] = df_solucion['destino'].str[3:]

    # Eliminar la columna 'origen'
    df_solucion.drop(columns=['origen','destino'], inplace=True)
    
    #Como df_solucion no tiene todas las combinaciones de ijkj'k', tengo que completar la matriz
    _lista_I=indices("i",network_repr.I)
    _lista_J=indices("j",network_repr.J)
    _lista_K=indices("k",network_repr.K)
    _lista_completa = np.array([[i, j, k, jp, kp, 0,0,0]
                        for i in _lista_I for j in _lista_J for k in _lista_K for jp in _lista_J for kp in _lista_K])
    _lista_completa = pd.DataFrame(_lista_completa, 
                                   columns=['nombre_I', 
                                            'nombre_J', 
                                            'servicio_K',
                                            'nombre_Jp',
                                            'servicio_Kp',
                                            'π_ijkjk','ϕ','π_jkjk'])
    _lista_completa['π_jkjk'] = _lista_completa['π_jkjk'].astype(float)
    _lista_completa['ϕ'] = _lista_completa['ϕ'].astype(float)
    _lista_completa['π_ijkjk'] = _lista_completa['π_ijkjk'].astype(float)
    
    #_lista_completa.update(df_solucion)
    df_solucion= pd.merge(_lista_completa, df_solucion, on=['nombre_I', 'nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp'],how='left')
    df_solucion['π_ijkjk'] = df_solucion['π_ijkjk_x'] + df_solucion['π_ijkjk_y']
    df_solucion.drop(['π_ijkjk_x', 'π_ijkjk_y'], axis=1, inplace=True)
    df_solucion['π_jkjk'] = df_solucion['π_jkjk_x'] + df_solucion['π_jkjk_y']
    df_solucion.drop(['π_jkjk_x', 'π_jkjk_y'], axis=1, inplace=True)
    df_solucion['ϕ'] = df_solucion['ϕ_x'] + df_solucion['ϕ_y']
    df_solucion.drop(['ϕ_x', 'ϕ_y'], axis=1, inplace=True)
    df_solucion.fillna(0, inplace=True)
    
    #df_solucion=_lista_completa
    #df_solucion['π_jkjk'] = df_solucion['π_jkjk'].astype(float)
    #df_solucion['ϕ'] = df_solucion['ϕ'].astype(float)
    #df_solucion['π_ijkjk'] = df_solucion['π_ijkjk'].astype(float)
    
    df_prob_fi_ijkjk = copy.deepcopy(df_solucion)
    df_prob_fi_ijkjk.drop(columns=['ϕ','π_jkjk'],inplace=True)
    
    df_fi_ijkjk = copy.deepcopy(df_solucion)
    df_fi_ijkjk.drop(columns=['π_ijkjk','π_jkjk'],inplace=True)
    
    df_prob_fi_jkjk = copy.deepcopy(df_solucion)
    df_prob_fi_jkjk.drop(columns=['ϕ','π_ijkjk'],inplace=True)
    df_prob_fi_jkjk = df_prob_fi_jkjk.groupby(
        ['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp']).mean(['π_jkjk'])
    
    solution.df_prob_fi_ijkjk =df_prob_fi_ijkjk 
    solution.df_fi_ijkjk=df_fi_ijkjk
    solution.df_prob_fi_jkjk =df_prob_fi_jkjk 

     # prob_fi_jkjk = fi_jkjk.groupby(
     #     ['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp']).sum(['lambda_ijk'])
     # prob_fi_jkjk['fi_jkjk'] = prob_fi_jkjk['fi_jkjk'] / \
     #     prob_fi_jkjk['lambda_ijk']
     # prob_fi_jkjk.fillna(0, inplace=True)
     # prob_fi_jkjk.reset_index(inplace=True)

    
    solution.state="Solucionado_Solución_Inicial"
    solution.network_repr=network_repr

    # %% Exportar resultados 
    solution.set_solution_excel()
    
    return solution