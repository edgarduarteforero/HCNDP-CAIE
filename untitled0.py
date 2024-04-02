# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 08:02:12 2024

@author: edgar
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


# Leer el archivo de Excel
archivo=os.getcwd()+"/tests/20240319_Experimento.xlsx"
#archivo_excel = 'C:\Users\edgar\OneDrive - Universidad Libre\Doctorado\Códigos Python\HcNDP\Health-Care-Network-Design-Problem\tests\20240319_Experimento.xlsx'  # Cambia esto al nombre de tu archivo Excel
nombre_hoja = 'Hoja1'
datos_excel = pd.read_excel(archivo, sheet_name=nombre_hoja)

# Extraer las tres variables
variable_x = datos_excel['Variable_X']
variable_y = datos_excel['Variable_Y']
variable_z = datos_excel['Variable_Z']

# Crear el scatter plot
plt.figure(figsize=(8, 6))
plt.scatter(variable_x, variable_y, c=variable_z, cmap='viridis', alpha=0.75)
plt.colorbar(label='Variable Z')
plt.title('Scatter Plot de tres variables')
plt.xlabel('Variable X')
plt.ylabel('Variable Y')
plt.grid(True)
plt.show()
