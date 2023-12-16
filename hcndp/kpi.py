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
    network.file['df_asignacion'].sort_index(inplace=True)
    for i in network.file['df_asignacion'].index.levels[0]: 
        #df_asignacion.loc[i,'lambda_ijk']=1
        network.file['df_asignacion'].loc[i,'lambda_ijk']=np.matmul(g[_i],np.linalg.inv(np.identity(len(probs))-(probs)))
        _i+=1

def set_phi_ijkjk (network):
    #Calculo flujos fi_ijkjk cuando estoy usando escenario 1. Estos fi vienen de lambda según la fórmula de abajo:
    # l_ijk*p_jjkk*x_jj
        
    # Construyo df_fi_ijkjk a partir de los lambda_ijk que se han calculado
    #Para cada i hago lo siguiente
    #Multiplico l_ijk*p_jjkk|*x_jj
    
    import pandas as pd
    network.file['df_flujos_ijkjk']=pd.merge(network.file['df_asignacion'][['lambda_ijk']], 
                               network.file['df_probs_kk'][['servicio_K','servicio_Kp','p_kkp']].set_index(['servicio_K','servicio_Kp']),
                               left_index=True, right_index=True)
    
    network.file['df_flujos_ijkjk']=pd.merge(network.file['df_flujos_ijkjk'], 
                               network.file['df_flujos_jj'].set_index(['nombre_J','nombre_Jp']),
                               left_index=True, right_index=True)
    
    network.file['df_flujos_ijkjk']=pd.merge(network.file['df_flujos_ijkjk'], 
                               network.file['df_arcos'].reset_index()[['nombre_J','nombre_Jp','servicio_K','servicio_Kp','p_jjkk']].set_index(['nombre_J','nombre_Jp','servicio_K','servicio_Kp']),
                               left_index=True, right_index=True)
        
    network.file['df_flujos_ijkjk']['fi_ijkjk']=network.file['df_flujos_ijkjk']['lambda_ijk']*network.file['df_flujos_ijkjk']['p_jjkk']*network.file['df_flujos_ijkjk']['x_jjp']
    
    network.file['df_flujos_ijkjk'] = network.file['df_flujos_ijkjk'].reorder_levels(['nombre_I', 'nombre_J', 'servicio_K','nombre_Jp', 'servicio_Kp'])
        
def set_prop_tao (network):
    # Calculo los valores de prop_tao_ijk. Proporción de clientes que son dirigidos desde ik a jk
    import pandas as pd
    
    network.file['df_asignacion']=pd.merge(network.file['df_asignacion'].reset_index(),
                                           network.file['df_demanda'])
    network.file['df_asignacion']['prop_tao_ijk']=network.file['df_asignacion']['tao_ijk']/network.file['df_asignacion']['demanda_i']
    network.file['df_asignacion'].drop(['demanda_i'],axis=1,inplace=True)
    network.file['df_asignacion']['prop_tao_ijk'] = network.file['df_asignacion']['prop_tao_ijk'].fillna(0)


#########################################
# Funciones para cálculo de probabilidades por teoría de colas

def p_0(sum_y,s,c): #Probabilidad de estado 0
    import math
    s=int(s)
    r = (c) and sum_y / (c) or 0 # Division by zero equals zero
    rho = (s*c) and sum_y / (s*c) or 0 # Division by zero equals zero
    p=((r)**s)/((1-rho)*math.factorial(s))
    suma = sum([((r)**j)/(math.factorial(j)) for j in range (int(s))])
    p=1/(p+suma)
    return p

def p_f1(p_0,sum_y,s,c,f): #Probabilidad de estado f<=s
    import math
    import sys    
    s=int(s)
    r = (c) and sum_y / (c) or 0 # Division by zero equals zero
    rho = (s*c) and sum_y / (s*c) or 0 # Division by zero equals zero
    rho = rho -sys.float_info.epsilon #Resto epsilon para no tener rho=1
    p=p_0*((r)**f)/math.factorial(f)
    return p

def p_f2(p_0,sum_y,s,c,f): #Probabilidad de estado f>s
    import sys 
    import math
    rho = (s*c) and sum_y / (s*c) or 0 # Division by zero equals zero
    rho = rho -sys.float_info.epsilon #Resto epsilon para no tener rho=1
    r = (c) and sum_y / (c) or 0 # Division by zero equals zero
    p=p_0*((r)**f)/(math.factorial(s)*(s**(f-s)))
    return p

