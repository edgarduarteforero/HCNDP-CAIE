# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 11:20:19 2024

@author: edgar
"""

#%% Mapas coropléticos
###############################################################################
"""

# Este código construye un mapa coroplético
# Está tomado de https://www.analyticsvidhya.com/blog/2021/09/how-to-visualise-data-in-maps-using-geopandas/
# No requiere shape files porque utiliza un mapa del mundo

import geopandas as gpd
import matplotlib.pyplot as plt

# Primero se brinda un ejemplo
# Datos de los ganadores de los Juegos Olímpicos 2021
# El dataset tiene país, disciplina, NOC, sexo
# Descargamos la base de datos de: https://github.com/sreedevigattu/olympics2021/blob/main/data/Teams.xlsx
import pandas as pd
df_teams = pd.read_excel("C:/Users/edgar/OneDrive - Universidad Libre/Doctorado/Códigos Python/HcNDP/Health-Care-Network-Design-Problem/data/Teams.xlsx")
print(df_teams.info())
print(df_teams.head())

df_teams_countries_disciplines = df_teams.groupby(by="NOC").agg({'Discipline':'count'}).reset_index().sort_values(by='Discipline', ascending=False)
ax = df_teams_countries_disciplines.plot.bar(x='NOC', xlabel = '', figsize=(20,8))
ax

# Importamos Geopandas
import geopandas as gpd
# Este mapa base viene por defecto con geopandas. Tiene los límites de los países del mundo
df_world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

print(f"{type(df_world)}, {df_world.geometry.name}")
print(df_world.head())
print(df_world.geometry.geom_type.value_counts())


# Imprimimos el mapa que está cargado en df_world
#df_world.plot(figsize=(10,6))

# Hago un merge del mapa mundial(df_world) con mi dataset de los juegos olímpicos
df_world_teams = df_world.merge(df_teams_countries_disciplines, how="left", left_on=['name'], right_on=['NOC'])
print("Type of DataFrame : ", type(df_world_teams), df_world_teams.shape[0])
df_world_teams.head()

# Imprimo un mapa con los límites únicamente
#ax = df_world["geometry"].boundary.plot(figsize=(20,16))

# Mapa coroplético
#df_world_teams.plot( column="Discipline", ax=ax, cmap='OrRd', 
#                     legend=True, legend_kwds={"label": "Participation", "orientation":"horizontal"})
#ax.set_title("Countries Vs Number of Disciplines Particpated in 2021 Olympics")

from mpl_toolkits.axes_grid1 import make_axes_locatable

fig, ax = plt.subplots(1, 1, figsize=(20, 16))
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="2%", pad="0.5%")

df_world_teams.plot(column="Discipline", ax=ax, cax=cax, cmap='OrRd',
legend=True, legend_kwds={"label": "Participation"})

df_world_teams.plot(column="Discipline", ax=ax, cax=cax, cmap='OrRd',
legend=True, legend_kwds={"label": "Participation"},
missing_kwds={'color': 'lightgrey'})
                    
# Dibujar los límites de los países
df_world_teams.boundary.plot(ax=ax, edgecolor='black')

