# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 10:44:03 2024

@author: edgar
"""

import pandas as pd
import os

# Especificar las rutas de los archivos de entrada y salida
inputFile = os.getcwd()+'/data/red_original/datos_i04_j04_k10_base.xlsx'
outputFile = os.getcwd()+'/data/red_original/datos_i04_j04_k10_base.txt'


# Cargar el archivo Excel
xls = pd.ExcelFile(inputFile)

# Especificar las hojas que quieres procesar
hojas_a_convertir = ['df_oferta', 'df_capac', 'df_niveles',
                     'df_demanda','df_sigma_max','df_dist_ij_k',
                     'df_dist_ij','df_w_ij','flujos_jj','df_flujos_jkjk',
                     'df_flujos_ijk', 'prob_serv']  # Nombres de las hojas

# Abrir el archivo de salida
with open(outputFile, 'w', encoding='utf-8') as f:
    for hoja in hojas_a_convertir:
        if hoja in xls.sheet_names:
            # Leer la hoja como un DataFrame
            df = pd.read_excel(xls, sheet_name=hoja)
            
            # Escribir el encabezado para la hoja
            f.write(f"# {hoja}\n")
            
            # Guardar la hoja en el archivo de texto
            df.to_csv(f, sep=' ', index=False, header=True)  # Puedes cambiar el delimitador
