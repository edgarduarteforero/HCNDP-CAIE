# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 17:57:21 2024

@author: edgar
"""

import subprocess

'''
Este código permite ejecutar main.py sin que el usuario tenga que 
ingresar las instrucciones por teclado. 
En la variable inputs se almacena la secuencia de caracteres. 
\n hace referencia a un enter.
'''

# Definir las entradas simuladas
inputs = "3\n5\nCualquier tecla"
#                 I  J  K 
inputs = "\ny\n1\n7\n7\n5\n3\n\n1\n2\n1\n1\n\n2\n2\n1\n\n4\n1\n5\n5\n10\n4\n2\n5\n5\n10\n9\n10\n"

# Ejecutar el script opciones.py y pasar las entradas simuladas como entrada estándar
process = subprocess.Popen(["python", "main.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate(inputs)

# Imprimir la salida del script
print(stdout)

# Manejar errores si es necesario
if stderr:
    print("Error:", stderr)
    