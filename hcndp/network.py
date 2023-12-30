# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 12:33:35 2023

@author: edgar
"""

# <codecell> Clase network
class Network:
    def __init__(self,I,J,K,archivo,name):
        self.I=I
        self.J=J
        self.K=K
        self.archivo=archivo
        self.name=name
        
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
        
    def read_file_excel(self,path):
        print ("Leyendo datos del archivo de Excel.")
        import pandas as pd
        import os
        self.file = pd.read_excel(path, sheet_name=None)
    
    
    def delete_surplus_data(self):
        from hcndp.data_functions import indices
        
        items=indices("i",self.I)
        self.file['df_demanda']=self.file['df_demanda'].query('nombre_I in @items')
        self.file['df_dist_ij']=self.file['df_dist_ij'].query('nombre_I in @items')
        self.file['df_w_ij']=self.file['df_w_ij'].query('nombre_I in @items')
        self.file['df_flujos_ijk']=self.file['df_flujos_ijk'].query('nombre_I in @items')
    
        items=indices("j",self.J)
        self.file['df_oferta']=self.file['df_oferta'].query('nombre_J in @items')
        self.file['df_capac']=self.file['df_capac'].query('nombre_J in @items')
        self.file['df_dist_ij']=self.file['df_dist_ij'].query('nombre_J in @items')
        self.file['df_w_ij']=self.file['df_w_ij'].query('nombre_J in @items')
        self.file['df_flujos_ijk']=self.file['df_flujos_ijk'].query('nombre_J in @items')
    
        items=indices("k",self.K)
        self.file['df_niveles']=self.file['df_niveles'].query('servicio_K in @items')
        self.file['df_capac']=self.file['df_capac'].query('servicio_K in @items')
        self.file['df_flujos_ijk']=self.file['df_flujos_ijk'].query('servicio_K in @items')
        self.file['df_sigma_max']=self.file['df_sigma_max'].query('servicio_K in @items')
    
    
    def merge_niveles_capac(self,_post_optima):
        #Agrego las columna nivel de atención y ubicaciones
        import pandas as pd
        import os
        
        self.file['df_capac']=pd.merge(self.file['df_capac'],self.file['df_niveles'],on='servicio_K',how='left')
        self.file['df_capac']=pd.merge(self.file['df_capac'],self.file['df_oferta'],on='nombre_J',how='inner')
        self.file['df_capac']=self.file['df_capac'].set_index(['nombre_J','servicio_K'],drop=True)
        
        if _post_optima==True:
            output_file=os.getcwd()+'/output/'+self.name+'/salida_optimizacion.xlsx'
    
            data = pd.read_excel (output_file,sheet_name='sigma',names=['nombre_J','servicio_K','sigma_jk'],
                                     index_col=0)
            self.file['df_capac']= pd.merge(self.file['df_capac'],data.set_index(['nombre_J','servicio_K']),left_index=True,right_index=True)
        
            self.file['df_capac'].drop(['sigma_jk_x'],axis=1,inplace=True)
            self.file['df_capac'].insert(4,'sigma_jk',self.file['df_capac'].pop('sigma_jk_y'))
            
            self.file['df_capac']['sigma_jk'] = self.file['df_capac']['sigma_jk'].round(0).astype('int')
        
        if _post_optima==False:   
            if self.file['df_capac']['s_jk'].sum() < self.file['df_capac']['sigma_jk'].sum():
                print ("""Hay un error en la capacidad.
                       La suma de los s_jk es menor a la suma de los sigma_jk asignados.
                       """)
                raise SystemExit("Stop right there!")
            
    def create_df_asignacion(self,_post_optima):
        import pandas as pd
        from hcndp.data_functions import decay_gauss
        import os
        from hcndp.data_functions import indices
        import numpy as np
    
        
        # Creo la matriz df_asignación para construir los arcos de la red
        # En la matriz df_asignacion creamos las columnas para incorporar la función de decaimiento de la distancia
        self.file['df_asignacion']=pd.DataFrame()
        self.file['df_asignacion']=self.file['df_capac'].reset_index().set_index('nombre_J')
    
        #Fusiono matrices de oferta y distancia creando arcos
        self.file['df_asignacion']=pd.merge(self.file['df_asignacion'], 
                                               self.file['df_dist_ij'].set_index(['nombre_J']),
                                               left_index=True,right_index=True,how='outer').sort_values('dist_IJ').reset_index()
        
        #Creo una matriz con las distancias de cobertura que se digitaron como parámetros
        self.file['df_asignacion']=pd.merge(self.file['df_asignacion'], 
                                               self.file['df_demanda'].reset_index()[['nombre_I','ubicacionesI_x','ubicacionesI_y']],
                                               on='nombre_I',how='inner').drop_duplicates()
         
        # Calculo las distancias ajustadas por la función de decaimiento con el título f_dij
        self.file['df_asignacion']['f_dij']=self.file['df_asignacion'].apply(lambda row: decay_gauss(row["dist_IJ"],row["d_o_k"]),axis='columns')
        self.file['df_asignacion']=self.file['df_asignacion'].set_index(['nombre_J','servicio_K'])
    
        self.file['df_flujos_ijk']=self.file['df_flujos_ijk'].set_index(['nombre_I','nombre_J','servicio_K']).sort_index()
        self.file['df_asignacion']=self.file['df_asignacion'].drop(['tao_ijk','z_ijk'], axis=1, errors='ignore')
        self.file['df_asignacion']=self.file['df_asignacion'].reset_index()
        self.file['df_asignacion']=self.file['df_asignacion'].set_index(['nombre_I','nombre_J','servicio_K'])
        self.file['df_asignacion']=pd.merge(self.file['df_asignacion'], self.file['df_flujos_ijk'],left_index=True, right_index=True)
    
        if _post_optima == True:
            # Cargo los resultados obtenidos de la optimización
            path=os.getcwd()+'/output/'+self.name+'/salida_optimizacion.xlsx'
            archivo_salida_optim = pd.read_excel(path, sheet_name=None)
    
            self.file['df_flujos_ijk']=archivo_salida_optim['f_ijk']
            self.file['df_fi_ijkjk'] = archivo_salida_optim['fi_ijkjk']
            
            # Elimino los flujos que no quiero contemplar en el ejercicio
            delete_surplus_data(self)
            
            # Creo la variable z_ijk que tiene valores 1 o 0
            df_flujos_ijk=self.file['df_flujos_ijk'].copy()
            df_flujos_ijk['z_ijk']= np.where(df_flujos_ijk['tao_ijk']!=0, 1,0)
            df_flujos_ijk=df_flujos_ijk.set_index(['nombre_I','nombre_J','servicio_K']).sort_index()
            
            # Creo copias de df_asignacion y df_w_ij
            df_asignacion=self.file['df_asignacion'].copy()
            df_w_ij=self.file['df_w_ij'].copy()
            
            # Actualizo df_asignacion
            df_asignacion=df_asignacion.reset_index(level=['servicio_K']).\
                        merge(df_w_ij.set_index(['nombre_I','nombre_J']),
                              left_index=True,right_index=True).rename(columns={"w_ij": "Flujo_w_ij"})
            df_asignacion=df_asignacion.reset_index()
            df_asignacion=df_asignacion.set_index(['nombre_I','nombre_J','servicio_K'])
            df_asignacion=df_asignacion.drop(['tao_ijk','z_ijk'], axis=1, errors='ignore')
            df_asignacion=pd.merge(df_asignacion, df_flujos_ijk,left_index=True, right_index=True)
            self.file['df_asignacion']=df_asignacion
            self.file['df_flujos']=df_flujos_ijk
    
    
    def create_df_probs_kk(self):
        import numpy as np
        import pandas as pd
        from hcndp.data_functions import indices
        
        # Obtengo las probabilidades de transferencia entre servicios y lo covierto en un df kk'
        data1 = self.file['prob_serv']
        data1=data1.drop(['Unnamed: 0'], axis=1)
        data1=data1.loc[np.arange(self.K)]
        data1=data1[np.arange(self.K)+1]
        data1=np.nan_to_num(data1) 
        
        # Obtengo los flujos habilitados entre j y j'
        data2 = self.file['flujos_jj']
        data2=data2.loc[np.arange(self.J)]
        data2=data2.iloc[:,np.arange(self.J)+1]
        data2=np.nan_to_num(data2) 
        
        #Convierto data1 a un dataframe con títulos
        self.file['df_probs_kk'] = pd.DataFrame(data = data1, 
                                                   index = indices("k",self.K), 
                                                   columns = indices("k",self.K))
        self.file['df_probs_kk'] = self.file['df_probs_kk']. \
                                    melt(ignore_index=False).reset_index(). \
                                    rename(columns={"index": "servicio_K", "variable": "servicio_Kp","value":"p_kkp"})
        self.file['df_probs_kk']['bin']=(self.file['df_probs_kk']['p_kkp']!=0).astype(int)
        
        #Convierto data2 a un dataframe con títulos
        self.file['df_flujos_jj'] = pd.DataFrame(data = data2, index = indices("j",self.J), 
                                                    columns = indices("j",self.J))
        self.file['df_flujos_jj'] = self.file['df_flujos_jj'].\
                                    melt(ignore_index=False).\
                                    reset_index().\
                                    rename(columns={"index": "nombre_J", "variable": "nombre_Jp","value":"x_jjp"})
    
    
    def create_df_arcos(self,_post_optima): 
        # Creo df_arcos con los índices de j y de k. Es un df con [j j' k k']
        # Explicación en p- 9B Notas del doctorado
        from hcndp.data_functions import indices
        import pandas as pd
        import numpy as np
        import os
        
        lista=[]
        j=indices("j",self.J)
        k=indices("k",self.K)
        for a in j:
          for b in j:
            for c in k: # range (1,K+1):
              for d in k: #range(1,K+1):
                lista.append([a,c,b,d])
        
        self.file['df_arcos']=pd.DataFrame(lista,columns=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'])
        self.file['df_arcos'].sort_values(by=['nombre_J','servicio_K'], inplace=True)
    
        
        if _post_optima==True:
            path=os.getcwd()+'/output/'+self.name+'/salida_optimizacion.xlsx'
            archivo_salida_optim = pd.read_excel(path, sheet_name=None)
            data = archivo_salida_optim['prob_fi_jkjk']
            #data = pd.read_excel (archivo, sheet_name='df_probs')
            #data = pd.read_excel('/content/drive/MyDrive/Colab Notebooks/FLNDP/datos.xlsx',sheet_name='probs')
            data= data.drop(['Unnamed: 0'], axis=1)
            #data= data.drop(['Unnamed: 1'], axis=1)
            #data= data.drop(index=0)
            #probs = np.array(data)
             
            probs=data.loc[:]['Probs'].to_numpy().reshape(self.J*self.K,self.J*self.K)
        
    
        if _post_optima==False:
    
            
            # self.file['df_arcos']=pd.DataFrame(lista,columns=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'])
            # self.file['df_arcos'].sort_values(by=['nombre_J','servicio_K'], inplace=True)
            
            # Construyo la matriz a partir de las probabilidades de transferencia entre servicios kk' y 
            # los flujos habilitados jj'
            # Obtengo las probabilidades de transferencia entre servicios y lo covierto en un df kk'
            data1 = self.file['prob_serv'].drop(['Unnamed: 0'], axis=1)
            data1 = data1.loc[np.arange(self.K)]
            data1 = data1[np.arange(self.K)+1]
            data1 = np.nan_to_num(data1) 
        
            # Obtengo los flujos habilitados entre j y j'
            data2 = self.file['flujos_jj']
            data2=data2.loc[np.arange(self.J)]
            data2=data2.iloc[:,np.arange(self.J)+1]
            data2=np.nan_to_num(data2) 
        
            # Construyo una matriz con las probabilidades 
            matriz=self.file['df_capac'].loc[:]['sigma_jk'].to_numpy().reshape(self.J,self.K) #Matriz con los valores de sigma_jk. 
            matriz=np.where(matriz == 0, 0, 1) #Convierto matriz a binario
            probs=[]
            for j_ in range (self.J):
                for k_ in range (self.K):
                    #data1:probabilidades entre servicios k
                    #data2:enlaces entre instalaciones j
                    #matriz: capacidad de recibir en jk
                    data4=np.where(data1== 0, 0, 1) #Convierto matriz de data1 a binario
                    data4=np.tile(data4[k_], (self.J, 1)) #Construyo una matriz de J filas y k columnas 
                    # Cada fila indica si puedo enviar desde cada j y k_ a cualquier otro k
                    data4=np.multiply(data4,matriz) # Combino matrices. 
                    # Data4 indica si puedo enviar desde J y K1 a cualquier destino k de acuerdo con las probabilidades
                    # Matriz indica si la combinación j k puede recibir de acuerdo con la capacidad sigma_jk
                    # Estoy en un bucle. La matriz indica desde j_ y k_ a qué j__ y k__ puedo remitir
                    data4=np.multiply(data4,np.transpose(np.tile(data2[j_],(self.K,1)))) #Combino con los enlaces entre j1 y j2
                    #La suma de cada columna en j4 indica a cuántos destinos puedo enviar desde j1 y k1
                    for j__ in range (self.J):
                        for k__ in range (self.K):
                            a = data2[j_,j__]*data1[k_,k__]*matriz[j__,k__]/np.sum(data4[:,k__]) if np.sum(data4[:,k__])!=0 else 0
                            #probs.append([j_,k_,j__,k__,data2[j_,j__],data1[k_,k__],matriz[j__,k__],np.sum(data4[:,k__]),a])
                            
                            probs.append(a)
                            # Probs depende de si existe p_kk (data1), si existe x_jj (data2), si hay capacidad sigma_jk (matriz) y el número de destinos
                            # Probs de ir de jk a j'k'. Se divide por el número de destinos para
                            # no incurrir en que la suma de las probabilidades sea mayor a 1.
        
            probs = np.reshape(probs,([len(data1)*len(data2),len(data1)*len(data2)]))
            
        # Cada fila es un par jk y cada columna es un par j'k'
        # Con base en la matriz de probabilidades construyo los arcos
        self.file['df_arcos']['p_jjkk']=probs.flatten()
        
        # Agrego las coordenadas de cada servidor j y jp
        self.file['df_arcos']=self.file['df_arcos'].set_index(['nombre_Jp'])
        self.file['df_arcos']=pd.merge(self.file['df_arcos'],
                                          self.file['df_oferta'].set_index('nombre_J'),
                                          left_index=True,right_index=True,how='outer')
        self.file['df_arcos']=self.file['df_arcos'].reset_index()
        self.file['df_arcos']=self.file['df_arcos'].rename(columns={"ubicacionesJ_x":"ubicacionesJp_x",
                                                                          "ubicacionesJ_y":"ubicacionesJp_y",
                                                                          "index":"nombre_Jp"})
        self.file['df_arcos']=self.file['df_arcos'].set_index(['nombre_J'])
        self.file['df_arcos']=pd.merge(self.file['df_arcos'],self.file['df_oferta'].set_index('nombre_J'),
                                          left_index=True,right_index=True,how='outer')
      
        
    def get_objective_function(self):
        _menu_options = {
        '1': 'Minimizar congestión máxima (rho)',
        '2': 'Maximizar accesibilidad mínima (alpha)',
        '3': 'Maximizar continuidad mínimia (delta)',
        '4': 'Maximizar accesibilidad total (alpha)',
        '5': 'Minimizar usuarios en espera total (Lq_total)',
        '6': 'Maximizar continuidad total (delta total)',       
        '7': 'Salir al menú anterior'
        }   
        while True:
            print("\n----------------------------------------------------------")
            print("Selección de la función objetivo")
            print("----------------------------------------------------------\n")
            print("Definir función objetivo:")
            for i,j in _menu_options.items():
                print (f"{i}. {j}")            
            objective = int (input("Selecciona una opción: \n"))
            if 1 <= objective <= 6:
                self.objective=objective
                return [objective,_menu_options[str(objective)]]
            
            elif objective == "7":
              break
            else:
                print("Opción no válida. Inténtalo de nuevo.")
        
            
    def calculate_exact_optima(self,objective,networks) :
        from hcndp import optima
        from hcndp import network_data
        from hcndp.network_data import _I,_J,_K,_archivo,_name_network,_models

        _menu_options = {
        '1': 'Minimizar congestión máxima (rho)',
        '2': 'Maximizar accesibilidad mínima (alpha)',
        '3': 'Maximizar continuidad mínimia (delta)',
        '4': 'Maximizar accesibilidad total (alpha)',
        '5': 'Minimizar usuarios en espera total (Lq_total)',
        '6': 'Maximizar continuidad total (delta total)',
        '7': 'Salir al menú anterior'
        }
        _name=str(f"objective_{_menu_options[str(objective)]}")
        optima.set_model_abstract(objetivo=objective,
                                  nombre_modelo=_name,
                                  _menu_options=_menu_options,
                                  self=self,
                                  networks=networks)
        model=self.models[_name]
        optima.read_data_dat(self,model)
        optima.set_instance(model.model_abstract , model.data_dat, objective, model)
        if objective == 5:
            optima.solve_ipopt(self, model,model.instance)
        else:
            optima.solve_gurobi(self, model,model.instance)          
        optima.get_degrees_freedom(model.instance)           
        optima.set_solution_excel(self, model.instance)
        optima.set_solution_txt(self, model.instance)
        
        # Actualizo la red original con una nueva red
        optima.update_solution_post_optima(original_network=self,
                                           new_network=networks[_name])

        
        

