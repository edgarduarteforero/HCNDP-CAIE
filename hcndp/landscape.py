# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:25:01 2024

@author: edgar
"""

# Este módulo realiza el análisis landscape para una búsqueda realizada 
# A fitness landscape corresponds to a graph where each vertex corresponds 
# to a solution in the search space, and edges represent the neighborhood 
# relations between the different solutions. (Tari & Ochoa, 2021)



# Construcción de la red de soluciones en NEtworkx
import networkx as nx

# Inicializar el grafo
G = nx.Graph()

def landscape(current_solution):
    # Se toma la lista landscape que se ha construido en una búsqueda
    # Tu lista de adyacencia
    lista=current_solution.landscape
    
    # Convertir las listas internas a tuplas o cadenas, para asegurarte de que son hashables
    for sublista in lista:
        nodo_principal = str(sublista[0][0])  # Convertir a cadena para mayor seguridad
        for vecino in sublista[1:]:
            vecino_nodo = str(vecino[0])  # Asegurarse de que es una cadena
            peso = round(vecino[1], 2)  # El peso puede ser un número
            # Agregar arista entre nodo_principal y vecino_nodo
            G.add_edge(nodo_principal, vecino_nodo, weight=peso)
            
    # Identificar el primer nodo (en este caso, el primer nodo principal)
    primer_nodo = str(lista[0][0][0])
    
    # Identificar el nodo con el peso más alto
    max_peso = -1
    nodo_max_peso = None
    for u, v, data in G.edges(data=True):
        if 'weight' in data and data['weight'] > max_peso:
            max_peso = data['weight']
            nodo_max_peso = v  # Se selecciona el nodo final con el mayor peso
    
    # Definir un color con transparencia (RGBA)
    # Aquí, el valor 'A' controla la transparencia (0.5 es semi-transparente)
    color_transparente = (0.3, 0.7, 0.9, 0.5)  # RGB más el valor alfa
    
    # Crear un diccionario para asignar colores a nodos
    color_map = {}
    for nodo in G.nodes:
        if nodo == primer_nodo:
            color_map[nodo] = 'green'  # El primer nodo debe ser verde
        # elif nodo == nodo_max_peso:
        #     color_map[nodo] = 'red'  # Nodo con el mayor peso debe ser rojo
        else:
            color_map[nodo] = color_transparente  # Otros nodos tienen un color neutro
            
    
    import matplotlib.pyplot as plt
    
    
    # Dibujar el grafo
    pos = nx.spring_layout(G)  # Elegir un layout para el gráfico
    nx.draw(G, pos, with_labels=False, node_size=50, 
            node_color=[color_map[nodo] for nodo in G.nodes],  # Asignar colores a los nodos
            edge_color='gray',
            font_size=10)
    
    # Dibujar etiquetas para los pesos de las aristas
    labels = nx.get_edge_attributes(G, 'weight')  # Obtener etiquetas de pesos
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels,
                                 label_pos=0.1,  # Cambiar la posición de las etiquetas
                                 font_size=4,  # Tamaño de fuente más pequeño
                                 font_color='black',  # Color de la fuente)
                                 )
    # Mostrar el gráfico
    plt.show()
    
    # Guardo el grafo construido dentro de current_solution
    current_solution.graph_landscape= G