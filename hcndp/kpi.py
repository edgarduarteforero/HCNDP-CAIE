# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 12:20:02 2023

@author: edgar
"""

#%% Calcular kpi para una solución

def calculate_kpi(current_solution,_post_optima):    
    import os
    network=current_solution.network_copy
    print (_post_optima)

    set_lambda_jk(current_solution, network,_post_optima)
    set_lambda_ijk(current_solution, network,_post_optima)
    set_phi_ijkjk(current_solution,network)
    set_prop_tao(current_solution,network)
    set_prob_k(current_solution,network)
    
    # Calculo las probabilidades de tener cantidades de clientes y tiempo en cola
    if 'customers' not in network.file:
        print("Uno de los KPI consiste en la probabilidad de tener x clientes o menos en cola.")
        customers = int(input("Ingresa un valor para clientes: \n"))
    
    set_prob_custom_queue(network,customers)
    network.file['customers']=customers
    
    if 'time' not in network.file:
        print("Uno de los KPI consiste en la probabilidad de esperar t o menos tiempo en cola.")
        time = int(input("Ingresa un valor para t: \n"))
        
    set_prob_wait_time (network,time)
    network.file['time']=time
    
    set_kpi_per_node(network)
    set_e2sfca(network)
    set_accessibility_per_node(network)
    set_accessibility_per_service(network)
    set_continuity_per_node(network)
    set_kpi_network(network)
    set_df_grafo_flujo_jkjk(network)
    
    print (f"\nSe han calculado los KPI y se guardaron en {network.name_problem}.")
        

#%% <codecell> Funciones para cálculo de probabilidades por teoría de colas


#########################################

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
# 

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

#%% <codecell> Funciones para congestión



def set_lambda_jk (current_solution, network,_post_optima):
    import numpy as np
    from hcndp.data_functions import reshape_matrix
    import os 
    import pandas as pd


    path=os.getcwd()+'/output/'+current_solution.name_problem+'/salida_optimizacion.xlsx'
        
    
    # Matriz de arribos externos g
    df_asignacion=network.file['df_asignacion']
    # Verificar si las columnas I, J y K están presentes en el índice
    if not all(col in df_asignacion.index.names for col in ['nombre_I', 
                                                            'nombre_J', 
                                                            'servicio_K']):
        # Si no están presentes, establecer las columnas I, J y K como índice
        df_asignacion.set_index(['nombre_I', 'nombre_J', 'servicio_K'], inplace=True)
    df_asignacion = df_asignacion.sort_index(level=[0, 1, 2])
    g=np.array(df_asignacion['tao_ijk']) # Lista de arribos externos ijk
    g=reshape_matrix(g, network.I, network.J*network.K)
    g=np.sum(g,axis=0) #Lista de suma por cada jk. Son los gamma jk
    # Nótese que se hace la suma de los g en el eje 0 para obtener los g_jk a partir de la suma en i de los g_ijk

    # SEGUNDO BLOQUE
    # Cálculo de lambdas y rho para cada par j k
    if _post_optima==False:
        df_capac=network.file['df_capac']
        df_arcos=network.file['df_arcos']
        df_arcos = df_arcos.set_index(['servicio_K','nombre_Jp','servicio_Kp'], append=True)
        df_arcos=df_arcos.sort_index(level=[0,1,2,3])
        probs=df_arcos['p_jjkk']
        probs=reshape_matrix(probs, network.J*network.K, network.J*network.K)
        df_capac['lambdas']=np.matmul(g,np.linalg.inv(np.identity(len(probs))-(probs)))
        df_capac.replace([np.inf,-np.inf], 0, inplace=True)
        df_capac['r']=df_capac['lambdas']/df_capac['c_jk'] #c_jk es la tasa de atención, es decir mu
        df_capac['rho']=df_capac['lambdas']/(df_capac['c_jk']*df_capac['sigma_jk']) # 
        df_capac.replace([np.inf,-np.inf], 0, inplace=True)
        df_capac.fillna(0,inplace=True)
        network.file['df_capac']=df_capac
        print ("\n Se actualizaron exitosamente los lambda_jk")

    if _post_optima==True:
        #TERCER BLOQUE
        ## También puedo importar los datos de lambda_jk desde el archivo datos.xlxs
        #df_capac['lambdas']=pd.read_excel (r'datos.xlsx', sheet_name='df_capac')
        
        data = pd.read_excel (path,sheet_name='l_jk',names=['nombre_J','servicio_K','lambda_jk'],index_col=0)
        
        df_capac=network.file['df_capac']

        #data = path['l_jk']
        df_capac=df_capac.merge(data, on=['nombre_J', 'servicio_K'], how='left')
        #df_capac=df_capac.rename(columns={"lambda_jk": "lambdas"})
        df_capac['lambdas'] = df_capac['lambda_jk']
        df_capac = df_capac.drop(columns=['lambda_jk'])
        df_capac['r']=df_capac['lambdas']/df_capac['c_jk'] #c_jk es la tasa de atención, es decir mu
        
        #Actualizo los sigma
        data = pd.read_excel (path,sheet_name='sigma',names=['nombre_J','servicio_K','sigma_jk'],
                             index_col=0)
        df_capac = df_capac.merge(data, on=['nombre_J', 'servicio_K'], how='left')        
        
        df_capac.drop(['sigma_jk_x'],axis=1,inplace=True)
        df_capac.insert(4,'sigma_jk',df_capac.pop('sigma_jk_y'))
        df_capac['sigma_jk'] = df_capac['sigma_jk'].round(0).astype('int')
        
        df_capac['rho']=df_capac['lambdas']/(df_capac['c_jk']*df_capac['sigma_jk']) # 
        df_capac.fillna(0,inplace=True)
        df_capac.replace([np.inf, -np.inf], 0, inplace=True)
        network.file['df_capac']=df_capac
        
        print ("\n Se actualizaron exitosamente los lambda_jk")
        
def set_lambda_ijk (solution, network,_post_optima):
    import numpy as np
    from hcndp.data_functions import reshape_matrix

    # Calculo los lambdas para cada ijk
    # Se calculan a través de un loop asumiendo que solo hay arribos en cada i
    #g=np.array(network.file['df_asignacion']['tao_ijk']) # Lista de arribos externos ijk
    #g=reshape_matrix(g, network.I, network.J*network.K)# Matriz de arribos externos de i por (jk)    
    df_asignacion=network.file['df_asignacion']
    if not all(col in df_asignacion.index.names for col in ['nombre_I', 
                                                            'nombre_J', 
                                                            'servicio_K']):
        # Si no están presentes, establecer las columnas I, J y K como índice
        df_asignacion.set_index(['nombre_I', 'nombre_J', 'servicio_K'], inplace=True)
    df_asignacion = df_asignacion.sort_index(level=[0, 1, 2])
    g=np.array(df_asignacion['tao_ijk']) # Lista de arribos externos ijk
    g=reshape_matrix(g, network.I, network.J*network.K)# Matriz de arribos externos de i por (jk)    


    # Puedo calcular los lambda ijk basado en redes de Jackson
    #network.file['df_asignacion']["lambda_ijk"] = 0.0
    df_asignacion["lambda_ijk"] = 0.0
    df_arcos=network.file['df_arcos']
    df_arcos = df_arcos.set_index(['servicio_K','nombre_Jp','servicio_Kp'], append=True)
    df_arcos=df_arcos.sort_index(level=[0,1,2,3])
    probs=df_arcos['p_jjkk']
    probs=reshape_matrix(probs, network.J*network.K, network.J*network.K)
    
    #Para cada i calculo el lambda ijk
    _i=0
    
    if _post_optima==False:
        network.file['df_asignacion']=network.file['df_asignacion'].reset_index()
        network.file['df_asignacion']=network.file['df_asignacion'].set_index(['nombre_I','nombre_J','servicio_K'])
        
        network.file['df_asignacion'].sort_index(inplace=True)
        for i in network.file['df_asignacion'].index.levels[0]: 
            #df_asignacion.loc[i,'lambda_ijk']=1
            network.file['df_asignacion'].loc[i,'lambda_ijk']=np.matmul(g[_i],np.linalg.inv(np.identity(len(probs))-(probs)))
            _i+=1    
        print ("\n Se actualizaron exitosamente los lambda_ijk")
    if _post_optima==True:
        network.file['df_asignacion']=network.file['df_asignacion'].reset_index()
        network.file['df_asignacion']=network.file['df_asignacion'].set_index(['nombre_I','nombre_J','servicio_K'])
        network.file['df_asignacion'].sort_index(inplace=True)
        for i in network.file['df_asignacion'].index.levels[0]: 
            #df_asignacion.loc[i,'lambda_ijk']=1
            network.file['df_asignacion'].loc[i,'lambda_ijk']=np.matmul(g[_i],np.linalg.inv(np.identity(len(probs))-(probs)))
            _i+=1
        print ("\n Se actualizaron exitosamente los lambda_ijk")

def set_phi_ijkjk (solution,network):
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
    print ("\n Se actualizaron exitosamente los phi_ijkjk")
   
def set_prop_tao (solution,network):
    # Calculo los valores de prop_tao_ijk. Proporción de clientes que son dirigidos desde ik a jk
    import pandas as pd
    df_demanda=network.file['df_demanda']
    
    if solution.state=="Solucionado_aproximación" or solution.state=="Optimizado":
        #network.file['df_asignacion'] = pd.merge(network.file['df_asignacion'], df_demanda[['nombre_I', 'servicio_K', 'pi_k']], on=['nombre_I', 'servicio_K'], how='left')
        network.file['df_asignacion']=network.file['df_asignacion'].reset_index()
        network.file['df_asignacion']=pd.merge(network.file['df_asignacion'].set_index(['nombre_I','servicio_K']), 
                                               df_demanda.set_index(['nombre_I', 'servicio_K'])['pi_k'], 
                                               left_index=True, right_index=True, how='left')
    else:
        df_demanda=network.file['df_demanda'].drop(['servicio_K'],axis=1)
        network.file['df_asignacion']=pd.merge(network.file['df_asignacion'].reset_index(),df_demanda)
    
    network.file['df_asignacion']['prop_tao_ijk']=network.file['df_asignacion']['tao_ijk']/network.file['df_asignacion']['demanda_i']
    #network.file['df_asignacion'].drop(['demanda_i'],axis=1,inplace=True)
    network.file['df_asignacion']['prop_tao_ijk'] = network.file['df_asignacion']['prop_tao_ijk'].fillna(0)
    print ("\n Se actualizaron exitosamente los tao_ijk (prop)")

def set_prob_k (solution,network):
    # Construyo las probabilidades de estado estable utilizando ecuaciones estacionarias. Son las π_k.
    import numpy as np
    import pandas as pd
    from hcndp.data_functions import indices
    
    data1 = network.file['prob_serv']
    data1=data1.drop(['Unnamed: 0'], axis=1)
    data1=data1.loc[np.arange(network.K)]
    data1=data1[np.arange(network.K)+1]
    data1=np.nan_to_num(data1)
    df_pi_k=data1
    
    # Agrego el estado final (salida del sistema)
    a=[np.zeros(len(df_pi_k))] # Creo una fila para la salida del sistema
    a[0][0]=0.2 #Asigno probabilidad de 0.05 a la primera posición (caso de retorno a medicina general)
    df_pi_k=np.append(df_pi_k,a,axis=0)
    
    a=[] 
    for i in df_pi_k:
        a.append(1-sum(i))
    a=np.array(a).reshape(len(a), 1)
    df_pi_k=np.append(df_pi_k,a,axis=1)
    
    df_pi_k=np.identity(len(df_pi_k))-df_pi_k.transpose()
    df_pi_k=np.vstack([df_pi_k,np.ones(len(df_pi_k))])
    
    f=np.append(np.zeros([1,len(df_pi_k)-1]),[1])
    
    df_pi_k=df_pi_k[1:]
    
    f=f[1:]
    
    df_pi_k=pd.DataFrame(np.linalg.solve(df_pi_k,f),columns=['pi_k'])
    df_pi_k['servicio_K']=indices("k",network.K+1)
    df_pi_k=df_pi_k[:-1]
    
    df_demanda=network.file['df_demanda']
    df_demanda=df_demanda.drop(['servicio_K'], axis=1)
    df_demanda = df_demanda.loc[:, ~df_demanda.columns.str.startswith('index')] #Elimino columnas con texto "index"
    df_demanda=pd.merge(df_demanda.reset_index(),df_pi_k.reset_index(),how="cross")
    
    #Si voy a utilizar probabilidades de estado estable para definir la demanda en la red habilito esta línea
    #df_demanda['h_ik']=df_demanda['demanda_i']*df_demanda['pi_k']
    
    #De lo contrario asumo que la demanda_i es la misma h_ik. siempre debo usar axis=1 cuando recorro un dataframe por filas
    df_demanda['h_ik']=df_demanda.apply (lambda row: row['demanda_i'] if row['servicio_K']=='k01' else "0",axis=1) 
    if solution.state=="Solucionado_aproximación" or solution.state=="Optimizado":
        print ("Ya está preparada la matriz df_demanda.")
    else:
        print ("Actualizo df_demanda.")
        network.file['df_demanda']=df_demanda
    print ("\n Se actualizaron exitosamente las demandas en estado estable df_pi.")


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

#%% <codecell> Funciones para accesibilidad

def set_e2sfca(network):
    import pandas as pd
    import numpy as np 
    
    df_asignacion=network.file['df_asignacion'].reset_index()
    df_capac=network.file['df_capac'].reset_index()
    df_capac=df_capac.set_index(['nombre_J','servicio_K'])
    df_demanda = network.file['df_demanda']
    
    # Calculo los numeradores
    # Hay un 'Sff' por cada combinación ijk
    df_asignacion['Sff']=df_asignacion['sigma_jk']*df_asignacion['f_dij'] #*df_asignacion['c_jk']
    
    # Calculo el denominador como el producto de la demanda y las distancias gaussianas
    # Hay un 'Pf' por cada combinación ijk
    df_asignacion=pd.merge(df_asignacion,df_demanda[['nombre_I','servicio_K','demanda_i']])
    df_asignacion['Pf']=df_asignacion['lambda_ijk']*df_asignacion['f_dij'] 
    
    # Los denominadores son sumatorias dejando fijos k y j y modificando i. 
    df_asignacion=pd.merge(df_asignacion.groupby(['servicio_K','nombre_J']).Pf.sum(),df_asignacion,on=['servicio_K','nombre_J'],how='left')
    df_asignacion=df_asignacion.rename(columns={"Pf_x":"Pf_grup","Pf_y":"Pf"})
    
    # Calculo las accesibilidades R de cada combinación i j k
    
    df_asignacion['R']=df_asignacion['Sff']*(df_asignacion['lambda_ijk']!=0)*100/df_asignacion['Pf_grup']
    df_asignacion.fillna(0,inplace=True)
    df_asignacion.replace([np.inf, -np.inf], 0, inplace=True)
    
    # Agrupo las accesibilidades por cada cliente y servicio K
    df_accesibilidad=df_asignacion.groupby(['nombre_I','servicio_K']).R.sum()
    df_demanda=pd.merge(df_demanda,df_accesibilidad,on=['nombre_I','servicio_K'],how='left')
    df_demanda=df_demanda.rename(columns={"R":"acces_H2SFCA"})
    
    #Agrego las demandas a df_accesibildiad
    df_accesibilidad=pd.merge(df_accesibilidad.reset_index().set_index('nombre_I'),df_demanda.groupby(['nombre_I']).demanda_i.sum(),left_on=['nombre_I'],right_on='nombre_I').set_index(['servicio_K'],append=True)
    df_accesibilidad['Acc_ponderado']=df_accesibilidad['R']*df_accesibilidad['demanda_i']
    
    network.file['df_demanda']=df_demanda
    network.file['df_asignacion']=df_asignacion
    network.file['df_accesibilidad']=df_accesibilidad
    
def set_accessibility_per_node(network):
    import pandas as pd    
    # Calculo accesibilidad para cada nodo de demanda i
    
    df_demanda=network.file['df_demanda']
    df_asignacion=network.file['df_asignacion']
    #Calculo la accesibilidad ponderada por la población (lambdas) para cada i
    #Equivale a Acc_ik*lambda_ik / sum_lambda_ik
    df_demanda=pd.merge(df_demanda.set_index(['nombre_I','servicio_K']),
                        df_asignacion.groupby(['nombre_I','servicio_K']).sum(numeric_only=True)['lambda_ijk'],
                        left_index=True,right_index=True)
    df_demanda['weighted']=df_demanda['acces_H2SFCA']*df_demanda['lambda_ijk']/df_demanda.groupby('nombre_I').lambda_ijk.sum()
    
    #En el paso anterior se calcularon accesibilidades ponderadas por la población. 
    #La suma de estas accesibilidades dará el promedio ponderado de accesibilidades.
    prueba=pd.merge(df_demanda,df_demanda.groupby('nombre_I')['weighted'].sum(),left_index=True,right_index=True)
    df_demanda['weighted']=prueba['weighted_y']
    
    network.file['df_demanda']=df_demanda
    #prueba contendrá la accesibilidad obtenida para cada nodo demanda i
    prueba=df_demanda.groupby('nombre_I')['weighted'].mean()    
    network.file['df_acces_node']=prueba
    network.file['df_acces_node'].name='Access_by_node'

def set_accessibility_per_service(network):
    import pandas as pd
    
    df_demanda=network.file['df_demanda']
    # Calculo accesibilidad para cada servicio k
    
    #Calculo la accesibilidad ponderada por la población (lambdas) para cada k
    #Equivale a Acc_ik*lambda_ik / sum_lambda_ik
    df_demanda['weighted_k']=df_demanda['acces_H2SFCA']*df_demanda['lambda_ijk']/df_demanda.groupby('servicio_K').lambda_ijk.sum()
    
    #En el paso anterior se calcularon accesibilidades ponderadas por la población. 
    #La suma de estas accesibilidades dará el promedio ponderado de accesibilidades.
    prueba=pd.merge(df_demanda,df_demanda.groupby('servicio_K')['weighted_k'].sum(),left_index=True,right_index=True)
    df_demanda['weighted_k']=prueba['weighted_k_y']
    
    network.file['df_demanda']=df_demanda
    #prueba contendrá la accesibilidad obtenida para cada servicio k
    prueba=df_demanda.groupby('servicio_K')['weighted_k'].mean()
    network.file['df_acces_service']=prueba
    network.file['df_acces_service'].name='Access_by_service'
    

def set_accessibility_network(network):
    df_demanda=network.file['df_demanda']
    df_demanda['h_ik'] = df_demanda['h_ik'].astype(int)
    #prueba=df_demanda['lambda_ijk']*df_demanda['acces_H2SFCA']/df_demanda['lambda_ijk'].sum()
    prueba=df_demanda['demanda_i']*df_demanda['acces_H2SFCA']/(df_demanda['demanda_i'].sum())
    #print ("Accesibilidad total=",prueba.sum())
    network.file['df_medidas']['Alpha_total']= [prueba.sum()]

#%% <codecell> Funciones para continuidad

def set_continuity_per_node(network):
    import pandas as pd 
    
    
    df_asignacion=network.file['df_asignacion'].copy()
    df_asignacion['gamma_ijk']= df_asignacion['lambda_ijk'].apply(lambda x: 1 if x != 0 else 0)

    #Calculo los delta_ij
    df_asignacion=pd.merge(df_asignacion,df_asignacion.groupby(['nombre_I','nombre_J']).gamma_ijk.sum(),on=['nombre_I','nombre_J'],how='left')
    df_asignacion=df_asignacion.rename(columns={"gamma_ijk_x":"gamma_ijk","gamma_ijk_y":"delta_ij"})
    
    #Calculo delta para cada i 
    df_continuidad=df_asignacion[['nombre_I','nombre_J','demanda_i','delta_ij']].drop_duplicates()
    df_continuidad['delta_ij']= df_continuidad['delta_ij'].apply(lambda x: 1 if x != 0 else 0)
    
    df_continuidad=pd.merge(df_continuidad,df_continuidad.groupby(['nombre_I']).delta_ij.sum(),on=['nombre_I'],how='left')
    df_continuidad=df_continuidad.rename(columns={"delta_ij_x":"delta_ij","delta_ij_y":"delta_i"})
    df_continuidad=df_continuidad.drop_duplicates(subset = ['nombre_I']).drop(['delta_ij'], axis=1)
    df_continuidad['delta_i']=network.J-df_continuidad['delta_i']
    network.file['df_continuidad']=df_continuidad


#%% <codecell> Funciones para medidas globales

def set_kpi_network(network):    
    import pandas as pd    
    import numpy as np
    
    df_capac=network.file['df_capac'].copy()
    df_continuidad=network.file['df_continuidad'].copy()
    df_accesibilidad=network.file['df_accesibilidad'].copy()
    df_demanda=network.file['df_demanda'].copy()
           
    df_medidas=pd.DataFrame()
    df_medidas['Wtotal']=[df_capac['L'].sum()/df_capac['Sum_tao_ij'].sum()]
    df_medidas['Wqtotal']= [df_capac['L_q'].sum()/df_capac['Sum_tao_ij'].sum()]
    df_medidas['Ltotal']= [df_capac['L'].sum()]
    df_medidas['Lqtotal']= [df_capac['L_q'].sum()]

    df_medidas['Delta_total']= [np.average(a=df_continuidad['delta_i'], weights=df_continuidad['demanda_i'])]
    
    df_medidas['rho_max']= [df_capac['rho'].max()]
    df_medidas['alpha_min']= [df_accesibilidad['R'].min()]
    df_medidas['delta_min']=[df_continuidad['delta_i'].min()]


    #df_demanda['h_ik'] = df_demanda['h_ik'].astype(int)
    #prueba=df_demanda['lambda_ijk']*df_demanda['acces_H2SFCA']/df_demanda['lambda_ijk'].sum()
    prueba=df_demanda['demanda_i']*df_demanda['acces_H2SFCA']/(df_demanda['demanda_i'].sum())
    df_medidas['Alpha_total']= [prueba.sum()]


    network.file['df_medidas']=df_medidas

def set_df_grafo_flujo_jkjk(network):
    import pandas as pd 

    df_grafo=network.file['df_arcos'].reset_index().copy()
    df_capac=network.file['df_capac'].copy()
    df_flujos_jj=network.file['df_flujos_jj'].copy()
    df_probs_kk=network.file['df_probs_kk'].copy()
    df_arcos=network.file['df_arcos'].copy()
    df_capac=network.file['df_capac'].reset_index().copy()
    df_capac.set_index(['nombre_J','servicio_K'],inplace=True)
    df_capac['t_jk']=df_capac.apply (lambda row: 1 if row['s_jk*c_jk']>0 else 1, axis=1)
    
    df_grafo = df_grafo.loc[df_grafo['p_jjkk'] != 0]
    df_grafo['jk']= df_grafo['nombre_J']+df_grafo['servicio_K']
    df_grafo['jpkp']= df_grafo["nombre_Jp"]+df_grafo['servicio_Kp']
    
    df_temporal=pd.merge(df_capac['lambdas'],df_arcos,on=["nombre_J",'servicio_K'],how="left")
    df_temporal['lambdas*probs']=df_temporal['lambdas']*df_temporal['p_jjkk']
    df_temporal=df_temporal.reset_index()
    df_temporal['jk_origen']=df_temporal['nombre_J']+df_temporal['servicio_K']
    df_temporal['jk_destino']=df_temporal['nombre_Jp']+df_temporal['servicio_Kp']
    df_grafo=df_temporal.reset_index()
    df_grafo = df_grafo.loc[df_grafo['lambdas*probs'] != 0]
    
    network.file['df_grafo']=df_grafo
    network.file['df_flujos_jkjk']=df_temporal
    df_flujos_jkjk=network.file['df_flujos_jkjk']

    #Hago el merge para t_jk
    df_flujos_jkjk=pd.merge(df_flujos_jkjk,df_capac['t_jk'],left_on=['nombre_Jp','servicio_Kp']
                  ,right_on=['nombre_J','servicio_K'],how='left')
    df_flujos_jkjk=pd.merge(df_flujos_jkjk,df_flujos_jj,left_on=['nombre_J','nombre_Jp'],right_on=['nombre_J','nombre_Jp'], how='left')
    df_flujos_jkjk=pd.merge(df_flujos_jkjk,df_probs_kk,left_on=['servicio_K','servicio_Kp'],right_on=['servicio_K','servicio_Kp'], how='left')
    df_flujos_jkjk['p_kkp_True_False']=df_flujos_jkjk['p_kkp']>0 # Flujos posibles
    df_flujos_jkjk['p_jjkk_True_False']=df_flujos_jkjk['p_jjkk']>0 #Flujos asignados
    network.file['df_flujos_jkjk']=df_flujos_jkjk

#%% <codecell> Main    
if __name__ == "__main__":
    import hcndp
    from hcndp import network_data
    from hcndp.read_data import read_file_excel
    from hcndp.network_data import _I,_J,_K,_archivo 
    from hcndp.figures import figure_network_cartesian
    import os
    
    network=network_data.Network(_I,_J,_K,_archivo)
    path=os.path.dirname(os.getcwd())+'/data/'+network.name+'/'+network.archivo
    read_file_excel(network,path)
    #read_data.read_parameters(network)
    read_file_excel(network,path)
    hcndp.read_data.delete_surplus_data(network)
    hcndp.read_data.merge_niveles_capac(network)
    hcndp.read_data.create_df_asignacion(network)
    hcndp.read_data.create_df_probs_kk(network)
    hcndp.read_data.create_df_arcos(network)