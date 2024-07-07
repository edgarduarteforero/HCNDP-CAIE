# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:19:25 2024

@author: edgar
"""
import pandas as pd
import numpy as np
from hcndp import network
import copy
from hcndp import local_search
from hcndp import kpi

    
def initial_solution(current_solution,network_original):
    #Creo la representación de la red
    network_repr=network.Network_representation(network_original.I,
                                                network_original.J,
                                                network_original.K,
                                                network_original.archivo,
                                                network_original.file)
    path_repr=network.Path_representation(network_original.K, 
                                          network_original.archivo,
                                          network_original.file)
    
    # Asignación de recurso σ_k para cada nodo de oferta j 
    print ("Construcción de solución inicial")
    for _k in path_repr.nodes_services.keys():
        if _k !=  'k00':
            #print ("Asignación de recursos para: ", _k)
            network_repr.asignacion_recursos(path_repr,_k)
            

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
    current_solution.df_sigma=network_repr.df_sigma
    current_solution.df_sigma = current_solution.df_sigma.rename(columns={'place':'nombre_J', 'service':'servicio_K', 'capac_instal_sigma':'sigma_jk'})


    # Para k=0 creo valores de λ_ijk0 
    # El valor de λ_ijk0 es igual a la demanda que hay en cada nodo ik0.
    for _,_j in network_repr.nodes_supply.items():
        for _p,_i in _j.matriz_λ.iterrows():
            if _i['nombre_I'].replace('i','j')==_i['nombre_J'] and _i['servicio_K']=='k00':
                _j.matriz_λ.loc[_p, 'λ_ijk'] = network_repr.nodes_demand[_i['nombre_I']].demand
    # Construyo primera solución 
    # Ordeno el diccionario de ser_ser_R
    path_repr.edges_ser_ser_R=dict(sorted(path_repr.edges_ser_ser_R.items()))
    
    #print ("Asignación de flujos ijkkp")
    for _i in path_repr.edges_ser_ser_R.values():
        k=_i.source
        kp=_i.target
    
            # Obtengo los delta ijkk
        network_repr.asignacion_flujos_δ(network_repr,path_repr,k,kp) 
        
            # Solución entre k y kp* obtengo los phi ijkjk
        network_repr.solucion_entre_k_kp(network=network_repr,_k=k,
                                             _kp=kp,
                                             archivo=network_original.file,
                                             current_solution=current_solution)
            
            # Obtengo las aproximaciones de lambda
        network_repr.construyo_λ(network_repr,kp)
        
    # Porcentajes de flujo. Obtengo los pi jk jk
    network_repr.obtencion_π(network_repr)
                
    # Construyo una matriz g con los arribos externos, es decir los ϕi.j.k0jk
    from hcndp.data_functions import indices

    _lista_i=indices("i",network_original.I)
    _lista_j=indices("j",network_original.J)
    _lista_k=indices("k",network_original.K)
    
    from itertools import product
    _lista = list(product(_lista_i, _lista_j,_lista_k))
    _g=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
    _g['tao_ijk'] = 0.0
    _g=_g.sort_values(by=['nombre_I', 'nombre_J','servicio_K'])
    current_solution.df_f_ijk=_g
    
    def arribos_externos(poblacion_origen,servicio_origen,nodo_destino):
        suma_acumulativa=0
        for clave,valor in network_repr.edges_sup_sup_X.items():
            if valor.node_demand_pop == poblacion_origen and valor.service_source==servicio_origen and valor.target==nodo_destino :
                suma_acumulativa += valor.flow_sup_sup_phi
        return suma_acumulativa
        
    _g['tao_ijk']=_g.apply(lambda row: arribos_externos(row['nombre_I'],'k00',row['nombre_J']+row['servicio_K']),axis=1)
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
        probs=np.reshape(probs,([network_original.J*(network_original.K),network_original.J*(network_original.K)]))
        _df_asignacion.loc[i,'lambda_ijk']=np.matmul(_g[_fila],np.linalg.inv(np.identity(len(probs))-(probs)))
        _fila+=1
    # Actualizo los valoes de lambda en las matrices en cada nodo oferta
    for _,_j in network_repr.nodes_supply.items():
        if _j.service!='k00':
            _j.matriz_λ=_df_asignacion.loc[(slice(None),_j.place,_j.service),:]
            _j.matriz_λ.reset_index(inplace=True)
            _j.matriz_λ = _j.matriz_λ.rename(columns={'lambda_ijk': 'λ_ijk'})
    
    # Actualizo los delta con base en los nuevos lambda
    #print ("Actualización de flujos ijkkp")
    for _i in path_repr.edges_ser_ser_R.values():
        k=_i.source
        kp=_i.target
    
        # Obtengo los delta ijkk
        
        network_repr.asignacion_flujos_δ(network_repr,path_repr,k,kp) 
        
    # Actualizo los phi con base en los nuevos lambda
    network_repr.solucion_flujos_phi_post_Jackson(network_repr)
            
           
    # Actualizo el df_asignacion en network
    
    current_solution.df_asignacion=_df_asignacion.reset_index()
    network_repr.df_asignacion=_df_asignacion
    current_solution.df_l_jk = network_repr.df_asignacion.groupby(level=['nombre_J', 'servicio_K']).sum()
    current_solution.df_l_jk = current_solution.df_l_jk.rename(columns={'lambda_ijk': 'lambda_jk'})
    current_solution.df_l_jk.reset_index(inplace=True)
    
    # Llevar solución a un df_solucion
    _lista=[] 
    for _i,_j in network_repr.edges_sup_sup_X.items():
        _lista.append([_j.node_demand_pop,
                       _j.source,_j.target,
                       _j.flow_sup_sup_perc_ijkjk,
                       _j.flow_sup_sup_phi,
                       _j.flow_sup_sup_perc_jkjk])
    df_solucion = pd.DataFrame(_lista, columns=['nombre_I', 'origen', 'destino','π_ijkjk','ϕ','π_jkjk'])
    
    current_solution.solution=df_solucion
    
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
    
    df_prob_fi_ijkjk = copy.deepcopy(df_solucion)
    df_prob_fi_ijkjk.drop(columns=['ϕ','π_jkjk'],inplace=True)
    
    df_fi_ijkjk = copy.deepcopy(df_solucion)
    df_fi_ijkjk.drop(columns=['π_ijkjk','π_jkjk'],inplace=True)
    
    df_prob_fi_jkjk = copy.deepcopy(df_solucion)
    df_prob_fi_jkjk.drop(columns=['ϕ','π_ijkjk'],inplace=True)
    df_prob_fi_jkjk = df_prob_fi_jkjk.groupby(
        ['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp']).mean(['π_jkjk'])
    
    df_prob_fi_jkjk=df_prob_fi_jkjk.rename(columns={'π_jkjk':'Probs'})
    
    current_solution.df_prob_fi_ijkjk =df_prob_fi_ijkjk 
    current_solution.df_fi_ijkjk=df_fi_ijkjk
    current_solution.df_prob_fi_jkjk =df_prob_fi_jkjk 
    
    # Calculo los rho para cada nodo jk y lo almaceno en nodes_supply
    for _i,_j in network_repr.nodes_supply.items():
        if _j.service != 'k00':
            if _j.matriz_λ['λ_ijk'].sum() == 0:
                _j.rho=0
            else: 
                _j.rho = _j.matriz_λ['λ_ijk'].sum()/(_j.capac_instal_sigma*_j.rate)

    current_solution.state="Solucionado Solución Inicial"
    current_solution.network_repr=network_repr
    
    local_search.calcular_kpi_local_search(current_solution)

    return current_solution

def fix_initial_solution(current_solution):
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    local_search.calcular_kpi_local_search(current_solution)

    if current_solution.network_copy.file['df_capac']['rho'].max() > 1 == True:
        # Si todavía quedan nodos con rho > 1
        # Construyo modelo de optimización
        current_solution.construct_model()
        
        # Creo el archivo datos.dat
        current_solution.network_copy.create_data_dat()
        
        # Convierto sigma_jk de variable a parámetro
        # _solucion.pyo_model.model_abstract=_solucion.pyo_model.var_sigma_to_param(_solucion.pyo_model.model_abstract)
        current_solution.construct_instance()
        
        # Fijo los nuevos valores de sigma en la instancia
        # Con esta estrategia no tengo que construir un nuevo modelo abstracto
        
        for _i,_j in current_solution.network_repr.nodes_supply.items():
            _new_sigma=_j.capac_instal_sigma
            if _j.service != 'k00':
              current_solution.pyo_model.instance.sigma[_j.place,_j.service].fix(_new_sigma)
        #print (f"Solucionando modelo de optimización para corregir errores")
        current_solution.execute_solver()
    
            
    print ("")
    local_search.calcular_kpi_local_search(current_solution)
            
    return  current_solution


def fix_initial_solution2(current_solution):
    # Corrige la solución inicial existente para evitar que tenga rho > 1
    
    local_search.calcular_kpi_local_search(current_solution)
    
    # Comprobar si las columnas son diferentes donde 'rho' > 1
    def check_conditions(df):
        # Filtrar filas donde 'rho' > 1
        rho_gt_one = df[df['rho'] > 1]
    
        # Verificar si hay diferencias entre 's_jk' y 'sigma_jk'
        return rho_gt_one['s_jk'].ne(rho_gt_one['sigma_jk']).any()
    
    while current_solution.network_copy.file['df_capac']['rho'].max() > 1 and\
        check_conditions(current_solution.network_copy.file['df_capac']): 
            # Mientras que haya algún nodo sobresaturado y existan diferencias entre 's_jk' y 'sigma_jk'


        for _index,_jnode in current_solution.network_repr.nodes_supply.items():
            if _jnode.service != 'k00' and _jnode.rho > 1 and _jnode.capac_instal_disponible != 0: # Identifico elementos con rho > 1
                #print (_i,_j.rho)
                nodo_mayor_congest= _index
                servicio_congest=_jnode.service # Identifico el servicio del elemento congestionado
                menor_congestion=2
                # Identifico el sigma menos congestionado de servicio_congest 
                for _m,_k in  current_solution.network_repr.nodes_supply.items():
                    if _k.service == servicio_congest and _k.rho < menor_congestion and _k.capac_instal_disponible>=1:
                        menor_congestion=_k.rho
                        nodo_menos_congest=_m
                        #print (_m,_k,menor_congestion)
                # Ajusto sigmas entre nodo_mayor_congest y nodo_menor_congest
                current_solution.network_repr.nodes_supply[nodo_mayor_congest].capac_instal_disponible -= 1 
                current_solution.network_repr.nodes_supply[nodo_mayor_congest].capac_instal_sigma += 1
                
                current_solution.network_repr.nodes_supply[nodo_menos_congest].capac_instal_disponible += 1 
                current_solution.network_repr.nodes_supply[nodo_menos_congest].capac_instal_sigma -= 1
                
                # Actualizo los nuevos valores de sigma de network_repr en network_copy > file > df_capac
                for _i,_j in current_solution.network_repr.nodes_supply.items():
                    a = _j.place
                    b = _j.service
                    c = _j.capac_instal_sigma
                
                    fila = current_solution.network_copy.file['df_capac'].query('nombre_J == @a and servicio_K == @b')
                    current_solution.network_copy.file['df_capac'].loc[fila.index, 'sigma_jk'] = c
                    fila = current_solution.df_sigma.query('nombre_J == @a and servicio_K == @b')
                    current_solution.df_sigma.loc[fila.index, 'sigma_jk'] = c
                    
                # Calculo los rho para cada nodo jk y lo almaceno en nodes_supply
                for _i,_j in current_solution.network_repr.nodes_supply.items():
                     if _j.service != 'k00':                                    
                        if _j.matriz_λ['λ_ijk'].sum() == 0:
                            _j.rho=0
                        else: 
                            _j.rho = _j.matriz_λ['λ_ijk'].sum()/(_j.capac_instal_sigma*_j.rate)                        
                
                
                
        local_search.calcular_kpi_local_search(current_solution)

    if current_solution.network_copy.file['df_capac']['rho'].max() > 1 == True:
        # Si todavía quedan nodos con rho > 1
        # Construyo modelo de optimización
        current_solution.construct_model()
        
        # Convierto sigma_jk de variable a parámetro
        # _solucion.pyo_model.model_abstract=_solucion.pyo_model.var_sigma_to_param(_solucion.pyo_model.model_abstract)
        current_solution.construct_instance()
        
        # Fijo los nuevos valores de sigma en la instancia
        # Con esta estrategia no tengo que construir un nuevo modelo abstracto
        
        for _i,_j in current_solution.network_repr.nodes_supply.items():
            _new_sigma=_j.capac_instal_sigma
            if _j.service != 'k00':
             current_solution.pyo_model.instance.sigma[_j.place,_j.service].fix(_new_sigma)
        #print (f"Solucionando modelo de optimización para corregir errores")
        current_solution.execute_solver()

            
    print ("")
    local_search.calcular_kpi_local_search(current_solution)
            
    return  current_solution



# %% <codecell> main
if __name__ == "__main__":

        # Borro carpeta con resultados previos
        from hcndp import data_functions
        import os


        data_functions.borrar_contenido_carpeta(os.getcwd()+'/output/')
        #print("\nContenidos borrados. \nContinuando...")
        
        from hcndp import read_data
        networks_dict={} #Diccionario con las redes utilizadas en el programa
        problems_dict={} #Diccionario con los problemas y las soluciones a la red del programa

        # Indicamos origen de datos y definimos valores I,J,K
        I,J,K= [4,4,4]
        archivo = r"C:\Users\edgar\OneDrive - Universidad Libre\Doctorado\Códigos Python\HcNDP\Health-Care-Network-Design-Problem\hcndp/data/red_original/datos_i16_j10_k10_base.xlsx"
        # Objeto network


        # Creamos un objeto network
        _name="red_original"

        networks_dict[_name] = network.Network(I,J,K,archivo,_name)
        networks_dict[_name].create_folders()
        #print (f"\nSe ha creado exitosamente el objeto {_name}.")


        # Llenar objeto con datos de Excel

        networks_dict[_name].read_file_excel('C:/Users/edgar/OneDrive - Universidad Libre/Doctorado/Códigos Python/HcNDP/Health-Care-Network-Design-Problem/data/red_original/datos_i16_j10_k10_base.xlsx')
        networks_dict[_name].delete_surplus_data()
        networks_dict[_name]=read_data.fix_sigma_max(networks_dict, _name)

        #print ("#" * 60)
        #print (f"\nSe han cargado exitosamente los datos en el objeto {_name}.")
    

        # Creo el objeto solucion
        from hcndp import solutions

        solutions.create_problem_object(networks_dict['red_original'], problems_dict, name_problem="temporal")
        current_solution = problems_dict["temporal"]

        # Defino objetivo y método
        current_solution.optimizar=True
        current_solution.tecnica="Aproximación"
        _objective_and_description =['1', 'Minimizar congestión máxima (rho)']
        #_objective_and_description =['2', 'Maximizar accesibilidad mínima (alpha)']
        #_objective_and_description =['3', 'Maximizar continuidad mínima (delta)']
        current_solution.objective = _objective_and_description[0]
        current_solution.description_objective = _objective_and_description[1]
        current_solution.name_problem = _objective_and_description[1]+" "+current_solution.tecnica
        
        # Actualizo nombre de la solución en solution_dict (Ya no es "temporal")
        _clave_temporal = 'temporal'
        _solucion_temporal = problems_dict[_clave_temporal]
        
        problems_dict[_solucion_temporal.name_problem] = problems_dict.pop(_clave_temporal)
        problems_dict[_solucion_temporal.name_problem].network_copy.name_problem = \
            problems_dict[_solucion_temporal.name_problem].name_problem
        print (f"Se ha actualizado el objeto {problems_dict[_solucion_temporal.name_problem].name_problem}")
        
        # Ejecuto initial solution
        current_solution= initial_solution(current_solution,networks_dict['red_original'])
        local_search.calcular_kpi_local_search(current_solution)
        current_solution= fix_initial_solution(current_solution)

        