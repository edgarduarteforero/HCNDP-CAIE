# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 12:33:35 2023

@author: edgar
"""

# <codecell> Funciones complementarias
# Importación de librerías

import numpy as np
import pandas as pd
import math
import os
import networkx as nx
from itertools import product
from io import StringIO
from hcndp.data_functions import indices
from hcndp.data_functions import decay_gauss


# <codecell> Clase network

class Network():
    def __init__(self,I,J,K,archivo,name):
        self.I=I
        self.J=J
        self.K=K
        self.archivo=archivo
        self.name=name
        

        
    def create_folders(self):
        
        # Comprueba si el directorio no existe antes de intentar crearlo
        if not os.path.exists(os.getcwd()+'/data/'+self.name+'/'):
            # Crea el directorio
            os.makedirs(os.getcwd()+'/data/'+self.name+'/')
            #print(f"Directorio /data/'{self.name}' creado con éxito.")
        else:
            #print(f"El directorio /data/'{self.name}' ya existe.")
            pass
        
        if not os.path.exists(os.getcwd()+'/output/'+self.name+'/'):
            # Crea el directorio
            os.makedirs(os.getcwd()+'/output/'+self.name+'/')
            #print(f"Directorio /output/'{self.name}' creado con éxito.")
        else:
            #print(f"El directorio /output/'{self.name}' ya existe.")
            pass
        
    def read_file_excel(self,path):
        #print ("Leyendo datos del archivo de Excel.")
        
        self.file = pd.read_excel(path, sheet_name=None)
    
    def read_file_txt(self,path):
        #print ("Leyendo datos del archivo de text.")
        
        
        
        # Leer todo el archivo de texto
        with open(path, 'r') as file:
            data = file.readlines()
        self.file={}
        
        # Separar las secciones según el encabezado
        sections = {}
        current_section = None
        current_data = []
        
        for line in data:
            line = line.strip()
            if line.startswith("#"):  # Reconocer los encabezados de sección
                if current_section:
                    # Crear un dataframe para la sección actual
                    sections[current_section] = pd.read_csv(StringIO("\n".join(current_data)),sep='\t')
                current_section = line[2:]  # Remover el '#' y el espacio
                current_data = []
            else:
                if current_section:  # Acumular datos para la sección actual
                    current_data.append(line)
        
        # Agregar la última sección al diccionario
        if current_section and current_data:
            sections[current_section] = pd.read_csv(StringIO("\n".join(current_data)),sep='\t')
        
        # Ahora puedes acceder a los dataframes por nombre de sección
        self.file['df_oferta'] = sections['df_oferta']
        self.file['df_niveles']= sections['df_niveles']
        self.file['df_capac']= sections['df_capac']
        self.file['df_demanda']= sections['df_demanda']
        self.file['df_dist_ij']= sections['df_dist_ij']
        self.file['df_dist_ij_k']= sections['df_dist_ij_k']
        self.file['df_sigma_max']= sections['df_sigma_max']
        self.file['df_w_ij']= sections['df_w_ij']
        self.file['df_flujos_ijk']= sections['df_flujos_ijk']
        self.file['flujos_jj']= sections['flujos_jj']
        self.file['prob_serv']= sections['prob_serv']

        self.file['flujos_jj']=self.file['flujos_jj'].reset_index().rename(columns={'index':'Unnamed: 0'})
        self.file['prob_serv']=self.file['prob_serv'].reset_index().rename(columns={'index':'Unnamed: 0'})
        
        
        # Función para verificar si los nombres de un dataframe son números enteros
        def es_entero(cadena):
            try:
                int(cadena)  # Intentar convertir a entero
                return True  # Si no hay error, es un entero
            except ValueError:
                return False  # Si hay error, no es un entero

        # Convertir solo los nombres de columnas que son enteros
        nuevos_nombres = [
            int(col) if es_entero(col) else col  # Convertir a entero solo si es un número
            for col in self.file['prob_serv'].columns
        ]

        # Asignar los nuevos nombres al DataFrame
        self.file['prob_serv'].columns = nuevos_nombres
        
        
        #print("DF self.file")
        #print(self.file)
        
    def delete_surplus_data(self):
        
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
    
    
    def merge_niveles_capac(self,_post_optima,current_solution=None):
        #Agrego las columna nivel de atención y ubicaciones
        
        if _post_optima==True:
            
            output_file=os.getcwd()+'/output/'+self.name_problem+'/salida_optimizacion.xlsx'
            
            if self.tecnica=="Local_Search" or self.tecnica == "Tabu_Search" or self.tecnica=="Aproximación" or\
                self.tecnica=="VND" or self.tecnica=="GVNS":
                data = current_solution.df_sigma 
                
                
            else:
                data = pd.read_excel (output_file,sheet_name='sigma',names=['nombre_J','servicio_K','sigma_jk'],
                                     index_col=0)
            
            if 'nombre_J' not in data.columns:
                data=data.rename(columns={'0':'nombre_J','1':'servicio_K','2':'sigma_jk'})
            self.file['df_capac']= pd.merge(self.file['df_capac'].set_index(['nombre_J','servicio_K']),data.set_index(['nombre_J','servicio_K']),left_index=True,right_index=True)
        
            try:  #Utilizo try porque al usar Local Search genera error.
                self.file['df_capac'].drop(['sigma_jk_x'],axis=1,inplace=True)
                self.file['df_capac'].insert(4,'sigma_jk',self.file['df_capac'].pop('sigma_jk_y'))    
            except KeyError as e:
                pass
            
                
            self.file['df_capac']['sigma_jk'] = self.file['df_capac']['sigma_jk'].round(0).astype('int')
            self.file['df_capac'].reset_index(inplace=True)

        if _post_optima==False:   
            self.file['df_capac']=pd.merge(self.file['df_capac'],self.file['df_niveles'],on='servicio_K',how='left')
            self.file['df_capac']=pd.merge(self.file['df_capac'],self.file['df_oferta'],on='nombre_J',how='inner')
            self.file['df_capac']=self.file['df_capac'].set_index(['nombre_J','servicio_K'],drop=True)
            self.file['df_capac'].reset_index(inplace=True)
            if self.file['df_capac']['s_jk'].sum() < self.file['df_capac']['sigma_jk'].sum():
                print ("""Hay un error en la capacidad.
                       La suma de los s_jk es menor a la suma de los sigma_jk asignados.
                       """)
                raise SystemExit("Stop right there!")
            
    def create_df_asignacion(self,_post_optima,current_solution=None):

    
        if _post_optima == False:
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
            self.file['df_asignacion'].reset_index(inplace=True)
            self.file['df_flujos_ijk'].reset_index(inplace=True)
        if _post_optima == True:
            # Cargo los resultados obtenidos de la optimización
            
            if self.tecnica=="Local_Search" or self.tecnica == "Tabu_Search" or self.tecnica=="Aproximación" or\
                self.tecnica=="VND" or self.tecnica=="GVNS":
                self.file['df_flujos_ijk']=current_solution.df_f_ijk
                self.file['df_fi_ijkjk'] = current_solution.df_fi_ijkjk
            else:
                path=os.getcwd()+'/output/'+self.name_problem+'/salida_optimizacion.xlsx'
                archivo_salida_optim = pd.read_excel(path, sheet_name=None)
                self.file['df_flujos_ijk']=archivo_salida_optim['f_ijk']
                self.file['df_fi_ijkjk'] = archivo_salida_optim['fi_ijkjk']
            
            # Elimino los flujos que no quiero contemplar en el ejercicio
            #import delete_surplus_data
            self.delete_surplus_data()
            
            # Creo la variable z_ijk que tiene valores 1 o 0
            df_flujos_ijk=self.file['df_flujos_ijk'].copy()
            df_flujos_ijk['z_ijk']= np.where(df_flujos_ijk['tao_ijk']!=0, 1,0)
            df_flujos_ijk=df_flujos_ijk.set_index(['nombre_I','nombre_J','servicio_K']).sort_index()
            
            # Creo copias de df_asignacion y df_w_ij
            df_asignacion=self.file['df_asignacion'].copy()
            df_w_ij=self.file['df_w_ij'].copy()
            
            # Actualizo df_asignacion
            # Esta actualización es solamente de sigma y tao
            # Queda pendiente la de lambda_ijk y prop tao
            
            
            #if 'nombre_I' not in df_asignacion.index.names or 'nombre_J' not in df_asignacion.index.names:
            #    # Reconstruir el índice utilizando las columnas 'I' y 'J'
            #     df_asignacion=df_asignacion.set_index(['nombre_I','nombre_J']).merge(df_w_ij.set_index(['nombre_I','nombre_J']),
            #                                                                      left_index=True,
            #                                                                      right_index=True).rename(columns={"w_ij": "Flujo_w_ij"})
            # df_asignacion=df_asignacion.reset_index()
            df_asignacion=df_asignacion.set_index(['nombre_I','nombre_J','servicio_K'])
            df_asignacion=df_asignacion.drop(['tao_ijk','z_ijk'], axis=1, errors='ignore')
            df_asignacion=pd.merge(df_asignacion, df_flujos_ijk,left_index=True, right_index=True)
            
            if 'Unnamed: 0' in df_asignacion.columns:
                df_asignacion.drop(columns=['Unnamed: 0'], inplace=True)
            
            # Actualizo los valores de sigma nuevos
            
            if self.tecnica=="Local_Search" or self.tecnica == "Tabu_Search" or self.tecnica=="Aproximación"\
                or self.tecnica=="VND" or self.tecnica=="GVNS":
                data=current_solution.df_sigma
            else:
                data = pd.read_excel (path,sheet_name='sigma',names=['nombre_J','servicio_K','sigma_jk'],
                                     index_col=0)
                
            if 'nombre_J' not in data.columns:
                data=data.rename(columns={'0':'nombre_J','1':'servicio_K','2':'sigma_jk'})            
            
            df_asignacion = pd.merge(df_asignacion,data.set_index(['nombre_J','servicio_K']),left_index=True,right_index=True)
        
        
            try : # Utilizo try porque al ejecutar en Local Search genera error
                df_asignacion.drop(['sigma_jk_x'],axis=1,inplace=True)
                df_asignacion.insert(4,'sigma_jk',df_asignacion.pop('sigma_jk_y'))
            except KeyError as e:
                pass 
            
            
            df_asignacion['sigma_jk'] = df_asignacion['sigma_jk'].round(0).astype('int')
            df_asignacion.reset_index(inplace=True)
            df_flujos_ijk.reset_index(inplace=True)
            
                        
            self.file['df_asignacion']=df_asignacion
            self.file['df_flujos']=df_flujos_ijk

    
    def create_df_probs_kk(self):

        
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
    
    
    def create_df_arcos(self,_post_optima,current_solution=None): 
        # Creo df_arcos con los índices de j y de k. Es un df con [j j' k k']
        # Explicación en p- 9B Notas del doctorado

        
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
            
            if self.tecnica=="Local_Search" or self.tecnica == "Tabu_Search" or self.tecnica=="Aproximación"\
                or self.tecnica=="VND" or self.tecnica=="GVNS":
                data=current_solution.df_prob_fi_jkjk
            else:
                path=os.getcwd()+'/output/'+self.name_problem+'/salida_optimizacion.xlsx'
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
        self.file['df_arcos'].reset_index(inplace=True)
        
    def get_objective_function(self):
        while True:
            # Solicito al usuario la función objetivo que desea utilizar
            _menu_options = {
            '1': 'Minimizar congestión máxima (rho)',
            '2': 'Maximizar accesibilidad mínima (alpha)',
            '3': 'Maximizar continuidad mínima (delta)',
            '4': 'Maximizar accesibilidad total (alpha)',
            '5': 'Minimizar usuarios en espera total (Lq_total)',
            '6': 'Maximizar continuidad total (delta total)',       
            '7': 'Salir al menú anterior'
            }   
        
            print("\n----------------------------------------------------------")
            print("Selección de la función objetivo")
            print("get_objective_function@network.py")
            print("----------------------------------------------------------\n")
            print("Definir función objetivo:")
            for i,j in _menu_options.items():
                print (f"{i}. {j}")            
            objective = input("Selecciona una opción: \n")
            if objective == '\n':
                print("Opción no válida. Inténtalo de nuevo.")
            
            elif objective.isdigit():
                if 1 <= int(objective) <= 6:
                    self.objective=objective
                    self.optimizar=True
                    return [objective,_menu_options[str(objective)]]
                
                elif objective == 7:
                    self.optimizar=False
                    break
              
            else:
                print("Opción no válida. Inténtalo de nuevo.")
        


    def create_data_dat(self):

        
        path=os.getcwd()+'/data/'+self.name+'/datos.dat'
    
        I=self.I
        J=self.J
        K=self.K 
        
        file= open(path,"w+")
        
        def indices_data_dat(letra,cantidad): # Se generan listas tipo j01,j02,j03
            file.write("set %s := "% letra)
            for i in range (1,cantidad+1):
                file.write(letra.lower()+f"{i:02d}"+" ")
            file.write(";\n\n")
        
        indices_data_dat("I",I)
        indices_data_dat("J",J)
        indices_data_dat("K",K)
    
    
        df_probs_kk=self.file['df_probs_kk']
        df_demanda=self.file['df_demanda_ik']   
        df_capac=self.file['df_capac']
        df_flujos_jj=self.file['df_flujos_jj']
        df_asignacion=self.file['df_asignacion']
        df_w_ij=self.file['df_w_ij']
        df_sigma_max=self.file['df_sigma_max']
        
        # Si estoy usando Local_Search entonces escribo los sigma como parámetros
        # if "Local_Search" in self.name_problem:
        #     file.write("param %s := \n"%"sigma")
        #     file.write(df_capac.reset_index()[['nombre_J','servicio_K','sigma_jk']].to_string(header=False,index=False))
        #     file.write(";\n\n")
        
        #Escribo los r_q
        file.write("param %s := \n"%"r_q")
        file.write(df_probs_kk[['servicio_K','servicio_Kp','p_kkp']].to_string(header=False, index=False))
        file.write(";\n\n")
        
        #Escribo los h
        file.write("param %s := \n"%"h")
        #if 'h_ik' not in df_demanda.index.names:
            # Si 'h_ik' no está en el índice, establecerlo como índice
        #    df_demanda.set_index('h_ik', inplace=True)
        file.write(df_demanda[['nombre_I','servicio_K','h_ik']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        #Escribo los s
        file.write("param %s := \n"%"s")
        file.write(df_capac[['nombre_J','servicio_K','s_jk']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        #Escribo los c
        file.write("param %s := \n"%"c")
        file.write(df_capac[['nombre_J','servicio_K','c_jk']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        #Escribo los x
        file.write("param %s := \n"%"x")
        file.write(df_flujos_jj[['nombre_J','nombre_Jp','x_jjp']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        
        #Escribo los d
        file.write("param %s := \n"%"d")
        file.write(df_asignacion[['nombre_I','nombre_J','servicio_K','f_dij']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        #Escribo los w
        file.write("param %s := \n"%"w")
        file.write(df_w_ij[['nombre_I','nombre_J','w_ij']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        # Escribo M. El número máximo de servidores en un solo jk (max de los s_jk)
        file.write("#Número máximo de s_jk \n")
        file.write("param %s := \n"%"M")
        file.write(str(df_capac['s_jk'].max()))
        file.write(";\n\n")
        
        # Escribo CDemanda máxima en los nodos de demandae haber en un solo jk (max de los s_jk *c_jk)
        file.write("#Máximo de los s_jk * c_jk \n")
        file.write("param %s := \n"%"cap_max")
        file.write(str(df_capac['s_jk*c_jk'].max()))
        file.write(";\n\n")
        
        # Escribo H (Demanda máxima en los nodos de demanda)
        file.write("#Demanda máxima en los nodos de demanda \n")
        file.write("param %s := \n"%"H")
        file.write(str(df_demanda['demanda_i'].max()))
        file.write(";\n\n")
        
        file.write("param %s := \n"%"e")
        file.write("10e-3")
        file.write(";\n\n")
        
        file.write("param %s := \n"%"r_bin_kk")
        file.write(df_probs_kk[['servicio_K','servicio_Kp','bin']].to_string(header=False, index=False))
        file.write(";\n\n")
        
        file.write("param %s := \n"%"sigma_max")
        file.write(df_sigma_max[['servicio_K','sigma_max']].to_string(header=False,index=False))
        file.write(";\n\n")
        
        file.write("param %s := \n"%"K_size")
        file.write(str(K))
        file.write(";\n\n")
        
        file.write("param %s := \n"%"J_size")
        file.write(str(J))
        file.write(";\n\n")
        
        file.close()
    
    # Uso getattr para que el objeto network_copy pueda acceder a los atributos del objeto padre 



class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def __str__(self):
        return f"Node {self.node_id}"

class Node_Demand(Node):
    def __init__(self, node_id, demand, service):
        super().__init__(node_id)
        self.demand = demand
        self.service = service

    def __str__(self):
        return f"Node_Demand {self.node_id}"

class Node_Supply(Node):
    def __init__(self, node_id, capac_instal_max, rate, place, service, matriz_λ, matriz_δ, capac_instal_sigma=0, capac_sigma_dispon=0):
        super().__init__(node_id)
        self.capac_instal_max = capac_instal_max
        self.capac_instal_disponible = capac_instal_max
        self.rate = rate
        self.place = place
        self.service = service
        self.matriz_λ = matriz_λ
        self.matriz_δ = matriz_δ
        self.capac_instal_sigma = capac_instal_sigma
        self.capac_sigma_dispon = capac_sigma_dispon

    def __str__(self):
        return f"Node_Supply {self.node_id}"    

class Edge:
    def __init__(self, edge_id, source, target):
        self.edge_id = edge_id
        self.source = source
        self.target = target

    def __str__(self):
        return f"Edge ({self.source} -> {self.target})"

class Edge_Dem_Sup_W (Edge):
    def __init__(self, edge_id, source, target, distance, service, flow_dem_sup_tau):
        super().__init__(edge_id, source,target)
        self.distance = distance
        self.service = service
        self.flow_dem_sup_tau= flow_dem_sup_tau

    def __str__(self):
        return f"Edge W ({self.source} -> {self.target}), service ({self.service}), τ ({self.flow_dem_sup_tau})"

class Edge_Sup_Sup_X (Edge):
    def __init__(self, edge_id, source, target,node_demand_pop,flow_sup_sup_phi,flow_sup_sup_perc,
                 service_source,service_target,distance_origin_target):
        super().__init__(edge_id, source,target)
        self.node_demand_pop=node_demand_pop
        self.flow_sup_sup_phi=flow_sup_sup_phi
        self.flow_sup_sup_perc=flow_sup_sup_perc
        self.service_source=service_source
        self.service_target=service_target
        self.distance_origin_target=distance_origin_target

    def __str__(self):
        return f"Customer ({self.node_demand_pop}), Edge X ({self.source} -> {self.target}), transfer percentage ({self.flow_sup_sup_perc})"



class Network_representation(Network):
    def __init__(self,I,J,K,archivo,file):
        self.I=I
        self.J=J
        self.K=K
        self.archivo=archivo
        self.file=file
        self.nodes_demand = {}
        self.nodes_supply = {}
        self.edges_dem_sup_W = {}
        self.edges_sup_sup_X = {}
        
        # Matriz de servicios
        
        df_niveles = file['df_niveles']
        items=indices("k",K)
        df_niveles=df_niveles.query('servicio_K in @items')
        
        # Matriz de demandas
        df_demanda = file['df_demanda']
        items=indices("i",I)
        df_demanda=df_demanda.query('nombre_I in @items')
        
        #Matriz de oferta
        df_oferta = file['df_oferta']
        items=indices("j",J)
        df_oferta=df_oferta.query('nombre_J in @items')
        
        # Matriz de capacidades
        df_capac = file['df_capac']
        items=indices("j",J)
        df_capac=df_capac.query('nombre_J in @items')
        items=indices("k",K)
        df_capac=df_capac.query('servicio_K in @items')
        
        #Agrego las columna nivel de atención y ubicaciones
        df_capac=pd.merge(df_capac,df_niveles,on='servicio_K',how='left')
        df_capac=pd.merge(df_capac,df_oferta,on='nombre_J',how='inner')
        
        # Importamos los flujos posibles entre nodos i y nodos j (w_ij)
        df_w_ij = file['df_w_ij']
        items=indices("i",I)
        df_w_ij=df_w_ij.query('nombre_I in @items')
        items=indices("j",J)
        df_w_ij=df_w_ij.query('nombre_J in @items')
        
        # Importamos las distancias entre nodos i j
        df_dist_ij = file['df_dist_ij']
        items=indices("i",I)
        df_dist_ij=df_dist_ij.query('nombre_I in @items')
        items=indices("j",J)
        df_dist_ij=df_dist_ij.query('nombre_J in @items')
        df_w_ij=pd.merge(df_w_ij,df_dist_ij,left_on=['nombre_I','nombre_J'],right_on=['nombre_I','nombre_J'], how='left')
        
        #Importamos los flujos posibles entre nodos j y j' (x_jj)
        df_x_jj = file['flujos_jj']
        df_x_jj=df_x_jj.loc[np.arange(J)]
        df_x_jj=df_x_jj.iloc[:,np.arange(J)+1]
        df_x_jj=np.nan_to_num(df_x_jj)
        df_x_jj = pd.DataFrame(data = df_x_jj, index = indices("j",J), columns = indices("j",J))
        df_x_jj = df_x_jj.melt(ignore_index=False).reset_index().rename(columns={"index": "nombre_J", "variable": "nombre_Jp","value":"x_jjp"})

        #Importamos los porcentajes de transferencia (p_kk')
        df_probs = file['prob_serv']
        df_probs=df_probs.drop(['Unnamed: 0'], axis=1)
        df_probs=df_probs.loc[np.arange(K)]
        df_probs=df_probs[np.arange(K)+1]
        df_probs=np.nan_to_num(df_probs)
        df_probs = pd.DataFrame(data = df_probs, index = indices("k",K), columns = indices("k",K))
        df_probs = df_probs.melt(ignore_index=False).reset_index().rename(columns={"index": "servicio_K", "variable": "servicio_Kp","value":"p_kkp"})
        df_probs["bin"]=(df_probs['p_kkp']!=0).astype(int)
        
        
        #Construimos la matriz df_arcos para flujos jkjk
        lista=[]
        j=indices("j",J)
        k=indices("k",K)
        for _a in j:
          for _b in j:
            for _c in k: # range (1,K+1):
              for _d in k: #range(1,K+1):
                lista.append([_a,_c,_b,_d])
        
        df_arcos=pd.DataFrame(lista,columns=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'])
        df_arcos.sort_values(by=['nombre_J','servicio_K'], inplace=True)

        # Creación de los nodos de demanda
        for _,row in df_demanda.iterrows():
            self.add_node_demand(row['nombre_I'],row['demanda_i'],'k01')

        # Creación de nodos de oferta artificiales
        for _, row in df_demanda.iterrows():
            self.add_node_supply(node_id=row['nombre_I'].replace('i', 'j')+'k00', 
                            capac_instal_max=math.nan,
                            rate=math.nan,
                            place=row['nombre_I'].replace('i', 'j'),
                            service='k00',
                            matriz_λ=pd.DataFrame(columns=['nombre_I','nombre_J','servicio_K','λ_ijk']),
                            matriz_δ=pd.DataFrame(columns=['nombre_I','nombre_J','servicio_K','servicio_Kp','δ_ijkkp']),
                            capac_instal_sigma=math.nan,
                            capac_sigma_dispon=math.nan)
            
        # Los nodos de oferta artificiales tienen un lambda igual a la demanda de su nodo i

        # Creación de los nodos de oferta
        for _, row in df_capac.iterrows():
            self.add_node_supply(node_id=row['nombre_J']+row['servicio_K'],
                            capac_instal_max=row['s_jk'],
                            #capac_instal_disponible = row['s_jk'],
                            rate=row['c_jk'],
                            place=row['nombre_J'],
                            service=row['servicio_K'],
                            matriz_λ=pd.DataFrame(columns=['nombre_I','nombre_J','servicio_K','λ_ijk']),
                            matriz_δ=pd.DataFrame(columns=['nombre_I','nombre_J','servicio_K','servicio_Kp','δ_ijkkp']),
                            capac_instal_sigma=0,
                            capac_sigma_dispon=0)

        # Creación de los arcos demanda - oferta
        for _, row in df_w_ij.iterrows():
            if row['w_ij']==1:
                self.add_edge_dem_sup_W(edge_id=row['nombre_I']+row['nombre_J']+'k01',
                                   source=row['nombre_I'],
                                   target=row['nombre_J']+'k01',
                                   distance=row['dist_IJ'],
                                   service='k01',
                                   flow_dem_sup_tau=0)

        #Creación de arcos entre nodos de oferta articiciales y reales
        for _,_i in self.edges_dem_sup_W.items():
                self.add_edge_sup_sup_X(edge_id= _i.source + _i.source.replace('i', 'j') +'k00' + _i.target,
                               source= _i.source.replace('i', 'j') +'k00',
                               target= _i.target,
                               node_demand_pop=_i.source,
                               flow_sup_sup_phi=0,
                               flow_sup_sup_perc=0,
                               service_source='k00',
                               service_target='k01',
                               distance_origin_target=0)    

        # Creación de los arcos oferta - oferta
        for _, row in df_x_jj.iterrows():
            for _p, row_p in df_probs.iterrows():
                if row['x_jjp']!=0 and row_p['p_kkp'] !=0 and \
                    df_capac[(df_capac['nombre_J'] == row['nombre_Jp']) & (df_capac['servicio_K']==row_p['servicio_Kp'])]['s_jk'].values[0]!=0:
                    for _i in df_demanda['nombre_I']:
                        if ((row_p['servicio_K']==row_p['servicio_Kp'] and (row['nombre_J'] != row['nombre_Jp'])) == False):
                            self.add_edge_sup_sup_X(edge_id=_i+row['nombre_J']+row_p['servicio_K']+row['nombre_Jp']+row_p['servicio_Kp'],
                                               source=row['nombre_J']+row_p['servicio_K'],
                                               target=row['nombre_Jp']+row_p['servicio_Kp'],
                                               node_demand_pop=_i,
                                               flow_sup_sup_phi=0,
                                               flow_sup_sup_perc=0,
                                               service_source=row_p['servicio_K'],
                                               service_target=row_p['servicio_Kp'],
                                               distance_origin_target=df_dist_ij[(df_dist_ij['nombre_I'] == _i) & (df_dist_ij['nombre_J'] == row['nombre_Jp'])]['dist_IJ'].values[0])
            
        # Creación de los λ_ijk en cada nodo de servicio jk
        for _i,_j in self.nodes_supply.items():
            for _,_i in df_demanda.iterrows():
                _lista=[_i['nombre_I'],_j.place,_j.service,0.0]
                _j.matriz_λ.loc[len(_j.matriz_λ)] = _lista
        
        # Creación de los δ_ijkk' en cada nodo de servicio jk
        for _i,_j in self.nodes_supply.items():
            for _,_i in df_demanda.iterrows():
                for _p,_k in df_niveles.iterrows():
                    _lista=[_i['nombre_I'],_j.place,_j.service,_k['servicio_K'],0.0]
                    _j.matriz_δ.loc[len(_j.matriz_δ)] = _lista
                    
        # Creación el df_asignación para almacenar flujos entrantes lambda ijk 
        # Construyo una matriz g con los arribos externos, es decir los ϕi.j.k0jk
        _lista_i=indices("i",I)
        _lista_j=indices("j",J)
        _lista_k=indices("k",K)
        _lista = list(product(_lista_i, _lista_j,_lista_k))
        _df_asignacion=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
        _df_asignacion["lambda_ijk"] = 0.0
        _df_asignacion=_df_asignacion.sort_values(by=['nombre_I','nombre_J', 'servicio_K'])
        _df_asignacion.set_index(['nombre_I', 'nombre_J','servicio_K'],inplace=True)
        self.df_asignacion = _df_asignacion
        self.df_asignacion.reset_index(inplace=True)


    def add_node_demand(self, node_id,demand,service):
        if node_id not in self.nodes_demand:
            self.nodes_demand[node_id] = Node_Demand(node_id,demand,service)

    def add_node_supply(self, node_id,capac_instal_max, rate, place, service,matriz_λ,matriz_δ,capac_instal_sigma,capac_sigma_dispon):
        if node_id not in self.nodes_supply:
            self.nodes_supply[node_id] = Node_Supply(node_id,capac_instal_max,rate, place, service,matriz_λ,matriz_δ, capac_instal_sigma,capac_sigma_dispon)
            self.nodes_supply[node_id].matriz_δ['δ_ijkkp']  = 0.0
            #self.nodes_supply[node_id].matriz_δ['δ_ijkkp']  = matriz_δ['δ_ijkkp'].astype(float)
            
    def add_edge_dem_sup_W(self, edge_id,source, target, distance,service, flow_dem_sup_tau):
        self.edges_dem_sup_W[edge_id] = Edge_Dem_Sup_W(edge_id,source, target, distance, service , flow_dem_sup_tau)
        if target not in self.nodes_demand[source].neighbors:
            self.nodes_demand[source].add_neighbor(target)

    def add_edge_sup_sup_X(self, edge_id, source, target,node_demand_pop,flow_sup_sup_phi,flow_sup_sup_perc,service_source,service_target,distance_origin_target):
        self.edges_sup_sup_X[edge_id] = Edge_Sup_Sup_X(edge_id,source, target, node_demand_pop,flow_sup_sup_phi,flow_sup_sup_perc,service_source,service_target,distance_origin_target)
        if target not in self.nodes_supply[source].neighbors:
            self.nodes_supply[source].add_neighbor(target)
        if target not in self.nodes_demand[node_demand_pop].neighbors:
            self.nodes_demand[node_demand_pop].add_neighbor(target)
    
    #Cargo las funciones que hacen parte de la heurística
    # Función de asignación exhaustiva de recursos
    # Función que llena los datos de df_matriz, y actualiza df_matriz_todos
    
    def asignacion_recursos(self,path,_k):
        # Construyo matriz de distancias filtrada (elimino distancias mayores a d_o)
        def construir_matriz(_k):
            df_matriz=pd.DataFrame(columns=['nombre_J','dist_max','nombre_I','demanda_I','s_jk','sigma_jk','reman_despues','reman_antes'])
            return df_matriz
        
        # Preparo df_matriz para que tenga los datos de una iteración
        suma_asignacion=0
        _d_o=path.nodes_services[_k].distance_do
        df_matriz_todos=construir_matriz(_k)
    
        # Suma de s_jk
        _x = sum([_i.capac_instal_max for _i in self.nodes_supply.values() if not math.isnan(_i.capac_instal_max) and  _i.service==_k])    
        
        # Calculo distancias dentro de la cobertura
        for _,_i in self.edges_sup_sup_X.items():
            if _i.distance_origin_target<=_d_o:
                _i.distance_origin_target_covered=_i.distance_origin_target
            else:
                _i.distance_origin_target_covered=math.nan
        
        while suma_asignacion < path.nodes_services[_k].service_capacity:
            df_matriz=construir_matriz(_k)
            
            # Construyo df_matriz con los arcos ij de la mayor distancia entre cada j y todos los i
            for _,_j in self.nodes_supply.items(): #Para cada nodo de oferta jk
                if _j.service==_k:
                    selected, max_dist = 0 , 0
                    
                    for i in self.edges_sup_sup_X.values():
                        if i.target == _:
                            if i.distance_origin_target_covered >= max_dist:
                                max_dist=i.distance_origin_target_covered
                                selected=i
                    
                    if selected != 0:
                        nueva_fila = {'nombre_J': selected.target, 
                                      'dist_max': selected.distance_origin_target_covered, 
                                      'nombre_I': selected.node_demand_pop, 
                                      'demanda_I': self.nodes_demand[selected.node_demand_pop].demand, 
                                      's_jk': self.nodes_supply[selected.target].capac_instal_disponible-1, # Resto 1 para que no se asigne toda la capacidad s_jk
                                      'sigma_jk':0,
                                      'reman_despues':math.nan,
                                      'reman_antes':math.nan}
                        selected.distance_origin_target_covered=math.nan
                        df_matriz = pd.concat([df_matriz, pd.DataFrame([nueva_fila])], ignore_index=True)
            
            # ordeno matriz por mayor distancia en orden descendente
            df_matriz=df_matriz.sort_values(by=['dist_max'],ascending=False)
            
            # remanente antes (fila0) = smax
            if df_matriz.empty :
                print (" ")
                break 
            else: 
                df_matriz['reman_antes'].iloc[0] = path.nodes_services[_k].service_capacity
            
            # Actualizo df_matriz con la asignación y copio sus datos a df_matriz_todos   
            for _i in range (len(df_matriz)):
                if df_matriz['reman_antes'].iloc[_i] <=0:
                    df_matriz['sigma_jk'].iloc[_i]=0
                    
                if _i==0 and suma_asignacion==0: 
                    df_matriz['reman_antes'].iloc[_i] = path.nodes_services[_k].service_capacity
                    df_matriz['sigma_jk'].iloc[_i]=min(df_matriz['demanda_I'].iloc[_i],df_matriz['s_jk'].iloc[_i],df_matriz['reman_antes'].iloc[_i])
                    df_matriz['reman_despues'].iloc[_i]=df_matriz['reman_antes'].iloc[_i]-df_matriz['sigma_jk'].iloc[_i]
                elif _i==0 and suma_asignacion!=0:
                    df_matriz['reman_antes'].iloc[_i] = df_matriz_todos['reman_despues'].iloc[-1]
                    df_matriz['sigma_jk'].iloc[_i]=min(df_matriz['demanda_I'].iloc[_i],df_matriz['s_jk'].iloc[_i],df_matriz['reman_antes'].iloc[_i])
                    df_matriz['reman_despues'].iloc[_i]=df_matriz['reman_antes'].iloc[_i]-df_matriz['sigma_jk'].iloc[_i]
                else:
                    df_matriz['reman_antes'].iloc[_i] = df_matriz['reman_despues'].iloc[_i-1]
                    df_matriz['sigma_jk'].iloc[_i]=min(df_matriz['demanda_I'].iloc[_i],df_matriz['s_jk'].iloc[_i],df_matriz['reman_antes'].iloc[_i])
                    df_matriz['reman_despues'].iloc[_i]=df_matriz['reman_antes'].iloc[_i]-df_matriz['sigma_jk'].iloc[_i]
                
                # Actualización de valores en los objetos
                self.nodes_supply[df_matriz['nombre_J'].iloc[_i]].capac_instal_disponible -= df_matriz['sigma_jk'].iloc[_i]
                self.nodes_supply[df_matriz['nombre_J'].iloc[_i]].capac_instal_sigma += df_matriz['sigma_jk'].iloc[_i]
                self.nodes_supply[df_matriz['nombre_J'].iloc[_i]].capac_sigma_dispon += df_matriz['sigma_jk'].iloc[_i]
                
            suma_asignacion+=sum(df_matriz['sigma_jk'])
            df_matriz_todos = df_matriz_todos._append(df_matriz,ignore_index=True)
        
        #print ("Final")
    
    
    # Función que calcula los δ_ijkk
    
    def asignacion_flujos_δ(self, network, path, _k, _kp):
        for _j in network.nodes_supply.values():
            if _j.service == _k:
                λ_ijk = _j.matriz_λ[(_j.matriz_λ['servicio_K'] == _k) & (_j.matriz_λ['nombre_J'] == _j.place)]
                δ_ij = _j.matriz_δ[(_j.matriz_δ['servicio_K'] == _k) & (_j.matriz_δ['nombre_J'] == _j.place)]
                
                for _p, _i in _j.matriz_δ.iterrows():
                    i = _i['nombre_I']
                    kp = _kp
                    
                    if _j.matriz_δ.loc[_p, 'servicio_Kp'] == kp:
                        if f"{_k}{kp}" in path.edges_ser_ser_R:
                            _r = path.edges_ser_ser_R[f"{_k}{kp}"].transfer_percentage
                        else:
                            _r = 0
                        
                        δ_ijkkp = λ_ijk.loc[(λ_ijk['nombre_I'] == i), 'λ_ijk'].iloc[0] * _r
                        _j.matriz_δ.loc[_p, 'δ_ijkkp'] = float(δ_ijkkp)
        
    def asignacion_flujos_δ2(self,network,path,_k,_kp):
        #print ("Inicio asignación flujos delta para ",_k," y ",_kp) 
        for _,_j in network.nodes_supply.items():
            if _j.service==_k:
                for _p,_i in _j.matriz_δ.iterrows():
                    j=_j.place
                    k=_j.service
                    i=_i['nombre_I']
                    kp=_kp
                    #kp=_i['servicio_Kp']
                    
                    if k+kp in path.edges_ser_ser_R:
                        _r=path.edges_ser_ser_R[k+kp].transfer_percentage
                    else:
                        _r=0
                    # Obtengo δ_ijkkp multiplicando _r * el lambda que sale de ijk
                    δ_ijkkp=float(_j.matriz_λ.where((_j.matriz_λ['nombre_I']==i) & (_j.matriz_λ['nombre_J']==j) 
                                      & (_j.matriz_λ['servicio_K']==k))['λ_ijk'].dropna().values[0] * _r)
                    if _j.matriz_δ.loc[_p,'nombre_I']==i and \
                        _j.matriz_δ.loc[_p,'nombre_J']==j and \
                        _j.matriz_δ.loc[_p,'servicio_K']==k and \
                        _j.matriz_δ.loc[_p,'servicio_Kp']==kp:        
                            _j.matriz_δ.loc[_p, 'δ_ijkkp'] = float(δ_ijkkp)
                
                #print ("Matriz de deltas actualizada para servicio origen ",_k)
                #print (_j.matriz_δ [_j.matriz_δ ['δ_ijkkp'] > 0])
        #print ("Finalizo asignación flujos delta para ",_k) 
    
    
    #Función para el cálculo de fi_ijkjk cuando ya se cuenta con lambdas calculados por Jackson
    
    def solucion_flujos_phi_post_Jackson(self,network_repr):
       for _,_arco in network_repr.edges_sup_sup_X.items():
           source=_arco.source
           #target=_arco.target
           _π=_arco.flow_sup_sup_perc
           _population=_arco.node_demand_pop
           _lambda=network_repr.nodes_supply[source].matriz_λ
           _lambda=_lambda.loc[_lambda['nombre_I'] == _population, 'λ_ijk'].values[0]
           
           _arco.flow_sup_sup_phi=_lambda*_π

    
    # Función para solucionar el problema de transporte entre k y kp
    def solucion_entre_k_kp(self,network,_k,_kp,archivo,current_solution):
        #print ("Inicio solución del problema de transporte entre ",_k, " y ",_kp)
    
        global network_x
        network_x = nx.DiGraph()
        df_dist_ij = archivo['df_dist_ij']
        
        #Creo nodos oferta. La oferta son los sigma disponibles * tasa de servicio (rate)
        for _i,_j in network.nodes_supply.items():
            if _j.service==_kp:
                network_x.add_node(_j.node_id,tipo="oferta",demand= ( round(_j.capac_instal_sigma) *_j.rate * 100 ))
                # Resto 10 a demand para que la solución no quede en el borde: capac_instal_sigma != s_jk
        # Creo nodos demanda. La demanda es el valor de delta_ijkkp
        for _i,_j in network.nodes_supply.items():
            if _j.service==_k: #Servicio origen
                for _,_l in _j.matriz_δ.iterrows(): 
                    if _l.δ_ijkkp != 0 and _l.servicio_Kp == _kp: #Si hay arco con _kp
                        network_x.add_node(_l["nombre_I"]+_l["nombre_J"]+_l["servicio_K"]+_l["servicio_Kp"],
                                           tipo="demanda",source=_j.node_id,demand=round(-_l['δ_ijkkp']*100))
                        # Creo arcos entre nodos de oferta y demanda
                        for _m in _j.neighbors: 
                            if _m[-3:]==_kp:
                                # Decido qué función de costo utilizar para definir los flujos
                                if current_solution.objective == "1": # 1 Significa congestión rho
                                    _distancia = df_dist_ij.loc[(df_dist_ij['nombre_I'] == _l["nombre_I"]) & (df_dist_ij['nombre_J'] == _m[:3]), 'dist_IJ'].values[0]
                                elif current_solution.objective == "2": # 2 Significa accesibilidad alpha
                                    _distancia = df_dist_ij.loc[(df_dist_ij['nombre_I'] == _l["nombre_I"]) & (df_dist_ij['nombre_J'] == _m[:3]), 'dist_IJ'].values[0]
                                    if _distancia == 0: # Corrijo posibles divisiones por cero
                                        _distancia = 0.001
                                    _distancia = round(network.nodes_supply[_m].capac_instal_sigma / (_l.δ_ijkkp*_distancia))
                                #print (f"Distancia entre {_l['nombre_I']} y {_m[:3]}: {_distancia}")
                                elif current_solution.objective == "3": # 3 Significa continuidad delta
                                    _distancia = df_dist_ij.loc[(df_dist_ij['nombre_I'] == _l["nombre_I"]) & (df_dist_ij['nombre_J'] == _m[:3]), 'dist_IJ'].values[0]
                                network_x.add_edge(_l["nombre_I"]+_l["nombre_J"]+_l["servicio_K"]+_l["servicio_Kp"],_m,weight=_distancia)
        
        # Nodos tipo demanda             Nodos tipo oferta 
        # Suma_Origen                    Suma_Destino
        #i1j1k1j2k2      ----->          i1j2k2
        # Tienen demanda negativa        Tienen demanda positiva
        
        #Balanceo nodos de demanda y oferta
        _suma_destino, _suma_origen=0,0
        for _i in network_x.nodes(data=True):
            if _i[1]['tipo']=="oferta":
                _suma_destino += _i[1]["demand"] #Suma de nodos destino o tipo oferta
            else:
                _suma_origen += _i[1]["demand"] #Suma de nodos origen o tipo demanda
        # ficticio hace las veces de nodo artificial para el balanceo de demanda
        if abs(_suma_destino) > abs(_suma_origen) : #Creo nodo tipo demanda ficticio y enlaces hacia el último jk con costo cero
            network_x.add_node("ficticio",tipo="demanda",demand=-abs(_suma_destino +_suma_origen) )
            for _i in network_x.nodes(data=True):
                if _i[1]["tipo"]=="oferta":
                    network_x.add_edge("ficticio",_i[0],weight=0)
        elif abs(_suma_destino) < abs(_suma_origen): #Creo nodo tipo oferta  ficticio de oferta y enlace desde el último jk con costo cero 
            network_x.add_node("ficticio",tipo="oferta",demand=abs(_suma_origen + _suma_destino))
            for _i in network_x.nodes(data=True):
                if _i[1]["tipo"]=="demanda":
                    network_x.add_edge(_i[0],"ficticio",weight=0)
        # network_x tiene una red con el nodo ficticio, los nodos ijkk y los nodos jk.
        # Los nodos ijkk son predecesores de los nodos jk porque allí se definen los flujos fi ijkjk
        
        # Redondear los pesos
        #for source, target, data in network_x.edges(data=True):
        #    if 'weight' in data:
        #        data['weight'] = round(data['weight'])
        
        
        if current_solution.objective in {"1","3"}: 
            # 1 Significa congestión rho y 3 significa continuidad delta
            # Resuelvo el problema de minimización del costo
            flowCost, flowDict = nx.network_simplex(network_x)
        elif current_solution.objective == "2": # 2 Significa accesibilidad alpha
            # Invertir los costos
            for u, v, data in network_x.edges(data=True):
                data['weight'] = -data['weight']
            flowCost, flowDict = nx.network_simplex(network_x)
            flowCost = -flowCost
        #elif current_solution.objective == "3": # 3 Significa continuidad delta
             # Resuelvo el problema de árbol de expansión

    
        # Como escalé las ofertas y demandas *100, actualizo sus valores
        # Itera sobre cada diccionario dentro del diccionario principal
        for subdiccionario in flowDict.values():
            # Itera sobre cada valor en el subdiccionario
            for _i, _j in subdiccionario.items():
                # Divide el valor por 100
                subdiccionario[_i] = float(_j / 100)
        
        # Actualizo las capacidades instaladas disponibles en cada nodo de oferta
        for _node_from, _flows in flowDict.items():
            for _node_to, _flow in _flows.items():
                if _flow > 0  :
                    if _node_from != "ficticio" and _node_to != 'ficticio':
                        #print(f"{_node_from}, {_flows}-> {_node_to}: {_flow}")
                        #print (network.nodes_supply[_node_to].capac_sigma_dispon)
                        network.nodes_supply[_node_to].capac_sigma_dispon -= _flow
                        #print (network.nodes_supply[_node_to].capac_sigma_dispon)
            
        # Imprimir resultados
        _resultado={}
        #print("Costo Total:", flowCost)
        #print("\nFlujo Óptimo:")
        for _node_from, _flows in flowDict.items():
            for _node_to, _flow in _flows.items():
                if _flow > 0:
                    #print(f"{_node_from} -> {_node_to}: {_flow}")
                    _resultado[(_node_from,_node_to)] = _flow
        
        #Construyo el gráfico de la red
        #pos=nx.circular_layout(network_x)
        #nx.draw(network_x, pos, node_size=3000, node_color='white',edgecolors= "grey", edge_color='black',linewidths= 2,
        #width= 2)
        #labels = {node: str(node) for node in network_x.nodes}
        #nx.draw_networkx_labels(network_x, pos, labels)
        ##edge_labels = nx.get_edge_attributes(network_x, "weight")
        ##print (edge_labels)
        #nx.draw_networkx_edge_labels(network_x, pos, _resultado)
        ## Set margins for the axes so that nodes aren't clipped
        #ax = plt.gca()
        #ax.margins(0.20)
        #plt.axis("off")
        #plt.show()
    
        
        # Almaceno los ϕ_{ijkjk} en los arcos sup_sup_X
        for _node_from, _flows in flowDict.items():
            for _node_to, _flow in _flows.items():
                if _flow > 0 :
                    if _node_from != "ficticio" and _node_to != "ficticio" :
                        _direccion = _node_from[:-3]+_node_to
                        network.edges_sup_sup_X[_direccion].flow_sup_sup_phi=_flow
        
        #print ("Termino solución del problema de transporte entre ",_k, " y ",_kp)
    
    
    
    # Función de obtención de porcentajes π
    #Esta función se podría borrar si no se utiliza más adelante
    def obtencion_π_2(self,network,k,kp):
        print ("Inicio obtención de π para ",k," y ",kp)
        _lista=[]
        for _i,_j in network.edges_sup_sup_X.items():
            if _j.service_source == k and _j.service_target == kp :
                _lista.append([_j.node_demand_pop,_j.source,_j.target,_j.flow_sup_sup_phi])
        _df = pd.DataFrame(_lista, columns=['poblacion','origen', 'destino', 'ϕ'])
        _suma_por_origen = _df.groupby('origen')['ϕ'].sum()
        #print ("Suma de ϕ por origen")
        #print (_suma_por_origen)
        
        _df['porcentaje'] = _df.apply(lambda row: row['ϕ'] / _suma_por_origen[row['origen']] if _suma_por_origen[row['origen']] > 0 else 0, axis=1)
        #print ("Obtención pi")
        #print (_df)
        
        for _,_i in _df.iterrows():
            _enlace=_i['poblacion']+_i['origen']+_i['destino']
            for _j,_k in network.edges_sup_sup_X.items():
                if _j == _enlace:
                    _k.flow_sup_sup_perc=_i['porcentaje']
                    #print (_i['porcentaje'])
                    #print (_j[:3],_enlace,_i['porcentaje'],_k.flow_sup_sup_perc)
        
        #print ("Finalizo obtención de π para ",k," y ",kp)
    
    #Esta propuesta de obtencion_π no se hace para cada k y kp
    # Se aplica a todas las combinaciones posibles de jkjpkp
    def obtencion_π(self,network):
        #print ("Primero calculo pi para cada i j k jp kp")
        for _i,_j in network.edges_sup_sup_X.items():

            _suma_phi = sum(objeto.flow_sup_sup_phi for objeto in network.edges_sup_sup_X.values() \
                            if objeto.source == _j.source and \
                               objeto.node_demand_pop == _j.node_demand_pop)
             
            if _j.flow_sup_sup_phi == 0 and _suma_phi == 0:
                _j.flow_sup_sup_perc_ijkjk=0
            else: 
                _j.flow_sup_sup_perc_ijkjk=_j.flow_sup_sup_phi/_suma_phi
                
        
        #print ("Ahora calculo pi para cada j k jp kp") # Se calcula para cada jkjpkp y se almacena en los ijkjpkp
        for _i,_j in network.edges_sup_sup_X.items():
            
            #pi_jkjpkp = suma_i (phi ijkjpkp) / suma_ijpkp (phi ijkjpkp)
            #pi_jkjpkp = suma_phi_jkjpkp / suma_phi_jk
            _suma_phi_jkjpkp = sum(objeto.flow_sup_sup_phi for objeto in network.edges_sup_sup_X.values() \
                            if objeto.source == _j.source and \
                                objeto.target == _j.target)
            
            _suma_phi_jk= sum(objeto.flow_sup_sup_phi for objeto in network.edges_sup_sup_X.values() \
                            if objeto.source == _j.source)
                
            if _suma_phi_jkjpkp == 0 and _suma_phi_jk == 0:
                _j.flow_sup_sup_perc_jkjk=0
            else: 
                _j.flow_sup_sup_perc_jkjk=_suma_phi_jkjpkp/_suma_phi_jk
             
            _j.flow_sup_sup_perc=_j.flow_sup_sup_perc_jkjk
        return 
        
        
    # Función de asignación de porcentajes π para flujos cíclicos
    def asignacion_π_ciclos(self,network,k,kp):
        for _i,_j in network.edges_sup_sup_X.items():
            if _j.service_source==k and _j.service_target==kp:
                if _i[1:3]==_i[4:6] == _i[10:12]:
                    _j.flow_sup_sup_perc=1.0
    # π es el porcentaje de usuarios que habiendo recibido servicio en jk y
    # teniendo que dirigirse a k'... son ruteados a j'
                
    # Función de construcción de $λ_{ijk}$ a partir de la suma de los phi_ijkjk
    # Es una primera aproximación de los λ_{ijk}. Los verdaderos se calculan en solutions.py línea 738
    def construyo_λ(self,network,kp):
        for _j in network.nodes_supply.values():
            if _j.service==kp:
                for _,_fila in _j.matriz_λ.iterrows():
                    _i=_fila['nombre_I']
                    _jp=_fila['nombre_J']
                    _kp=_fila['servicio_K']
                    _suma=0.0
                    for _arco in network.edges_sup_sup_X.values():
                        if  _arco.node_demand_pop==_i and  _arco.target == _jp+_kp:
                                _suma += _arco.flow_sup_sup_phi
                    _j.matriz_λ.loc[_,'λ_ijk'] = _suma
                    
                
    
    def __str__(self):
        _df_pivot = self.df_asignacion.reset_index()
        _df_pivot['nombre_I_nombre_J']=_df_pivot['nombre_I']+_df_pivot['nombre_J']
        _df_pivot = _df_pivot.pivot(index='nombre_I_nombre_J', columns='servicio_K', values='lambda_ijk')
            
        return f"Tasas de arribo para usuarios de \n {_df_pivot}"
        
        
        #nodes_demand_str = ", ".join(str(node) for node in self.nodes_demand.values())
        #nodes_supply_str = ", ".join(str(node) for node in self.nodes_supply.values())
        #edges_dem_sup_str = ", ".join(str(edge) for edge in self.edges_dem_sup_W)
        #edges_sup_sup_str = ", ".join(str(edge) for edge in self.edges_sup_sup_X)
        #return f"Network with nodes: {nodes_demand_str} \n and {nodes_supply_str} \nEdges: {edges_dem_sup_str} and {edges_sup_sup_str} "

class Path_representation:
    def __init__(self,K,archivo,file):
        self.K=K
        self.archivo=archivo
        self.file=file
        self.nodes_services = {}
        self.edges_ser_ser_R = {}

        # Matriz de servicios
        df_niveles = file['df_niveles']
        items=indices("k",K)
        df_niveles=df_niveles.query('servicio_K in @items')
        
        #Importamos los porcentajes de transferencia (p_kk')
        df_probs = file['prob_serv']
        df_probs=df_probs.drop(['Unnamed: 0'], axis=1)
        df_probs=df_probs.loc[np.arange(K)]
        df_probs=df_probs[np.arange(K)+1]
        df_probs=np.nan_to_num(df_probs)
        df_probs = pd.DataFrame(data = df_probs, index = indices("k",K), columns = indices("k",K))
        df_probs = df_probs.melt(ignore_index=False).reset_index().rename(columns={"index": "servicio_K", "variable": "servicio_Kp","value":"p_kkp"})
        df_probs["bin"]=(df_probs['p_kkp']!=0).astype(int)
        
        # Creación de los nodos de servicios
        for _,row in df_niveles.iterrows():
            self.add_node_service(row['servicio_K'],row['Servicio'],row['sigma_max'],row['d_o_k'])
        
        #Creación de nodo del servicio artificial k00
        self.add_node_service('k00','Servicio artificial',math.nan,math.nan)
        
        #Creación de arcos oferta oferta artificiales
        self.add_edge_ser_ser_R(edge_id='k00k01',
                                source='k00',
                                target='k01',
                                transfer_percentage=1)
        
        # Creación de los arcos oferta - oferta
        for _, row in df_probs.iterrows():
            if row['p_kkp']!=0:
                self.add_edge_ser_ser_R(edge_id=row['servicio_K']+row['servicio_Kp'],
                                        source=row['servicio_K'],
                                        target=row['servicio_Kp'],
                                        transfer_percentage=row['p_kkp'])

    
    def add_node_service(self, node_id,service_name,service_capacity,distance_do):
        if node_id not in self.nodes_services:
            self.nodes_services[node_id] = Node_Service(node_id,service_name,service_capacity,distance_do)

    def add_edge_ser_ser_R(self, edge_id, source, target,transfer_percentage):
        self.edges_ser_ser_R[edge_id] = Edge_Ser_Ser_R(edge_id,source,target, transfer_percentage)
        #self.edges_ser_ser_R.append(Edge_Ser_Ser_R(source, target, transfer_percentage))
        if target not in self.nodes_services[source].neighbors:
            self.nodes_services[source].add_neighbor(target)
        #self.nodes_services[source].add_neighbor(target)

    def __str__(self):
        nodes_services_str = ", ".join(str(node) for node in self.nodes_services.values())
        edges_services_str = ", ".join(str(edge) for edge in self.edges_ser_ser_R)
        return f"Clinical Path with nodes: {nodes_services_str} and \nEdges: {edges_services_str}"

class Node_Service(Node):
    def __init__(self, node_id, service_name, service_capacity,distance_do):
        super().__init__(node_id)
        self.service_name = service_name
        self.service_capacity = service_capacity
        self.distance_do = distance_do

    def __str__(self):
        return f"Node_Service {self.node_id}"

class Edge_Ser_Ser_R (Edge):
    def __init__(self, edge_id,source, target, transfer_percentage):
        super().__init__(edge_id,source,target)
        self.transfer_percentage = transfer_percentage

    def __str__(self):
        return f"Edge R ({self.source} -> {self.target})"


