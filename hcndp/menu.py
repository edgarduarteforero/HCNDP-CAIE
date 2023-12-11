# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:45:27 2023

@author: edgar
"""


def show_menu_main(network):
    while True:
        print("\n----------------------------------------------------------")
        print("Bienvenido al aplicativo HealthCare Network Design Problem")
        print("----------------------------------------------------------\n")
        print("Selecciona una opción:")
        print("1. Cargar datos")
        print("2. Representación de la red")
        print("3. Calcular medidas de desempeño")
        print("4. Solución del problema (Pendiente)")
        print("5. Salir")

        opcion = input("Selecciona una opción: \n")

        if opcion == "1":
            print("Has seleccionado la Opción 1.")
            show_menu_read_data(network)
            
        elif opcion == "2":
            print("Has seleccionado la Opción 2.")
            show_menu_show_network(network)
            
        elif opcion == "3":
            print("Has seleccionado la Opción 3.")
            calculate_kpi(network)
            
        elif opcion == "4":
            print("Has seleccionado la Opción 4.")
            
        elif opcion == "5":
            print("Saliendo del programa.")
            break
        
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")

def show_menu_read_data(network):
    from hcndp import read_data
    import os
    path=os.getcwd()+'/data/'+network.archivo
    
    while True:
        print("\n----------------------------------------------------------")
        print("Cargue de datos")
        print("----------------------------------------------------------\n")
        
        print("1. Importar datos desde Excel")
        print("2. Ingresar datos manualmente (Pendiente)")
        print("3. Regresar al menú principal")
        opcion1 = input("Selecciona una opción: \n")
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            read_data.read_parameters(network)
            read_data.read_file_excel(network,path)
            read_data.delete_surplus_data(network)
            read_data.merge_niveles_capac(network)
            read_data.create_df_asignacion(network)
            read_data.create_df_probs_kk(network)
            read_data.create_df_arcos(network)
            
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")
            read_data.data_by_hand()
        elif opcion1 == "3":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


def show_menu_show_network(network):
    from hcndp import figures
    while True:
        print("\n----------------------------------------------------------")
        print("Representaciones de la red")
        print("----------------------------------------------------------\n")
        
        print("1. Plano cartesiano")
        print("2. Chord diagram")
        print("3. Salir")
        opcion1 = input("Selecciona una opción: \n")
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            figures.figure_network_cartesian(network)
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")
            figures.figure_chord_diagram(network)
        elif opcion1 == "3":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def calculate_kpi(network):
    from hcndp import kpi
    kpi.set_lambda_jk(network)
        

if __name__ == "__main__":
    from main import I,J,K
    print (I)
    
            
            