# -*- coding: utf-8 -*-
"""

Created on Tue Mar 19 17:57:21 2024

@author: edgar
"""

import subprocess
import time
import os
import shutil
import re 
import winsound
import pandas as pd

'''
Este código permite ejecutar main.py sin que el usuario tenga que 
ingresar las instrucciones por teclado. 
En la variable inputs se almacena la secuencia de caracteres. 
\n hace referencia a un enter.
'''
# Características a revisar
# Tamaño de red IJK
# Metaheurística
# Operadores (Si LS o TS)
# Objetivos

lista_completa={}
lista_resultados=[]
min_I=3
max_I=6 #6
max_J=6 #6
min_K=3
max_K=6 #6
operadores=[1,2,3,4,5,6,7,8]
meta=[6] # 3:Local Search 4:Tabu Search 5: VND 6:GVND
obj=[1,2,3]

for K in range (min_K , max_K+1):
    for nodos in range (min_I , max_I+1):    
        I=nodos
        J=nodos
        #for operador in range (1,8+1): # Número de operadores (desde 1 hasta 8+1)
        #for operador in operadores:
        for metaheuristica in meta: #Número de metaheurísticas
                for objetivo in obj: #Objetivo de la función objetivo
                    # Definir las entradas simuladas
                    
                    inputs = (
                        "y\n"  # Borro resultados anteriores
                        "1\n"  # Escojo archivo .txt
                        f"{I}\n"  # I
                        f"{J}\n"  # J
                        f"{K}\n"  # K
                        "4\n"  # Continuar a crear red
                        "\n"  # Salto de línea vacío
                        "1\n"  # Problema mono-objetivo
                        "2\n"  # Obtener soluciones mono-objetivo
                        #"4\n"  # 3:Local Search 4:Tabu Search 5: VND 6:GVND
                        f"{metaheuristica}\n"  # 3:Local Search 4:Tabu Search 5: VND 6:GVND
                        #"2\n"  # 1 rho, 2 alpha 3 delta
                        f"{objetivo}\n" # Minimizar congestión máxima (rho)
                        #f"{operador}\n"  # Operador de permutación (agregado como f-string)
                        "\n" # Tecla para continuar
                        #"4\n"  # KPI
                        #"1\n"  # Escojo solución obtenida
                        #"10\n"  # No gráficos
                        "9\n"  # Salir
                        "10\n"  # Salir
                        )
            
                    # Marcar el inicio del tiempo CPU
                    #start_cpu_time = time.process_time()
                    start_cpu_time = time.perf_counter()
                    
                    # Ejecutar el script opciones.py y pasar las entradas simuladas como entrada estándar
                    process = subprocess.Popen(["python", "main.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate(inputs)
                    
                    # Imprimir la salida del script
                    #print(stdout)
                    
                    # Medir el tiempo CPU transcurrido
                    #cpu_time_elapsed = time.process_time() - start_cpu_time
                    cpu_time_elapsed = time.perf_counter() - start_cpu_time
                    #print (I,J,K,operador, metaheuristica,objetivo)                   
                    print (I,J,K, metaheuristica,objetivo)                   
                    print("CPU time transcurrido:", cpu_time_elapsed, "segundos")
                    
                    # Mover la carpeta de resultados a la carpeta tests
                    # Obtener la ruta del directorio actual
                    #ruta_actual = os.getcwd()
                    
                    # Rutas de origen y destino
                    #ruta_origen = os.path.join(ruta_actual, "output")
                    #ruta_destino = os.path.join(ruta_actual, "tests", "20240607 Experimento LS TS")
                    
                    # Asegurarte de que el destino existe
                    #if not os.path.exists(ruta_destino):
                    #    os.makedirs(ruta_destino)
                    
                    # Prefijo para las carpetas
                    #prefijo = str(I)+str(J)+str(K)+"_Oper_"+str(operador)+"_"#+str(metaheuristica)+"_"+str(objetivo)+"_"
                    #prefijo = str(I)+str(J)+str(K)+"_Oper_"+str(operador)+"_"+str(metaheuristica)+"_"+str(objetivo)+"_"
                    prefijo = str(I)+str(J)+str(K)+"_"+str(metaheuristica)+"_"+str(objetivo)+"_"

                    
                    # Traer datos de problems_dict para alimentar la salida del experimento
                    # Expresión regular para encontrar "Función objetivo: " seguido de números
                    _patron_fo = r"Valor función objetivo: (\d+\.\d+)"  # Capturar los números después del texto
                    _patron_operador = r"Operador: \s*(.*)"  # Captura todo el texto después de "operador: "
                    _patron_vecindario_final = r"Vecindario final número: \s*(.*)"  # Captura todo texto después "Vecindario final número: "
                    _patron_solucion_inicial = r"Valor función objetivo inicial: \s*(.*)"  # Captura todo texto después "Vecindario final número: "Valor función objetivo inicial:
                    
                    # Buscar todas las ocurrencias y extraer los valores
                    _valores_fo = re.findall(_patron_fo, stdout)  # Devuelve una lista de todos los valores encontrados
                    _valores_operador = re.findall(_patron_operador, stdout)  # Devuelve una lista de todos los valores encontrados
                    _valores_vecindario_final = re.findall(_patron_vecindario_final, stdout)  # Devuelve una lista de todos los valores encontrados
                    _valores_solucion_inicial = re.findall(_patron_solucion_inicial, stdout)  # Devuelve una lista de todos los valores encontrados
                    
                    if not _valores_fo:
                        _valores_fo = "nd"
                    if not _valores_operador :
                        _valores_operador = "nd"
                    if not _valores_vecindario_final :
                        _valores_vecindario_final  = "nd"
                    if not _valores_solucion_inicial:
                        _valores_solucion_inicial = "nd"
                    
                    lista_resultados=[_valores_vecindario_final[0],
                                             _valores_operador[0],
                                             _valores_fo[0],
                                             cpu_time_elapsed,
                                             _valores_solucion_inicial[0],
                                             str(metaheuristica),#
                                             str(objetivo),#
                                             #str(operador),#
                                             ]
                     
                    # Copiar todos los contenidos de "output"
                    #for item in os.listdir(ruta_origen):
                    #    item_path = os.path.join(ruta_origen, item)  # Ruta completa del elemento
                        
                    #    if os.path.isdir(item_path):
                            # Si es una carpeta, copiarla con el nuevo nombre
                    #        nuevo_nombre = prefijo + " " + item  # Agregar prefijo
                    #        nuevo_destino = os.path.join(ruta_destino, nuevo_nombre)
                            
                            # Mover el directorio completo con el nuevo nombre
                    #        shutil.move(item_path, nuevo_destino)
                    
                    #    elif os.path.isfile(item_path):
                            # Si es un archivo, copiarlo sin cambiar el nombre
                    #        shutil.copy2(item_path, ruta_destino)
                        
                    #print("Carpeta movida a:", ruta_destino)
            
                    #winsound.Beep(1000, 100)
            
                    #print (lista_resultados)
                    
                    
                    
                    #lista_completa[str(str(I)+str(J)+str(K)+str(_valores_operador[0]))] = lista_resultados
                    lista_completa[str(str(I)+str(J)+str(K)+"_"+str(_valores_operador[0]+"_"+str(metaheuristica)+"_"+str(objetivo)))] = lista_resultados
            
                    # _valores_vecindario_final,_valores_operador,_valores_fo,cpu_time_elapsed,solucion_inicial
                    
                    # Manejar errores si es necesario
                    if stderr:
                        print("Error:", stderr)
                
df_lista_completa = pd.DataFrame(lista_completa)
nombre_archivo = 'archivo_transpuesto.xlsx'
df_lista_completa.transpose().to_excel(nombre_archivo)