"""



#%% Mapas Colombia - Departamento político
'''
###############################################################################
### El siguiente Código está basado en 
#https://towardsdatascience.com/plotting-maps-with-geopandas-428c97295a73


import geopandas as gpd
import matplotlib.pyplot as plt

# División política de Colombia
# Cargar el shapefile de los municipios de Colombia
# Cambia 'ruta_a_shapefile_colombia' por la ruta a tu archivo
# Shape file descargado desde https://www.colombiaenmapas.gov.co/
fig, ax = plt.subplots(1, 1, figsize=(12, 12),dpi=300)

gdf_colombia = gpd.read_file("C:/Users/edgar/OneDrive - Universidad Libre/Doctorado/Códigos Python/HcNDP/Health-Care-Network-Design-Problem/data/Servicio-610/Municipios_202406_shp/Municipios_202406_shp/Municipio, Distrito y Área no municipalizada.shp")
gdf_santander = gdf_colombia[gdf_colombia["Depto"] == "Santander"]

mapa_imprimir= gdf_santander
mapa_imprimir = mapa_imprimir.to_crs(epsg=4326)

mapa_imprimir.plot(column='MpArea', cmap='OrRd', legend=True, edgecolor='gray') 


plt.show()

'''


#%% Mapa Departamento Demanda

###############################################################################
### El siguiente Código está basado en 
#https://towardsdatascience.com/plotting-maps-with-geopandas-428c97295a73

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import math
import pandas as pd
# División política de Colombia
# Cargar el shapefile de los municipios de Colombia
fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=300)

gdf_colombia_poblacion = gpd.read_file("C:/Users/edgar/OneDrive - Universidad Libre/Doctorado/Códigos Python/HcNDP/Health-Care-Network-Design-Problem/data/SHP_MGN_ANM_MPIOS/MGN_ANM_MPIOS.shp",
                                       encoding='utf-8')
gdf_santander_poblacion = gdf_colombia_poblacion[gdf_colombia_poblacion["DPTO_CCDGO"] == "68"]
mapa_imprimir2 = gdf_santander_poblacion[["MPIO_CCDGO", "LATITUD","LONGITUD","MPIO_CNMBR", "MPIO_CDPMP", "STP27_PERS", "geometry"]]
mapa_imprimir2.loc[:, 'STP27_PERS'] = mapa_imprimir2['STP27_PERS'].astype(int)

# Añado datos de municipio
# [Código municipio, demanda mensual, servicios habilitados]
demanda=[
[68001,22,10],
[68077,1,1],
[68079,1,1],
[68081,11,10],
[68190,2,4],
[68211,1,1],
[68271,1,1],
[68276,8,10],
[68307,4,5],
[68397,1,1],
[68406,3,2],
[68432,1,1],
[68464,1,1],
[68498,1,1],
[68500,1,1],
[68547,2,10],
[68573,1,1],
[68575,3,3],
[68615,1,1],
[68655,1,1],
[68679,4,6],
[68689,2,4],
[68755,2,4],
[68770,1,1],
[68861,1,1],
[68895,1,1]]

df_demanda=pd.DataFrame(demanda,columns=["Cod_Mun","Dem","Servicios"])
df_demanda.loc[:, 'Cod_Mun'] = df_demanda['Cod_Mun'].astype(str)
df_demanda.loc[:, 'Servicios'] = df_demanda['Servicios'].astype(int)

mapa_imprimir2=mapa_imprimir2.merge(df_demanda,how='left',left_on="MPIO_CDPMP", right_on="Cod_Mun")

# Cambiar la proyección a EPSG:3857 (métrica para distancias en metros)
mapa_imprimir2 = mapa_imprimir2.to_crs(epsg=4326) #4326 3857

# # Añadir mapa de calor
# import numpy as np
# mapa_imprimir2['log_poblacion'] = np.log10(mapa_imprimir2['Dem'])

# import seaborn as sns
# sns.kdeplot(data=mapa_imprimir2,
#             x='LONGITUD', 
#             y='LATITUD', 
#             fill=True,
#             cmap="Reds", #'coolwarm',
#             alpha=0.8,  # Ajustar la transparencia
#             gridsize=500,  # Aumentar el tamaño de la cuadrícula
#             levels=20,  # Aumentar el número de niveles
#             bw_adjust=0.4,  # Ajustar el ancho de banda
#             weights=mapa_imprimir2['Dem'],  # Ponderar por población
#             ax=ax)

# Añadir barra de colores
# norm = plt.Normalize(vmin=mapa_imprimir2['Dem'].min(), vmax=mapa_imprimir2['Dem'].max())  # Establecer límites de la barra de color
# sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
# sm.set_array([])  # Crear un array vacío para la barra de color
# cbar = plt.colorbar(sm, ax=ax)
# cbar.set_label("User demand rate (user / month")  # Etiqueta de la barra de colores

# Graficar el mapa en el eje correcto (ax)
# mapa_imprimir2.plot(column='Dem', cmap='OrRd', legend=True, 
#                     legend_kwds={'title': "Population by quintiles"},
#                     scheme="quantiles", k=5, edgecolor='gray', linewidth=0.5,ax=ax)
mapa_imprimir2.plot(edgecolor='grey',facecolor='none', linewidth=0.5,  ax=ax)


# Quitar los rótulos de los ejes
ax.set_xticks([])  # Quitar las marcas en el eje X
ax.set_yticks([])  # Quitar las marcas en el eje Y

# Añadir la barra de escala ajustada a 100 km
ax.add_artist(ScaleBar(111,location='lower right', units='km', length_fraction=0.2))

# Añadir los puntos de las ciudades
# Asegúrate de que las columnas 'LATITUD' y 'LONGITUD' están en el gdf_santander_poblacion
# for index, row in mapa_imprimir2.iterrows():
#     if pd.notna(row['Dem']):
#         ax.plot(row['LONGITUD'], row['LATITUD'], 'o', color='black', markersize=3, alpha=0.5) #markersize=math.log(row['STP27_PERS'])
#     #ax.plot(row['LONGITUD'], row['LATITUD'], 'o', color='black', markersize=math.log(row['STP27_PERS'],3), alpha=0.5) #
    #ax.text(row['LONGITUD'], row['LATITUD'], row['MPIO_CNMBR'], fontsize=4, ha='right')

# Añadir datos a cada ciudad
# for index, row in mapa_imprimir2.iterrows():
#     if pd.notna(row['Servicios']):
#         # Obtener las coordenadas y el valor de Servicios
#         x, y = row['LONGITUD'], row['LATITUD']
#         servicios = int(row['Servicios'])
        
#         # Dibujar un círculo en la ubicación del municipio
#         circle = plt.Circle((x, y), 0.05, color='white', alpha=0.4, zorder=2)  # Puedes ajustar el radio según sea necesario
#         ax.add_artist(circle)
        
#         # Imprimir el número de servicios dentro del círculo
#         ax.text(x, y, servicios, fontsize=12, ha='right', va='bottom', zorder=3)


# Imprimir círculos alrededor de los nodos
import matplotlib.cm as cm

# Definir un rango de tamaño para los círculos
min_size = 10  # Tamaño mínimo del círculo
max_size = 100  # Tamaño máximo del círculo

# Normalizar los servicios para escalar el tamaño
max_servicios = mapa_imprimir2['Servicios'].max()
min_servicios = mapa_imprimir2['Servicios'].min()

for index, row in mapa_imprimir2.iterrows():
    if pd.notna(row['Dem']):
        # Obtener las coordenadas y el valor de Servicios
        x, y = row['LONGITUD'], row['LATITUD']
        demanda = int(row['Dem'])

        # Calcular el tamaño del círculo en función de los servicios
        #size = min_size + (max_size - min_size) * ((servicios - min_servicios) / (max_servicios - min_servicios))

        # Calcular el color en función de los servicios
        # color = cm.Greens((servicios - min_servicios) / (max_servicios - min_servicios))
        if demanda <= 5:
            color="Green"
        elif demanda<=15:
            color="Orange"
        else:
            color="Red"
        # Dibujar un círculo en la ubicación del municipio
        circle = plt.Circle((x, y), radius=0.08, color=color, alpha=0.6, zorder=2)  # Usa el tamaño calculado
        ax.add_artist(circle)

        # Imprimir el número de servicios dentro del círculo
        ax.text(x, y, demanda, fontsize=12, ha='center', va='center', zorder=3)

# Agregar leyenda
import matplotlib.patches as mpatches

# Crear círculos para la leyenda
circle1 = mpatches.Circle((0, 0), 0.05, color='red',  alpha=0.6, label='User/month > 15')
circle2 = mpatches.Circle((0, 0), 0.05, color='orange',  alpha=0.6, label='5 < User/month <=15')
circle3 = mpatches.Circle((0, 0), 0.05, color='green',  alpha=0.6, label='0 <= User/month <= 5')

# Agregar círculos a la leyenda
legend_handles = [circle1, circle2, circle3]

# Agregar la leyenda al gráfico
ax.legend(handles=legend_handles, loc='upper right', title='Demand rates')

# Añadir la flecha Norte ajustada
x_coord = -74.5
y_coord = 8
arrow_length = 0.25  # Ajusta el tamaño de la flecha25000

# Dibujar solo la flecha Norte
ax.annotate('N', xy=(x_coord, y_coord + arrow_length), xytext=(x_coord, y_coord),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', fontsize=12)

# Mostrar el mapa
plt.show()


#%% Mapa Departamento Capacidad

###############################################################################
### El siguiente Código está basado en 
#https://towardsdatascience.com/plotting-maps-with-geopandas-428c97295a73

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import math
import pandas as pd
# División política de Colombia
# Cargar el shapefile de los municipios de Colombia
fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=300)

gdf_colombia_poblacion = gpd.read_file("C:/Users/edgar/OneDrive - Universidad Libre/Doctorado/Códigos Python/HcNDP/Health-Care-Network-Design-Problem/data/SHP_MGN_ANM_MPIOS/MGN_ANM_MPIOS.shp",
                                       encoding='utf-8')
gdf_santander_poblacion = gdf_colombia_poblacion[gdf_colombia_poblacion["DPTO_CCDGO"] == "68"]
mapa_imprimir2 = gdf_santander_poblacion[["MPIO_CCDGO", "LATITUD","LONGITUD","MPIO_CNMBR", "MPIO_CDPMP", "STP27_PERS", "geometry"]]
mapa_imprimir2.loc[:, 'STP27_PERS'] = mapa_imprimir2['STP27_PERS'].astype(int)

# Añado datos de municipio
# [Código municipio, demanda mensual, servicios habilitados]
demanda=[
[68001,22,10],
[68077,1,1],
[68079,1,1],
[68081,11,10],
[68190,2,4],
[68211,1,1],
[68271,1,1],
[68276,8,10],
[68307,4,5],
[68397,1,1],
[68406,3,2],
[68432,1,1],
[68464,1,1],
[68498,1,1],
[68500,1,1],
[68547,2,10],
[68573,1,1],
[68575,3,3],
[68615,1,1],
[68655,1,1],
[68679,4,6],
[68689,2,4],
[68755,2,4],
[68770,1,1],
[68861,1,1],
[68895,1,1]]

df_demanda=pd.DataFrame(demanda,columns=["Cod_Mun","Dem","Servicios"])
df_demanda.loc[:, 'Cod_Mun'] = df_demanda['Cod_Mun'].astype(str)
df_demanda.loc[:, 'Servicios'] = df_demanda['Servicios'].astype(int)

mapa_imprimir2=mapa_imprimir2.merge(df_demanda,how='left',left_on="MPIO_CDPMP", right_on="Cod_Mun")

# Cambiar la proyección a EPSG:3857 (métrica para distancias en metros)
mapa_imprimir2 = mapa_imprimir2.to_crs(epsg=4326) #4326 3857

# # Añadir mapa de calor
# import numpy as np
# mapa_imprimir2['log_poblacion'] = np.log10(mapa_imprimir2['Dem'])

# import seaborn as sns
# sns.kdeplot(data=mapa_imprimir2,
#             x='LONGITUD', 
#             y='LATITUD', 
#             fill=True,
#             cmap="Reds", #'coolwarm',
#             alpha=0.8,  # Ajustar la transparencia
#             gridsize=500,  # Aumentar el tamaño de la cuadrícula
#             levels=20,  # Aumentar el número de niveles
#             bw_adjust=0.4,  # Ajustar el ancho de banda
#             weights=mapa_imprimir2['Dem'],  # Ponderar por población
#             ax=ax)

# Añadir barra de colores
# norm = plt.Normalize(vmin=mapa_imprimir2['Dem'].min(), vmax=mapa_imprimir2['Dem'].max())  # Establecer límites de la barra de color
# sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
# sm.set_array([])  # Crear un array vacío para la barra de color
# cbar = plt.colorbar(sm, ax=ax)
# cbar.set_label("User demand rate (user / month")  # Etiqueta de la barra de colores

# Graficar el mapa en el eje correcto (ax)
# mapa_imprimir2.plot(column='Dem', cmap='OrRd', legend=True, 
#                     legend_kwds={'title': "Population by quintiles"},
#                     scheme="quantiles", k=5, edgecolor='gray', linewidth=0.5,ax=ax)
mapa_imprimir2.plot(edgecolor='grey',facecolor='none', linewidth=0.5,  ax=ax)


# Quitar los rótulos de los ejes
ax.set_xticks([])  # Quitar las marcas en el eje X
ax.set_yticks([])  # Quitar las marcas en el eje Y

# Añadir la barra de escala ajustada a 100 km
ax.add_artist(ScaleBar(111,location='lower right', units='km', length_fraction=0.2))

# Añadir los puntos de las ciudades
# Asegúrate de que las columnas 'LATITUD' y 'LONGITUD' están en el gdf_santander_poblacion
# for index, row in mapa_imprimir2.iterrows():
#     if pd.notna(row['Dem']):
#         ax.plot(row['LONGITUD'], row['LATITUD'], 'o', color='black', markersize=3, alpha=0.5) #markersize=math.log(row['STP27_PERS'])
#     #ax.plot(row['LONGITUD'], row['LATITUD'], 'o', color='black', markersize=math.log(row['STP27_PERS'],3), alpha=0.5) #
    #ax.text(row['LONGITUD'], row['LATITUD'], row['MPIO_CNMBR'], fontsize=4, ha='right')

# Añadir datos a cada ciudad
# for index, row in mapa_imprimir2.iterrows():
#     if pd.notna(row['Servicios']):
#         # Obtener las coordenadas y el valor de Servicios
#         x, y = row['LONGITUD'], row['LATITUD']
#         servicios = int(row['Servicios'])
        
#         # Dibujar un círculo en la ubicación del municipio
#         circle = plt.Circle((x, y), 0.05, color='white', alpha=0.4, zorder=2)  # Puedes ajustar el radio según sea necesario
#         ax.add_artist(circle)
        
#         # Imprimir el número de servicios dentro del círculo
#         ax.text(x, y, servicios, fontsize=12, ha='right', va='bottom', zorder=3)


# Imprimir círculos alrededor de los nodos
import matplotlib.cm as cm

# Definir un rango de tamaño para los círculos
min_size = 10  # Tamaño mínimo del círculo
max_size = 100  # Tamaño máximo del círculo

# Normalizar los servicios para escalar el tamaño
max_servicios = mapa_imprimir2['Servicios'].max()
min_servicios = mapa_imprimir2['Servicios'].min()

for index, row in mapa_imprimir2.iterrows():
    if pd.notna(row['Servicios']):
        # Obtener las coordenadas y el valor de Servicios
        x, y = row['LONGITUD'], row['LATITUD']
        servicios = int(row['Servicios'])

        # Calcular el tamaño del círculo en función de los servicios
        #size = min_size + (max_size - min_size) * ((servicios - min_servicios) / (max_servicios - min_servicios))

        # Calcular el color en función de los servicios
        # color = cm.Greens((servicios - min_servicios) / (max_servicios - min_servicios))
        if servicios <= 3:
            color="Green"
        elif servicios<=7:
            color="Orange"
        else:
            color="Red"
        # Dibujar un círculo en la ubicación del municipio
        circle = plt.Circle((x, y), radius=0.08, color=color, alpha=0.6, zorder=2)  # Usa el tamaño calculado
        ax.add_artist(circle)

        # Imprimir el número de servicios dentro del círculo
        ax.text(x, y, servicios, fontsize=12, ha='center', va='center', zorder=3)

# Agregar leyenda
import matplotlib.patches as mpatches

# Crear círculos para la leyenda
circle1 = mpatches.Circle((0, 0), 0.05, color='red',  alpha=0.6, label='Enabled Services > 7')
circle2 = mpatches.Circle((0, 0), 0.05, color='orange',  alpha=0.6, label='3 < Enabled services <=7')
circle3 = mpatches.Circle((0, 0), 0.05, color='green',  alpha=0.6, label='0 <= Enabled services <=3')

# Agregar círculos a la leyenda
legend_handles = [circle1, circle2, circle3]

# Agregar la leyenda al gráfico
ax.legend(handles=legend_handles, loc='upper right', title='Enabled services')

# Añadir la flecha Norte ajustada
x_coord = -74.5
y_coord = 8
arrow_length = 0.25  # Ajusta el tamaño de la flecha25000

# Dibujar solo la flecha Norte
ax.annotate('N', xy=(x_coord, y_coord + arrow_length), xytext=(x_coord, y_coord),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', fontsize=12)

# Mostrar el mapa
plt.show()