def p_total(sum_y,s,c,f): #Suma de probabilidades en estado estable hasta un estado f
    #Se interpreta como la probabilidad de tener f o menos personas en el sistema
    s=int(s)
    p_total=0
    p__0=p_0(sum_y,s,c)
    if sum_y<=(s*c) and (s*c)!=0: #Valido que se pueda calcular p_total
        for i in range(int(f+1)):
            if i==0:
                p_total+=p__0
                
            elif 0<i<s:
                p_total+=p_f1(p__0,sum_y,s,c,i)
                
            elif i>=s:
                p_total+=p_f2(p__0,sum_y,s,c,i)
                
    else:
        p_total=float('NaN')
    return p_total

def p_wqt(sum_y,s,c,t):
    
    import sys
    import math
    rho = (s*c) and sum_y / (s*c) or 0 # Division by zero equals zero
    rho = rho -sys.float_info.epsilon #Resto epsilon para no tener rho=1
    if rho < 1 and (s*c)!=0 : #Valido que se pueda calcular p_total
        p__0=p_0(sum_y,s,c)   
        r = (c) and sum_y / (c) or 0 # Division by zero equals zero
        p_wqt=math.exp(-(s*c-sum_y)*t)
        s=int(s)
        p_wqt=1-(r**s)*p__0*p_wqt/(math.factorial(s)*(1-rho))
    else:
        
        p_wqt=float('NaN')
    return p_wqt


def L_q(r,rho,s,c,p_o):
    import math
    s=int(s)
    Lq=((r**s)*rho/(math.factorial(s)*(1-rho)**2))*p_o
    return Lq

def W_q(L_q,lambdas,rho):
    import pandas as pd
    if pd.isna(L_q) or lambdas==0: #Valido que se pueda calcular p_total
       W_q=float('NaN')
    else:
       W_q=L_q/lambdas
    return W_q

##########################################

def set_prob_custom_queue (network,customers):
    # Cálculo de probabilidades Pbjk en estado estable para MMs
    # Consiste en la probabilidad de encontrar b o menos usuarios en cola
    #sum_y=tasa de arribos
    #s=número de servidores
    #c=tasa de servicio de cada servidor
    import pandas as pd

    # Creo una columna en df_capac con las demandas asignadas sum tao_ij
    network.file['df_capac']=network.file['df_capac'].reset_index().set_index(['nombre_J','servicio_K'])
    network.file['df_capac']=(pd.merge(network.file['df_capac'],network.file['df_asignacion'].groupby(['nombre_J','servicio_K']).tao_ijk.sum(),
                       left_index=True,
                       right_index=True,how='outer').fillna(0)) 
    network.file['df_capac'].rename(columns = {'tao_ijk':'Sum_tao_ij'}, inplace = True)
    
    #Calculo la probabilidad de tener b clientes o menos en cola
    network.file['df_capac']['prob_b'+str(customers)]=network.file['df_capac'].apply(lambda row: p_total(row["lambdas"],row["sigma_jk"],row["c_jk"],customers),axis='columns')
    
    #Calculo la probabilidad de tener cero clientes en espera en cola
    network.file['df_capac']['prob_b'+str(0)]=network.file['df_capac'].apply(lambda row: p_total(row["lambdas"],row["sigma_jk"],row["c_jk"],0),axis='columns')
    

def set_prob_wait_time (network,t):
    # Cálculo de probabilidades Ptjk en estado estable para MMs
    # Consiste en la probabilidad de tener que esperar t o menos unidades de tiempo en cola
    # Detallamos el valor de t
    
    network.file['df_capac']['prob_t'+str(t)]=network.file['df_capac'].apply(lambda row: p_wqt(row["lambdas"],row["sigma_jk"],row["c_jk"],t),axis='columns')    

def set_kpi_per_node(network):
    df_capac=network.file['df_capac']
    df_capac['L_q']=df_capac.apply(lambda row: L_q(row["r"],row["rho"],row["sigma_jk"],row["c_jk"],row["prob_b0"]),axis='columns')
    df_capac['W_q']=df_capac.apply(lambda row: W_q(row["L_q"],row["lambdas"],row['rho']),axis='columns')
    df_capac['L']=df_capac['L_q']+df_capac['r']
    df_capac['W']=df_capac['W_q']+1/(df_capac['sigma_jk']+df_capac['c_jk'])

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