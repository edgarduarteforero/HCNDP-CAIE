# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 10:17:30 2024

@author: edgar
"""

# Ruta del archivo .txt que deseas depurar
file_path = "data/red_original/datos_i10_j10_k10_base_test.txt"

# Cadena de texto que deseas buscar para eliminar líneas
cadena_a_eliminar = [#"j05",
                     #"j06",
                     #"j07",
                     #"j08",
                     #"j09",
                     #"j10",
                     "j11",
                     "j12",
                     "j13",
                     "j14",
                     "j15",
                     "j16",
                     
                    #"i05",
                    #"i06",
                    #"i07",
                    #"i08",
                    #"i09",
                    #"i10",
                    "i11",
                    "i12",
                    "i13",
                    "i14",
                    "i15",
                    "i16",
                     
                    #"k06",
                    #"k07",
                    #"k08",
                    #"k09",
                    #"k10",
                     
                     ]

try:
    # Leer el archivo línea por línea
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Filtrar líneas que no contienen la cadena
    filtered_lines = []
    for line in lines:
        # Si la línea comienza con #, agregar una línea en blanco después
        if line.strip().startswith('#'):
            filtered_lines.append('\n')
        # Eliminar las líneas que contengan las cadenas a eliminar o que estén en blanco
        if not any(cadena in line for cadena in cadena_a_eliminar) and line.strip():
            filtered_lines.append(line)


    # Sobrescribir el archivo con las líneas filtradas
    with open(file_path, "w") as file:
        file.writelines(filtered_lines)

    print(f"Líneas que contienen '{cadena_a_eliminar}' fueron eliminadas exitosamente.")

except FileNotFoundError:
    print(f"El archivo {file_path} no fue encontrado.")
except Exception as e:
    print(f"Ocurrió un error: {e}")