# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 17:42:37 2023

@author: edgar
"""

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
    asignacion=network.file['df_asignacion']
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
    #ax.grid()
    plt.show()
    #plt.pause(0.1) #Muestra imagen en pestaña Plots a medida que se ejecuta el código
    path=os.getcwd()+'/output/'+'network_cartesian.png'
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
    path=os.getcwd()+'/output/'

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



def figure_prob_custom_queue(network):
    # Construyo gráficos para representar las probabilidades de tener clientes en cola
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()
    
    df_capac=network.file['df_capac'].reset_index()

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
    path=os.getcwd()+'/output/'+str(customers)+'_prob_custom_queue.png'
    plt.savefig(path, dpi=300)
    
    
def figure_prob_time_in_queue(network):
    # Construyo gráficos para representar las probabilidades de tiempo en cola
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    plt.rcdefaults()

    df_capac=network.file['df_capac'].reset_index()

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
    path=os.getcwd()+'/output/'+str(time)+'prob_time_in_queue.png'
    plt.savefig(path, dpi=300)

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
    
    figure_network_cartesian(network)
    figure_chord_diagram(network)