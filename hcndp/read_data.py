# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:04:10 2023

@author: edgar
"""
def menu_select_file(I):
    import textwrap
    print (textwrap.dedent('''\
           Vamos a seleccionar el archivo con los datos de la red.
           
           Por defecto, HCNDP proporciona el archivo 
           datos_i16_j10_k10_base.xlsx ubicado en la carpeta \data\
               
           Puedes seguir utilizando ese archivo o definir tu propio archivo 
           de datos.
           
           '''))
    
    while True:
        print("Selecciona una opción:")
        print("1. Utilizar archivo existente datos_i16_j10_k10_base.xlsx ")
        print("2. Cargar nuevo archivo")
        if int(I) > 0:
            print("3. Continuar a crear red")

        opcion = input("Selecciona una opción: \n")

        if opcion == "1":
            print (textwrap.dedent(""" \
            Has seleccionado la Opción 1.
                  
            El archivo datos_i16_j10_k10_base.xlsx tiene estos parámetros:
            I = 16
            J = 10
            K = 10
            
            A continuación podrás actualizar estos parámetros.
            Se recomienda iniciar con una configuración así:
            I = 4
            J = 4
            K = 4                
            """))
            I,J,K,archivo= update_parameters()
            
        elif opcion == "2":
            print (textwrap.dedent(""" \
            \nHas seleccionado la Opción 2.
            Selecciona tu archivo desde la ventana emergente.
            """))
            
            I,J,K,archivo= select_external_file_explorer()
        
        elif opcion == "3":
            print("Volviendo al programa principal.")
            break
        
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")
    return I,J,K,archivo

def update_parameters():
    import textwrap
    import os
    I=16
    J=10
    K=10 
    archivo=os.getcwd()+'/data/red_original/'+"datos_i16_j10_k10_base.xlsx"
    
    # Indica la cantidad de nodos de origen
    print (f"La cantidad de nodos origen por defecto es {I}")
    I= input("Ingresa la cantidad de nodos origen: ") or I
    
    # Indica la cantidad de nodos de oferta
    print (f"La cantidad de nodos oferta por defecto es {J}")
    J= input("Ingresa la cantidad de nodos oferta: ") or J
    
    #Indica la cantidad de nodos de servicio
    print (f"La cantidad de servicios por defecto es {K}")
    K= input("Ingresa la cantidad de servicios: ") or K
    
    print (textwrap.dedent(f""" \
    \nParámetros actualizados:
    I={I}
    J={J}
    K={K}
     archivo = datos_i16_j10_k10_base.xlsx
     """))
           
    return I,J,K,archivo           

def select_external_file_explorer():
    import textwrap
    import tkinter as tk
    from tkinter import filedialog
    archivo = ""
    
    def seleccionar_archivo():
        nonlocal archivo
        archivo = filedialog.askopenfilename()
        label_resultado.config(text="Archivo seleccionado: " + archivo)
        print("Archivo seleccionado:", archivo)
        ventana.destroy()  # Cierra la ventana principal y permite continuar la ejecución
    
    # Crear una ventana principal
    ventana = tk.Tk()
    ventana.title("Seleccionar Archivo")
    
    # Crear un etiqueta para el texto interno
    etiqueta_texto = tk.Label(ventana, text="Selecciona un archivo:")
    etiqueta_texto.pack(pady=10)
    
    
    # Crear un botón que llame a la función seleccionar_archivo
    boton_seleccionar = tk.Button(ventana, 
                                  text="Seleccionar Archivo", 
                                  command=seleccionar_archivo)
    
    boton_seleccionar.pack(pady=10)
    
    # Crear una etiqueta para mostrar el resultado después de seleccionar el archivo
    label_resultado = tk.Label(ventana, text="")
    label_resultado.pack(pady=10)
    
    
    # Iniciar el bucle de eventos
    ventana.mainloop()
    
    
    I= input("Ingresa la cantidad de nodos origen: ")
    J= input("Ingresa la cantidad de nodos oferta: ")
    K= input("Ingresa la cantidad de servicios: ")
    
    print (textwrap.dedent(f""" \
    \nParámetros actualizados:
    I={I}
    J={J}
    K={K}
     archivo = datos_i16_j10_k10_base.xlsx
     """))
     
           
    return I,J,K,archivo


if __name__ == "__main__":
    pass
