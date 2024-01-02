# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 17:42:37 2023

@author: edgar
"""

def show_menu_figures(solution):
    network=solution.network_copy
    
    from hcndp import figures
    while True:
        print("\n----------------------------------------------------------")
        print("Representaciones de la red")
        print("----------------------------------------------------------\n")
        print(" 1. Plano cartesiano")
        print(" 2. Chord diagram")
        print(" 3. Probabilidades de x clientes en espera")
        print(" 4. Probabilidades de esperar t tiempo")
        print(" 5. Longitud de cola y tiempo en espera por nodo")
        print(" 6. Plano cartesiano nodos y cobertura")
        print(" 7. Distancias gaussianas")
        print(" 8. Accesibilidad en cartesiano, mapa de calor y nodos")
        print(" 9. Flujos entre ik y jk")
        print("10. Salir")
        opcion1 = input("Selecciona una opción: \n")
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            try:     
                figures.figure_network_cartesian(network)
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has importado los datos.")
        
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")
            try: 
                figures.figure_chord_diagram(network)
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has importado los datos.")
        
        elif opcion1 == "3":
            print("Has seleccionado la Opción 3.")
            try:
                figures.figure_prob_custom_queue(network)    
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
                
        elif opcion1 == "4":
            print("Has seleccionado la Opción 4.")
            try:
                figures.figure_prob_time_in_queue(network)    
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
        
        elif opcion1 == "5":
            print("Has seleccionado la Opción 5.")
            try:
                figures.figure_Lq_per_node(network)
                figures.figure_Wq_per_node(network)
                figures.figure_service_rate_per_node(network)
                figures.figure_rho_per_node(network)
                figures.figure_rho_weighted(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
            
        elif opcion1 == "6":
            print("Has seleccionado la Opción 6.")
            try:
                figures.figure_nodes_coverage(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
            
        elif opcion1 == "7":
            print("Has seleccionado la Opción 7.")
            try:
                figures.figure_gaussian(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
        
        elif opcion1 == "8":
            print("Has seleccionado la Opción 8.")
            try:
                figures.figure_accessibility(network)
                figures.figure_heatmap_accessibility(network)
                figures.figure_accessibility_per_node(network)
                figures.figure_accessibility_per_service(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
         
        elif opcion1 == "9":
            print("Has seleccionado la Opción 9.")
            try:
                figures.figure_flows_f_ijk(network) 
                figures.figure_flows_f_ijk_k1(network)
                figures.figure_flows_f_ijkjk(network)
                figures.figure_flows_f_jpkpjk(network)
                figures.figure_digraph(network)
                figures.figure_digraph_complete(network)
                figures.figure_sankey(network)

            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
         
        elif opcion1 == "10":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

#%% <codecell> Descriptive basic figures

def figure_network_cartesian(network):
    # Gráfico de la red completo (incluye flujos de ij y de jj')
    import matplotlib.pyplot as plt
    import pandas as pd
    plt.rcdefaults()
    import matplotlib
    import os
    

    fig, ax = plt.subplots(1,figsize=(6,6*1),constrained_layout=True) #Figura con 1 axes, que contiene toda la red
    fig.suptitle('Direcciones de flujos entre nodos',fontsize=14,weight="bold")

    demanda=network.file['df_demanda']
    capacidad=network.file['df_capac']
    #Se asume que se está utilizando toda la capacidad disponible en cada nodo de oferta j y servicio k
    capacidad['cap_total']=capacidad.c_jk*capacidad.sigma_jk #Capacidad de atención (cli/serv * serv/nodo)
    idx = pd.IndexSlice #Permite referenciar más fácilmente en un multiindex.
    datos_dem=demanda[['ubicacionesI_x','ubicacionesI_y','demanda_i']] #Datos de la demanda 
    datos_cap=capacidad[['ubicacionesJ_x','ubicacionesJ_y','cap_total']] #Datos de la oferta

    # Construyo los scatter con datos de oferta y de demanda
    ax.scatter(network.file['df_oferta']['ubicacionesJ_x'],
               network.file['df_oferta']['ubicacionesJ_y'],
               label='Nodos de servicio',c ="Green",marker='D',
               edgecolor='darkgreen',s=200,alpha=0.5)
    ax.scatter(datos_dem['ubicacionesI_x'],datos_dem['ubicacionesI_y'], 
               label='Nodos de demanda',c="Red",marker='o',
               edgecolor='darkred',s=datos_dem['demanda_i']*100,alpha=0.2)

    # Grafico la asignación de usuarios entre cada servidor para el primer servicio k=1
    # prueba es la sección de df_asignación donde Z=1 
    # Los naranjas son los flujos entre i y j para k1
    asignacion=network.file['df_asignacion'].copy()
    prueba=asignacion[(asignacion['tao_ijk'] >= 0.1)] #Escojo las asignaciones habilitadas con z=1
    prueba=pd.merge(asignacion,network.file['df_w_ij'],
                    left_on=['nombre_I','nombre_J'],
                    right_on=['nombre_I','nombre_J'], how='left')
    prueba=prueba[(prueba['w_ij']>0)]
    # Dibujo una flecha para cada arco posible existente en prueba.
    prueba.apply(lambda row: ax.arrow(row['ubicacionesI_x'],row['ubicacionesI_y'],
                                      row['ubicacionesJ_x']-row['ubicacionesI_x'],
                                      row['ubicacionesJ_y']-row['ubicacionesI_y'],
                                      width=0.0001,alpha=0.5,color='orangered',                            
                                      fill=True,length_includes_head=True,
                                      head_width=0.055,
                                      ),
                                      axis=1)

    # prueba2 contiene los flujos entre j y j'
    prueba2=pd.merge(network.file['df_arcos'].reset_index(),
                     network.file['df_flujos_jj'],
                     left_on=['nombre_J','nombre_Jp'],right_on=['nombre_J','nombre_Jp'], how='left')
    prueba2=prueba2[(prueba2['x_jjp'] >0)]

    # Los grises son los flujos entre j para cualquier k.
    # Consultar detalles de anotaciones en: https://matplotlib.org/stable/tutorials/text/annotations.html
    for _, row in prueba2.iterrows():
        ax.annotate("", xy=(row.iloc[5], row.iloc[6]), xytext=(row.iloc[7], row.iloc[8]),
                    arrowprops=dict(color="grey", linewidth=0.9, arrowstyle="->", connectionstyle="arc3,rad=0.3"))


    # Agrego los nombres de nodos de demanda
    for i in range(network.I):
        matriz=network.file['df_demanda'].reset_index()[['nombre_I','ubicacionesI_x','ubicacionesI_y']].drop_duplicates().to_numpy()
        ax.annotate(matriz[i,0], (float(matriz[i,1]) - 0.15, float(matriz[i,2]) +0.005))

    # Agrego los nombres de nodos de oferta
    for i in range(network.J):
        matriz=network.file['df_oferta'].reset_index()[['nombre_J','ubicacionesJ_x','ubicacionesJ_y']].drop_duplicates().to_numpy()
        ax.annotate(matriz[i,0], (float(matriz[i,1])+0.15, float(matriz[i,2])+0.005))

    ax.legend(loc='lower left',fontsize=8)
    ax.set_xlabel('Coordenada x')
    ax.set_ylabel('Coordenada y')
    ax.set_title("Naranja: Enlaces ijk. Grises: Enlaces jk j'k'")
    ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.1)
    ax.set_ylim(ax.get_ylim()[0] - 0.1, ax.get_ylim()[1] + 0.1)
    plt.show()
    #plt.pause(0.1) #Muestra imagen en pestaña Plots a medida que se ejecuta el código
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/network_cartesian.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/network_cartesian.png'
    plt.savefig(path, dpi=300)
  
    
def figure_chord_diagram(network):
    # Es necesario tener en cuenta que existen flujos entre los servidores de la red. Cada flujo se da 
    # entre un par de nodos de servicio y un par de servicios: jj'kk'
    # Construyo un Chord Diagram para representar los flujos entre servidores jj'kk'
    import pandas as pd
    import holoviews as hv
    hv.extension('bokeh','matplotlib')
    import webbrowser
    import os
    path=os.getcwd()+'/output/'+network.name+'/'

    # Construyo un dataframe con jjpkkp y pjjkk
    df_arcos=network.file['df_arcos'].reset_index()
    df_arcos['origen'],df_arcos['destino']=0,0
    df_prueba = pd.DataFrame()
    df_prueba=df_arcos[['nombre_J','nombre_Jp','servicio_K','servicio_Kp','p_jjkk','origen','destino']]
    
    # Ajusto el contenido de df_prueba para que quede así:
    # origen - destino - pjjkk
    df_prueba.loc[:,'origen']=df_prueba['nombre_J']+df_prueba['servicio_K']
    df_prueba.loc[:,'destino']=df_prueba['nombre_Jp']+df_prueba['servicio_Kp']
    
    df_prueba = df_prueba[['origen', 'destino', 'p_jjkk']]
    
    # Multiplico la probabilidad por 100 y convierto a enteros para mejor visualización

    df_prueba.loc[:,'p_jjkk'] = df_prueba['p_jjkk']*100
    df_prueba.loc[:,'p_jjkk'] = df_prueba['p_jjkk'].astype(int)    
    df_prueba=df_prueba[(df_prueba != 0).all(1)] # Elimino ceros
    df_prueba=df_prueba.reset_index(drop=True) # Ajusto el índice
    
    hv.output(size=200)
    chord=hv.Chord(df_prueba)
    chord.opts(width=400, 
               height=400,
               node_color='index', 
               edge_color='origen',
               edge_line_width=1.5,
               node_size=40,
               edge_alpha=0.7,
               label_index='index',
               cmap='Category10', 
               edge_cmap='Category10',
               label_text_font_size='10pt')
       
    hv.save(chord, path+'chord2', fmt='html') # Se exporta la imagen
    html_file_path = path+'chord2'+'.html'
    webbrowser.open('file://' + html_file_path, new=2)
    
    # TODO La imagen chord debe ser exporada como un png.
    #hv.save(chord, path+'chord2', fmt='png')


#%% <codecell> Probability figures

def figure_prob_custom_queue(network):
    # Construyo gráficos para representar las probabilidades de tener clientes en cola
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()
    
    df_capac=network.file['df_capac'].reset_index()
    
    if 'customers' not in network.file:
        print("Uno de los KPI consiste en la probabilidad de tener x clientes o menos en cola.")
        customers = int(input("Ingresa un valor para clientes: \n"))
        network.file['customers']=customers
        from hcndp import kpi
        kpi.set_prob_custom_queue(network,customers)
        network.file['customers']=customers
        
    
    customers=network.file['customers']
    labels = df_capac['nombre_J']+'K'+df_capac['servicio_K'].astype(str)
    serie1 = df_capac['prob_b0']
    serie2 = df_capac['prob_b'+str(customers)]
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, serie1, width, label='prob_b0')
    rects2 = ax.bar(x + width/2, serie2, width, label='prob_b'+str(customers))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Prob. acumulada de número de clientes en cola')
    ax.set_title('Probabilidades por nodo de servicio')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/'+str(customers)+'_prob_custom_queue.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/_prob_custom_queue.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/_prob_custom_queue.png'
        
    plt.savefig(path, dpi=300)
     
def figure_prob_time_in_queue(network):
    # Construyo gráficos para representar las probabilidades de tiempo en cola
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()

    df_capac=network.file['df_capac'].reset_index()

    if 'time' not in network.file:
        from hcndp import kpi
        print("Uno de los KPI consiste en la probabilidad de esperar t o menos tiempo en cola.")
        time = int(input("Ingresa un valor para t: \n"))
        kpi.set_prob_wait_time (network,time)
        network.file['time']=time
        
    time=network.file['time']
    labels = df_capac['nombre_J']+'K'+df_capac['servicio_K'].astype(str)
    #serie1 = df_capac['prob_t0.25']
    serie1 = df_capac['prob_t'+str(time)]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, serie1, width, label='prob_t'+str(time))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Probabilidad acumulada de tiempo en espera')
    ax.set_title('Probabilidades por nodo de servicio')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)

    fig.tight_layout()

    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/'+str(time)+'prob_time_in_queue.png'
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/prob_time_in_queue.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/prob_time_in_queue.png'
     
    
    plt.savefig(path, dpi=300)

#%% <codecell> Congestion and Queuing theory figures

def figure_Lq_per_node (network):
    # Construyo gráficos para representar las medidas de desempeño
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()
    
    df_capac=network.file['df_capac'].reset_index()
    labels = df_capac['nombre_J']+'K'+df_capac['servicio_K'].astype(str)
    serie1 = df_capac['L_q']
    serie2 = df_capac['W_q']

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig =plt.figure()
    ax = fig.add_subplot(111) # Create matplotlib axes
    #ax2 = fig.add_subplot(111) # Create matplotlib axes
    #ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

    rects1 = ax.bar(x - width/2, serie1, width, label='L_q')
    #rects2 = ax.bar(x + width/2, serie2, width, label='W_q')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Medidas de desempeño por nodo de servicio')
    ax.set_xticks(x, labels)
    ax.legend()
    
    ax.bar_label(rects1, padding=3)

    fig.tight_layout()

    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/figure_Lq_per_node.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_Lq_per_node.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_Lq_per_node.png'
   
    plt.savefig(path, dpi=300)
    
def figure_Wq_per_node (network):
    # Construyo gráficos para representar las medidas de desempeño
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()
    
    df_capac=network.file['df_capac'].reset_index()
    labels = df_capac['nombre_J']+'K'+df_capac['servicio_K'].astype(str)
    serie1 = df_capac['W_q']

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig =plt.figure()
    ax = fig.add_subplot(111) # Create matplotlib axes
    
    rects1 = ax.bar(x - width/2, serie1, width, label='W_q')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Medidas de desempeño por nodo de servicio')
    ax.set_xticks(x, labels)
    ax.legend()
    
    ax.bar_label(rects1, padding=3)

    fig.tight_layout()

    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/figure_Wq_per_node.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_Wq_per_node.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_Wq_per_node.png'
  
    plt.savefig(path, dpi=300)
      
def figure_service_rate_per_node(network):
    # Construyo gráficos de calor para analizar los recursos disponibles en cada par j k
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import seaborn as sns
    import os
    plt.clf() #Evita que se sobreescriban imágenes de seaborn
    
    df_capac=network.file['df_capac'] 
    df_temporal = df_capac.pivot_table( index='nombre_J', columns='servicio_K', values='cap_total')
    
    sns.set(rc = {'figure.figsize':(5,5)})
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5,robust=True,annot=True,annot_kws={"size": 7},cbar_kws={'label': 'Number of servers'})
    ax.set(xlabel='Services (k)', ylabel='Facilities (j)')
    #path=os.getcwd()+'/output/'+network.name+'/service_rate_per_node.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/service_rate_per_node.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/service_rate_per_node.png'
  
    
    ax.figure.savefig(path,dpi=300) 
    print (ax)
    
def figure_rho_per_node(network):
    # Construyo gráficos de calor para analizar la congestión para cada par j k
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import seaborn as sns
    import os
    plt.clf() #Evita que se sobreescriban imágenes de seaborn
    
    df_capac=network.file['df_capac'] 
    df_temporal = df_capac.pivot_table( index='nombre_J', columns='servicio_K', values='rho')
    sns.set(rc = {'figure.figsize':(6,6)})
    ax1=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5,vmin=0, vmax=1,annot=True,annot_kws={"size": 7},cbar_kws={'label': 'Rho'})
    ax1.set(xlabel='Services (k)', ylabel='Facilities (j)')
    #path=os.getcwd()+'/output/'+network.name+'/rho_per_node.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/rho_per_node.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/rho_per_node.png'
  
    
    ax1.figure.savefig(path,dpi=300)
    print (ax1)

def figure_rho_weighted(network):
    # Calculo utilización para cada nodo de servicio j
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import seaborn as sns
    import os
    import numpy as np
    plt.clf() #Evita que se sobreescriban imágenes de seaborn
    
    df_capac=network.file['df_capac'] 
    prueba=df_capac[df_capac['rho']!=0].groupby('nombre_J')['rho'].mean()

    # Construyo gráficos para representar 
    labels = prueba.index
    serie1 = prueba
    x = np.arange(len(serie1))
    fig, ax = plt.subplots(figsize=(7,7))
    ax.set(ylim=(0, 1.0))
    ax.bar(labels,serie1, label='Utilization')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Service facilities')
    #ax.set_title('Probabilidades por nodo de servicio')
    ax.set_xticks(x,labels)
    ax.legend()
    fig.tight_layout()
    #path=os.getcwd()+'/output/'+network.name+'/rho_weighted.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/rho_weighted.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/rho_weighted.png'
  
    
    
    ax.figure.savefig(path,dpi=300)    

#%% <codecell> Accessibility and coverage figures

def figure_nodes_coverage(network):
    # Mapa de puntos y círculos de cobertura
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import pandas as pd
    import os
    import numpy as np
    
    df_demanda=network.file['df_demanda']
    df_capac=network.file['df_capac']
    df_niveles=network.file['df_niveles']
    df_oferta=network.file['df_oferta']
    df_asignacion=network.file['df_asignacion'].copy()
    
    fig, ax = plt.subplots(network.K,figsize=(6,6*network.K),constrained_layout=True) #Figura con K axes, uno para cada servicio
    #gs = gridspec.GridSpec(2, 3)
    fig.suptitle('Nodos de servicio y demanda con sus áreas de cobertura',fontsize=14,weight="bold")
    
    # Tabla pivote para demanda
    demanda = pd.pivot_table(df_demanda, values=['demanda_i','ubicacionesI_x','ubicacionesI_y'], 
                               index=['nombre_I','servicio_K'], 
                               aggfunc="mean")
 

    # Tabla pivote para capacidad
    capacidad = pd.pivot_table(df_capac, values=['c_jk','sigma_jk','ubicacionesJ_x','ubicacionesJ_y'], 
                               index=['nombre_J', 'servicio_K'], 
                               aggfunc="mean")

    #Se asume que se está utilizando toda la capacidad disponible en cada nodo de oferta j y servicio k
    capacidad['cap_total']=capacidad.c_jk*capacidad.sigma_jk #Capacidad de atención (cli/serv * serv/nodo)
    idx = pd.IndexSlice

    #for k in range (K): # Para cada servicio se hace un ax.
    for k_nom in df_niveles['servicio_K']:  # Para cada servicio se hace un ax.
        k=int(''.join(filter(str.isdigit, k_nom)))-1
        datos_dem=demanda.loc[idx[:,k_nom], ['ubicacionesI_x','ubicacionesI_y','demanda_i']] #Datos de la demanda de cada servicio K
        datos_cap=capacidad.loc[idx[:,k_nom], ['ubicacionesJ_x','ubicacionesJ_y','cap_total']] #Datos de la oferta de cada servicio K
        
        #Imprimo círculos de cobertura para cada instalacion
        for j in range (len(df_oferta)): 
            instala=df_oferta.reset_index().iloc[j]['nombre_J']
            df_asignacion=df_asignacion.reset_index().set_index(['nombre_J','servicio_K'])
            df_asignacion=df_asignacion.sort_index()
            # Los círculos reflejan la cobertura y por lo tanto tienen que ver con la accesibilidad
            # Si dejo 'cob' trae las coberturas por nivel
            # Si dejo 'cob_a' trae la cobertura única
            circle = plt.Circle((df_oferta['ubicacionesJ_x'][j],
                                  df_oferta['ubicacionesJ_y'][j]), radius=df_asignacion.loc[(instala,k_nom),'d_o_k'].values[0],
                                facecolor='none', alpha=0.2,edgecolor="black", 
                                linewidth=3)
            ax[k].add_patch(circle)
       
        #Imprimo los puntos de demanda y oferta
        im_oferta=ax[k].scatter(df_oferta['ubicacionesJ_x'],df_oferta['ubicacionesJ_y'],label='Nodos de servicio',
                      c=datos_cap['cap_total'],cmap ="Greens",marker='D',edgecolor='green')
        im_demanda=ax[k].scatter(datos_dem['ubicacionesI_x'],datos_dem['ubicacionesI_y'], label='Nodos de demanda',
                      c=datos_dem['demanda_i']*1,cmap="Reds",marker='o',edgecolor='darkred')
        
        # Agrego los nombres de nodos de demanda
        for i in range(network.I):
            matriz=df_demanda.reset_index()[['nombre_I','ubicacionesI_x','ubicacionesI_y']].drop_duplicates().to_numpy()
            ax[k].annotate(matriz[i,0], (matriz[i,1], matriz[i,2] +0.4))
        
        # # Agrego los nombres de nodos de oferta
        for j in range(network.J):
            matriz=df_oferta.reset_index().to_numpy()
            matriz = np.delete(matriz, 0, axis=1)
            ax[k].annotate(matriz[j,0], (matriz[j,1], matriz[j,2] -0.4))
        
        ax[k].legend(loc='lower left',fontsize=8)
        ax[k].set_xlabel('Coordenada x')
        ax[k].set_ylabel('Coordenada y')

        ax[k].set_title("Servicio "+str(k+1))
        ax[k].relim() # recompute the ax.dataLim
        ax[k].autoscale_view() # update ax.viewLim using the new dataLim
        ax[k].set(xlim=(-4.5, 25), ylim=(-4.5, 25))
        ax[k].grid()
        plt.colorbar(im_oferta,ax=ax[k],label="Oferta (Servidores)")
        plt.colorbar(im_demanda,ax=ax[k],location='bottom',label="Demanda (Pacientes)")
    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/figure_nodes_coverage.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_nodes_coverage.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_nodes_coverage.png'
  
    
    plt.savefig(path, dpi=300)

def figure_gaussian(network):
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import os

    # Representación gráfica de las coberturas utilizando la función gaussiana
    df_asignacion=network.file['df_asignacion']
    figura_gaussian = df_asignacion.loc[df_asignacion['lambda_ijk'] > 0].plot.scatter('dist_IJ', 'f_dij')
    
    # Agregar un título al gráfico
    figura_gaussian.set_title('Gráfico de Dispersión: dist_IJ vs f_dij')
    
    # Mostrar el gráfico
    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/figure_gaussian.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_gaussian.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_gaussian.png'
 
    plt.savefig(path, dpi=300)

def figure_accessibility(network):
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import pandas as pd
    import os
    import numpy as np
    plt.rcdefaults()
    
    df_demanda=network.file['df_demanda'].copy()
    df_capac=network.file['df_capac']
    df_niveles=network.file['df_niveles']
    df_oferta=network.file['df_oferta']
    df_asignacion=network.file['df_asignacion'].copy()
    
    fig, ax = plt.subplots(network.K,figsize=(8,8*network.K),constrained_layout=True) #Figura con K axes, uno para cada servicio

    fig.suptitle('Accesibilidad para cada nodo de demanda',fontsize=14,weight="bold")
    
    # Tabla pivote para demanda
    demanda = pd.pivot_table(df_demanda, values=['demanda_i','ubicacionesI_x','ubicacionesI_y','acces_H2SFCA'], 
                               index=['nombre_I','servicio_K'], 
                               aggfunc="mean")
 
    # Tabla pivote para capacidad
    capacidad = pd.pivot_table(df_capac, values=['c_jk','sigma_jk','ubicacionesJ_x','ubicacionesJ_y'], 
                               index=['nombre_J', 'servicio_K'], 
                               aggfunc="mean")
    
    #Se asume que se está utilizando toda la capacidad disponible en cada nodo de oferta j y servicio k
    capacidad['cap_total']=capacidad.c_jk*capacidad.sigma_jk #Capacidad de atención (cli/serv * serv/nodo)
    idx = pd.IndexSlice #Permite referenciar más fácilmente en un multiindex.
    
    df_niveles = df_niveles.set_index(['servicio_K'])
    print (df_niveles)
    
    for i_nom in df_niveles.index:  # Para cada servicio se hace un ax.       
        i=int(''.join(filter(str.isdigit, i_nom)))-1
        
        if 'k01' not in df_niveles.index:
            df_niveles = df_niveles.set_index(['servicio_K'])
            
        for m in range (len(df_oferta)): #Imprimo círculos de cobertura para oferta
            circle = plt.Circle((df_oferta['ubicacionesJ_x'][m], df_oferta['ubicacionesJ_y'][m]), 
                                radius=df_niveles.loc[i_nom]['d_o_k'], 
                                facecolor='none', alpha=0.2)#,edgecolor="black", linewidth=3)
            ax[i].add_patch(circle)


        for m in range (len(df_demanda)): #Imprimo círculos de cobertura para demanda
            circle = plt.Circle((df_demanda.iloc[m]['ubicacionesI_x'], df_demanda.iloc[m]['ubicacionesI_y']), 
                                radius=df_niveles.loc[i_nom]['d_o_k'], 
                                facecolor="none",edgecolor="gray",linestyle="--",alpha=0.2) #,edgecolor="black", linewidth=3)
            ax[i].add_patch(circle)

        #Datos de la demanda de cada servicio K
        datos_dem=demanda.loc[idx[:,i_nom], ['ubicacionesI_x','ubicacionesI_y','demanda_i','acces_H2SFCA']] 
        #Datos de la oferta de cada servicio K
        datos_cap=capacidad.loc[idx[:,i_nom], ['ubicacionesJ_x','ubicacionesJ_y','cap_total']] 
        
        #Imprimo los puntos de oferta y demanda
        im_oferta=ax[i].scatter(df_oferta['ubicacionesJ_x'],df_oferta['ubicacionesJ_y'],label='Supply nodes',
                      c=datos_cap['cap_total'],cmap ="Blues",marker='D',s=150,edgecolor='black')
        im_demanda=ax[i].scatter(datos_dem['ubicacionesI_x'],datos_dem['ubicacionesI_y'], label='Demand nodes',
                      c=datos_dem['demanda_i'],cmap="Reds",marker='o',edgecolor='black',
                      s=100) #s=10+datos_dem['acces_H2SFCA']*100

        #Configuro la leyenda
        rombos=ax[i].scatter(-100,-100,marker='D',c="white",s=150,edgecolor='black', label="Supply nodes")
        circulos=ax[i].scatter(-100,-100,marker='o',c="white",s=150,edgecolor='black', label="Demand nodes")
        areas_supply=ax[i].scatter(-100,-100,marker='o',c="gray",s=150,label="Facility Catchment Areas",alpha=0.2)
        areas_demand=ax[i].scatter(-100,-100,marker='o',c="none",edgecolor='gray',s=150,label="Demand Catchment Areas",alpha=0.2)
        ax[i].legend(loc='lower left',fontsize=12,handles=[rombos,circulos,areas_supply,areas_demand])
        ax[i].set_xlabel('Coord. x')
        ax[i].set_ylabel('Coord. y')

        ax[i].set_title("Service "+str(i+1))
       
        # Agrego los nombres de nodos de demanda
        for k in range(network.I):
            matriz=df_demanda.reset_index()
            matriz=matriz[['nombre_I','ubicacionesI_x','ubicacionesI_y','acces_H2SFCA']].to_numpy() #.drop_duplicates()
            ax[i].annotate(str(matriz[k,0]+", Acc = "+str(round(matriz[k,3], 2))), (matriz[k,1]+0.3, matriz[k,2] +0.00))

        # Agrego los nombres de nodos de oferta
        for k in range(network.J):
            matriz=df_oferta.reset_index().to_numpy()
            matriz = np.delete(matriz, 0, axis=1)
            ax[i].annotate(matriz[k,0], (matriz[k,1]+0.30, matriz[k,2]+0.30))

        ax[i].relim() # recompute the ax.dataLim
        ax[i].autoscale_view() # update ax.viewLim using the new dataLim

        plt.colorbar(im_oferta,ax=ax[i],label="Capacity (Supply nodes)")
        plt.colorbar(im_demanda,ax=ax[i],location='bottom',label="Demand (Patients/unit of time)")
        
    plt.show()
    #path=os.getcwd()+'/output/'+network.name+'/figure_accessibility.png'
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_accessibility.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_accessibility.png'
 
    
    plt.savefig(path, dpi=300)

def figure_heatmap_accessibility(network):
    import seaborn as sns
    import os
    import matplotlib.pyplot as plt
    
    # Construyo gráficos de calor para analizar la accesibilidad para cada par i k
    df_accesibilidad=network.file['df_accesibilidad']
    df_temporal = df_accesibilidad.pivot_table( index='nombre_I', columns='servicio_K', values='Acc_ponderado')
    df_temporal=df_temporal.fillna(0)
    sns.set(rc = {'figure.figsize':(5.5,5.5)})
    
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5, robust=True,annot=True,annot_kws={"size": 7})#,vmin=0, vmax=5000)
    ax.set(xlabel='Services (k)', ylabel='Demand nodes (i)')
    
    #path=os.getcwd()+'/output/'+network.name+'/figure_heatmap_accessibility.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_heatmap_accessibility.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_heatmap_accessibility.png'
 
    
    ax.figure.savefig(path,dpi=300)    
    

def figure_accessibility_per_node(network):    
    # Construyo gráficos para representar las accesibilidades
    import os
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import numpy as np
    
    df_capac=network.file['df_capac']
    df_capac=df_capac.reset_index()
    df_acces_node=network.file['df_acces_node']
    
    labels = df_acces_node.index
    serie1 = df_acces_node
    x = np.arange(len(serie1))
    fig, ax = plt.subplots(figsize=(10,6))
    #ax.set(ylim=(0, 1.1))

    ax.bar(labels,serie1, label='Accessibility')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Demand nodes')
    #ax.set_title('Probabilidades por nodo de servicio')
    ax.set_xticks(x,labels)
    ax.legend()
    fig.tight_layout()

    #path=os.getcwd()+'/output/'+network.name+'/figure_accessibility_per_node.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_accessibility_per_node.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_accessibility_per_node.png'
 
    ax.figure.savefig(path,dpi=300)    



def figure_accessibility_per_service(network):
    # Construyo gráficos para representar las accesibilidades por cada servicio
    import os
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    import numpy as np
    
    df_capac=network.file['df_capac']
    df_capac=df_capac.reset_index()
    df_acces_service=network.file['df_acces_service']
    
    labels = df_acces_service.index
    serie1 = df_acces_service
    x = np.arange(len(serie1))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(labels,serie1, label='Accessibility')
    #ax.set(ylim=(0, 4.0))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Services')
    #ax.set_title('Probabilidades por nodo de servicio')
    ax.set_xticks(x,labels)

    ax.legend()
    fig.tight_layout()

    #path=os.getcwd()+'/output/'+network.name+'/figure_accessibility_per_service.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_accessibility_per_service.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_accessibility_per_service.png'

    ax.figure.savefig(path,dpi=300)  

#%% <codecell> Flows
    
def figure_flows_f_ijk(network):
    
    # Creo un mapa de calor con los flujos fijk
    # en las filas van los orígenes ik
    # en las columnas van los destinos jk
    import seaborn as sns
    from matplotlib import pyplot as plt
    import os 
    
    df_temporal=network.file['df_flujos_ijk'].reset_index().copy()
    df_temporal['ik']=df_temporal['nombre_I']+df_temporal['servicio_K']
    df_temporal['jk']=df_temporal['nombre_J']+df_temporal['servicio_K']
    df_temporal = df_temporal.pivot_table( index='ik', columns='jk', values='tao_ijk')

    df_temporal=df_temporal.fillna(0).round(decimals=0)
    sns.set(rc = {'figure.figsize':(8,8)})
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5, robust=True,vmin=0, vmax=20,annot=True,annot_kws={"size": 7})
    ax.set(xlabel='Destinations (jk)', ylabel='Origins (ik)',title='Patient flow between demand and supply nodes')
    #ax.figure.savefig("figura_2SFCA.png",dpi=300)

    #path=os.getcwd()+'/output/'+network.name+'/figure_flows_f_ijk.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_flows_f_ijk.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_flows_f_ijk.png'

    ax.figure.savefig(path,dpi=300)  

def figure_flows_f_ijk_k1(network):
    # Creo un mapa de calor con los flujos fijk PERO SOLO PARA K1
    # en las filas van los orígenes ij
    # en las columnas van los destinos jk

    import seaborn as sns
    from matplotlib import pyplot as plt
    import os 

    df_temporal=network.file['df_flujos_ijk'].reset_index().copy()
    df_temporal = df_temporal[df_temporal.tao_ijk != 0]
    df_temporal['ik']=df_temporal['nombre_I']+df_temporal['servicio_K']
    df_temporal['jk']=df_temporal['nombre_J']+df_temporal['servicio_K']
    df_temporal = df_temporal.pivot_table( index='ik', columns='jk', values='tao_ijk')

    df_temporal=df_temporal.fillna(0).round(decimals=0)
    sns.set(rc = {'figure.figsize':(8,8)})
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5, robust=True,vmin=0, vmax=20, annot=True,annot_kws={"size": 12}) # vmax=df_temporal.to_numpy().max(),
    ax.set(xlabel='Destinations (jk)', ylabel='Origins (ik)',title='Patient flow between demand and supply nodes')
    #ax.figure.savefig("figura_2SFCA.png",dpi=300)

    #path=os.getcwd()+'/output/'+network.name+'/figure_flows_f_ijk_k1.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_flows_f_ijk_k1.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_flows_f_ijk_k1.png'

    ax.figure.savefig(path,dpi=300)  

def figure_flows_f_ijkjk(network):
    # Creo un mapa de calor con los porcentajes fi_jkjk
    # en las filas van los orígenes jpkp
    # en las columnas van los destinos jk
    import seaborn as sns
    from matplotlib import pyplot as plt
    import os 

    df_temporal=network.file['df_arcos'].reset_index().copy()
    df_temporal['jk_origen']=df_temporal['nombre_J']+df_temporal['servicio_K']
    df_temporal['jk_destino']=df_temporal['nombre_Jp']+df_temporal['servicio_Kp']
    df_temporal = df_temporal.pivot_table( index='jk_origen', columns='jk_destino', values='p_jjkk')

    df_temporal=df_temporal.fillna(0).round(decimals=2)
    sns.set(rc = {'figure.figsize':(8,8)})
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5, robust=True,vmin=0, vmax=1,annot=True,annot_kws={"size": 7})
    ax.set(xlabel='Destinations (jk)', ylabel='Origins (jk)',title='Proportions of patients between supply nodes')
    #ax.figure.savefig("figura_2SFCA.png",dpi=300)

    #path=os.getcwd()+'/output/'+network.name+'/figure_flows_f_ijkjk.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_flows_f_ijkjk.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_flows_f_ijkjk.png'

    ax.figure.savefig(path,dpi=300)  

def figure_flows_f_jpkpjk(network):
    # Creo un mapa de calor con los flujos fjpkpjk
    # en las filas van los orígenes jpkp
    # en las columnas van los destinos jk
    import seaborn as sns
    from matplotlib import pyplot as plt
    import pandas as pd
    import os 

    df_capac=network.file['df_capac'].copy()
    df_arcos=network.file['df_arcos'].reset_index().copy()
    df_temporal=pd.merge(df_capac['lambdas'],df_arcos,on=["nombre_J",'servicio_K'],how="left")
    df_temporal['lambdas*probs']=df_temporal['lambdas']*df_temporal['p_jjkk']
    df_temporal=df_temporal.reset_index()
    df_temporal['jk_origen']=df_temporal['nombre_J']+df_temporal['servicio_K']
    df_temporal['jk_destino']=df_temporal['nombre_Jp']+df_temporal['servicio_Kp']
    df_temporal = df_temporal.pivot_table( index='jk_origen', columns='jk_destino', values='lambdas*probs')

    df_temporal=df_temporal.fillna(0).round(decimals=2)
    sns.set(rc = {'figure.figsize':(8,8)})
    ax=sns.heatmap(df_temporal,cmap="Oranges",linewidths=.5, robust=True,vmin=0, vmax=10,annot=True,annot_kws={"size": 7})
    ax.set(xlabel='Destinations (jk)', ylabel='Origins (jk)',title='Patient flow between supply nodes')
    #ax.figure.savefig("figura_2SFCA.png",dpi=300)

    #path=os.getcwd()+'/output/'+network.name+'/figure_flows_f_jpkpjk.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_flows_f_jpkpjk.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_flows_f_jpkpjk.png'

    ax.figure.savefig(path,dpi=300)  

def figure_digraph(network):
 
    # REPRESENTACIÓN DE LA RED
    # Los colores corresponden a las proporciones de pacientes entre cada par de nodos.
    import pandas as pd
    import numpy as np
    import networkx as nx
    import matplotlib.pyplot as plt
    import pygraphviz
    import os
    
    df_grafo=network.file['df_grafo']
    
    # Build your graph
    G=nx.from_pandas_edgelist(df_grafo,"jk_origen", 'jk_destino',create_using=nx.DiGraph() )
    
    # Plot it
    nx.draw(G, with_labels=True, font_size=8,node_size=1000, node_color='lightgrey',alpha=1, arrows=True, edge_color=df_grafo['p_jjkk'],
            edge_cmap=plt.cm.Oranges,pos=nx.nx_agraph.graphviz_layout(G, prog="neato"))
    
    #path=os.getcwd()+'/output/'+network.name+'/figure_digraph.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_digraph.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_digraph.png'

    plt.savefig(path, format='png', dpi=300, bbox_inches='tight')

def figure_digraph_complete(network):
    # GRAFICO
    # REPRESENTACIÓN DE LA RED
    # Los colores corresponden a LA PROPORCIÓN DE PACIENTES entre cada par de nodos.
    
    import pandas as pd
    import numpy as np
    import networkx as nx
    import matplotlib.pyplot as plt
    import os
    
    # Build a dataframe with 4 connections
    #df = pd.DataFrame({ 'from':['A', 'B', 'C','A'], 'to':['D', 'A', 'E','C']})
    
    df_grafo=network.file['df_arcos'].reset_index().copy()
    df_grafo = df_grafo.loc[df_grafo['p_jjkk'] != 0]
    df_grafo['jk']= df_grafo['nombre_J']+df_grafo['servicio_K']
    df_grafo['jpkp']= df_grafo["nombre_Jp"]+df_grafo['servicio_Kp']
    
    # Build your graph
    G=nx.from_pandas_edgelist(df_grafo,"jk", 'jpkp',create_using=nx.DiGraph() )
    
    # Plot it
    nx.draw(G, with_labels=True, font_size=8,node_size=1000, node_color='lightgrey',alpha=1, arrows=True, edge_color=df_grafo['p_jjkk'],
            edge_cmap=plt.cm.Oranges,pos=nx.circular_layout(G))
    
    
    #path=os.getcwd()+'/output/'+network.name+'/figure_digraph_complete.png'
    plt.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_digraph_complete.png'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_digraph_complete.png'


    plt.savefig(path, format='png', dpi=300, bbox_inches='tight')
    
def figure_sankey(network):
    import re
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.io as io
    io.renderers.default='browser'
    from plotly.offline import plot
    import os 
    import plotly.express as px
    
    # GRAFICO sankey
    # Obtengo los nodos de la red en una lista
    # Obtengo los nombres de los nodos de demnada
    # Obtengo los nombres de los nodos de oferta
    # Uno las dos listas anteriores e una sola lista y la numero
    
    df_demanda=network.file['df_demanda']
    df_capac=network.file['df_capac']
    df_asignacion=network.file['df_asignacion']
    df_arcos=network.file['df_arcos']
    df_flujos_jkjk=network.file['df_flujos_jkjk']
    
    df_lista_nodos = df_demanda.reset_index()['nombre_I'].unique()    
    df_lista_nodos = pd.DataFrame(df_lista_nodos, columns=["Nodos"])
    _df_lista_nodos1 = df_capac.reset_index()['nombre_J']+df_capac.reset_index()['servicio_K']
    _df_lista_nodos1 = pd.DataFrame(_df_lista_nodos1, columns=["Nodos"])
    
    df_lista_nodos = pd.concat([df_lista_nodos, 
                                _df_lista_nodos1],
                               ignore_index=True)
    
    df_lista_nodos.reset_index(inplace=True)
    df_lista_nodos = df_lista_nodos.rename(columns = {'index':'Consecutivo'})
    df_lista_nodos['Posicion']=df_lista_nodos.apply(lambda row: re.findall(r'\d+', row['Nodos']),axis='columns')
    df_lista_nodos['Posicion']=df_lista_nodos.apply(lambda row: row['Posicion'] + ['00'] if len(row['Posicion'])==1 else row['Posicion'],axis='columns')
    df_lista_nodos['Posicion_y']=df_lista_nodos.apply(lambda row: row['Posicion'][0],axis='columns')
    df_lista_nodos['Posicion_x']=df_lista_nodos.apply(lambda row: row['Posicion'][1],axis='columns')
    df_lista_nodos['Posicion_y'] = df_lista_nodos['Posicion_y'].astype('int')
    df_lista_nodos['Posicion_x'] = df_lista_nodos['Posicion_x'].astype('int')
    
    # Normalizo las posiciones
    df_lista_nodos['Posicion_x_norm'] = (df_lista_nodos['Posicion_x']-df_lista_nodos['Posicion_x'].min()+0.1)/(df_lista_nodos['Posicion_x'].max()-df_lista_nodos['Posicion_x'].min()+0.1)
    df_lista_nodos['Posicion_y_norm'] = (df_lista_nodos['Posicion_y']-df_lista_nodos['Posicion_y'].min()+0.1)/(df_lista_nodos['Posicion_y'].max()-df_lista_nodos['Posicion_y'].min()+0.1)

    # Construyo una matriz con origen, destino y valor
    # Construcción para los flujos entre i y j (df_asignacion)
    prueba=df_asignacion[['nombre_I','nombre_J','servicio_K','prop_tao_ijk','tao_ijk']]
    prueba.loc[:, 'destino'] = prueba['nombre_J'] + prueba['servicio_K']
    prueba=prueba.drop(['nombre_J','servicio_K'],axis=1)
    prueba=prueba.rename(columns={'nombre_I':'origen','prop_tao_ijk':'flujo'})
    print ("avance")
    # Construcción para los flujos entre jk y jk
    prueba2=df_arcos.reset_index()[['nombre_J','servicio_K','nombre_Jp','servicio_Kp','p_jjkk']]
    prueba2['origen']=prueba2['nombre_J']+prueba2['servicio_K']
    prueba2['destino']=prueba2['nombre_Jp']+prueba2['servicio_Kp']
    prueba2=prueba2[['origen','destino','p_jjkk']]
    prueba2=prueba2.rename(columns={'p_jjkk':'flujo'})
    prueba=pd.concat([prueba, prueba2])

    #Combino prueba y df_lista_nodos para obtener los flujos numerados
    prueba=pd.merge(prueba,df_lista_nodos,left_on='origen',right_on="Nodos")
    prueba=pd.merge(prueba,df_lista_nodos[['Nodos','Consecutivo']],left_on='destino',right_on="Nodos",how='left')

    #Incluyo los datos de df_flujos_jkjk
    df_flujos_jkjk=df_flujos_jkjk.set_index(['jk_origen','jk_destino'])
    prueba=pd.merge(prueba,df_flujos_jkjk[['lambdas*probs']],left_on=['origen','destino'],right_index=True,how='left')
    prueba.fillna(0,inplace=True)
    prueba['lambdas*probs']=prueba['tao_ijk']+prueba['lambdas*probs']
    
    #Incluyo columnas con los valores de k origen y k destino
    prueba['k_origen']=prueba.apply(lambda row: re.findall(r'k\d+', row['origen']),axis='columns')
    prueba['k_destino']=prueba.apply(lambda row: re.findall(r'k\d+', row['destino']),axis='columns')
    prueba['k_origen']=prueba.apply(lambda row: row['k_origen'][0] if len(row['k_origen'])==1 else row['Nodos_x'] ,axis='columns')
    prueba['k_destino']=prueba.apply(lambda row: row['k_destino'][0],axis='columns')




    #https://plotly.com/python/sankey-diagram/
    # Construyo gráfico con flujos en términos de proporciones o flujos
    
    # Si necesito gráfico para un k específico, quito el comentario siguiente:
    #prueba=prueba[(prueba['k_origen']=="k02") ]#| (prueba['k_destino']=="k02")]
    #prueba=prueba[(prueba['k_origen']=="k01") | (prueba['k_origen']=="i01") | (prueba['k_destino']=="k01")]
    
    fig = go.Figure(data=[go.Sankey(
        arrangement = "freeform", 
        textfont = {"size":20},
        node = {

          "pad" : 20, # Espacio entre nodos
          "thickness" : 20, #Ancho de cada nodo
          #line = dict(color = "black", width = 0.5), #Línea de cada nodo
          "label" : df_lista_nodos['Nodos'].tolist(), #label = ["i1", "i2", "i3", "i4", "j1k1", "j1k2" , "j1k3"],
          "x": df_lista_nodos['Posicion_x_norm'],
          "y": df_lista_nodos['Posicion_y_norm'],
          #color = "blue"
        },
         link = {
          "source":prueba['Consecutivo_x'].tolist(),        
          "target":prueba['Consecutivo_y'].tolist(),
          #"value":prueba['flujo'].tolist()
          "value":prueba['lambdas*probs'].tolist(),
             "arrowlen":15

            #source = [0,1], # indices correspond to labels, eg A1, A2, A1, B1, ...
            #target = [4,2], 
          #value = [8,3]
        }
        )])

    fig.update_layout(title_text="Proporciones de flujo entre nodos", font_size=18,  width=2200, height=900, margin_t=200)
    fig.show()
    
    if network.name_solution == "solución_subóptima":
        path=os.getcwd()+'/output/'+'red_original'+'/figure_sankey.html'
    else:
        path=os.getcwd()+'/output/'+network.name_solution+'/figure_sankey.html'

    
    fig.write_html(path)

#%% <codecell> main


if __name__ == "__main__":
    import hcndp
    from hcndp import network_data
    from hcndp.read_data import read_file_excel
    from hcndp.network_data import _I,_J,_K,_archivo 
    from hcndp.figures import figure_network_cartesian
    import os 
    network=network_data.Network(_I,_J,_K,_archivo)
    path=os.path.dirname(os.getcwd())+'/data/'+network.archivo
    path=os.getcwd()+'/data/'+network.archivo
    read_file_excel(network,path)
    #read_data.read_parameters(network)
    read_file_excel(network,path)
    hcndp.read_data.delete_surplus_data(network)
    hcndp.read_data.merge_niveles_capac(network)
    hcndp.read_data.create_df_asignacion(network)
    hcndp.read_data.create_df_probs_kk(network)
    hcndp.read_data.create_df_arcos(network)
    
    figure_network_cartesian(network)
    #figure_chord_diagram(network)
    figure_Lq_per_node(network)
    figure_rho_per_node(network)
