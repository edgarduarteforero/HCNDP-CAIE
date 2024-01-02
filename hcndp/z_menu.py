# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:45:27 2023

@author: edgar
"""

def show_menu_main(network,networks):
    while True:
        print("\n----------------------------------------------------------")
        print("Bienvenido al aplicativo HealthCare Network Design Problem")
        print("----------------------------------------------------------\n")
        print("Selecciona una opción:")
        print("1. Cargar datos")
        print("2. Representación de la red")
        print("3. Calcular medidas de desempeño")
        print("4. Solución del problema (Pendiente)")
        print("5. Exportar a Excel")
        print("6. Exportar a data.dat")
        print("7. Optimización exacta")
        print("9. Salir")

        opcion = input("Selecciona una opción: \n")

        if opcion == "1":
            print("Has seleccionado la Opción 1.")
            show_menu_read_data(network)
            
        elif opcion == "2":
            print("Has seleccionado la Opción 2.")
            show_menu_figures(network)
            
        elif opcion == "3":
            print("Has seleccionado la Opción 3.")
            calculate_kpi(network)
            
        elif opcion == "4":
            print("Has seleccionado la Opción 4.")
        
        elif opcion == "5":
            print("Has seleccionado la Opción 5.")
            export_to_excel(network)
        
        elif opcion == "6":
            print("Has seleccionado la Opción 6.")
            export_data_dat(network)
        
        elif opcion == "7":
            print("Has seleccionado la Opción 7.")
            exact_optimization(network,networks)
        
        elif opcion == "9":
            print("Saliendo del programa.")
            break
        
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")

#%% <codecell> Cargar datos

def show_menu_read_data(network):
    from hcndp import read_data
    import os
    path=os.getcwd()+'/data/'+network.name+'/'+network.archivo
    
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
            read_data.merge_niveles_capac(network,post_optima=False)
            read_data.create_df_asignacion(network,post_optima=False)
            read_data.create_df_probs_kk(network)
            read_data.create_df_arcos(network,post_optima=False)
            
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")
            read_data.data_by_hand()
        elif opcion1 == "3":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")
#%% <codecell> Representación de la red
def show_menu_figures(network):
    from hcndp import figures
    while True:
        print("\n----------------------------------------------------------")
        print("Representaciones de la red")
        print("----------------------------------------------------------\n")
        print(" 1. Plano cartesiano")
        print(" 2. Chord diagram")
        print(" 3. Probabilidades de x clientes en espera")
        print(" 4. Probabilidades de esperar t tiempo")
        print(" 5. Longitud de cola y tiempo en espera por nodo")
        print(" 6. Plano cartesiano nodos y cobertura")
        print(" 7. Distancias gaussianas")
        print(" 8. Accesibilidad en cartesiano, mapa de calor y nodos")
        print(" 9. Flujos entre ik y jk")
        print("10. Salir")
        opcion1 = input("Selecciona una opción: \n")
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            try:     
                figures.figure_network_cartesian(network)
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has importado los datos.")
        
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")
            try: 
                figures.figure_chord_diagram(network)
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has importado los datos.")
        
        elif opcion1 == "3":
            print("Has seleccionado la Opción 3.")
            try:
                figures.figure_prob_custom_queue(network)    
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
                
        elif opcion1 == "4":
            print("Has seleccionado la Opción 4.")
            try:
                figures.figure_prob_time_in_queue(network)    
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
        
        elif opcion1 == "5":
            print("Has seleccionado la Opción 5.")
            try:
                figures.figure_Lq_per_node(network)
                figures.figure_Wq_per_node(network)
                figures.figure_service_rate_per_node(network)
                figures.figure_rho_per_node(network)
                figures.figure_rho_weighted(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
            
        elif opcion1 == "6":
            print("Has seleccionado la Opción 6.")
            try:
                figures.figure_nodes_coverage(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
            
        elif opcion1 == "7":
            print("Has seleccionado la Opción 7.")
            try:
                figures.figure_gaussian(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
        
        elif opcion1 == "8":
            print("Has seleccionado la Opción 8.")
            try:
                figures.figure_accessibility(network)
                figures.figure_heatmap_accessibility(network)
                figures.figure_accessibility_per_node(network)
                figures.figure_accessibility_per_service(network)
                
            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
         
        elif opcion1 == "9":
            print("Has seleccionado la Opción 9.")
            try:
                figures.figure_flows_f_ijk(network) 
                figures.figure_flows_f_ijk_k1(network)
                figures.figure_flows_f_ijkjk(network)
                figures.figure_flows_f_jpkpjk(network)
                figures.figure_digraph(network)
                figures.figure_digraph_complete(network)
                figures.figure_sankey(network)

            except AssertionError as error:
                print(error)
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has obtenido los KPI.")
         
        elif opcion1 == "10":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

#%% <codecell> Calcular medidas de desempeño
def calculate_kpi(network):
    from hcndp import kpi
    kpi.set_lambda_jk(network)
    kpi.set_lambda_ijk(network)
    kpi.set_phi_ijkjk(network)
    kpi.set_prop_tao(network)
    kpi.set_prob_k(network)
    
    print("Uno de los KPI consiste en la probabilidad de tener x clientes o menos en cola.")
    customers = int(input("Ingresa un valor para clientes: \n"))
    kpi.set_prob_custom_queue(network,customers)
    network.file['customers']=customers
    
    print("Uno de los KPI consiste en la probabilidad de esperar t o menos tiempo en cola.")
    time = int(input("Ingresa un valor para t: \n"))
    kpi.set_prob_wait_time (network,time)
    network.file['time']=time
    
    kpi.set_kpi_per_node(network)
    kpi.set_e2sfca(network)
    kpi.set_accessibility_per_node(network)
    kpi.set_accessibility_per_service(network)
    kpi.set_continuity_per_node(network)
    kpi.set_kpi_network(network)
    kpi.set_df_grafo_flujo_jkjk(network)

#%% <codecell> Exportar a Excel
def export_to_excel(network):
    from hcndp import export
    export.export_data(network)
    export.create_index_sheet(network)

#%% <codecell> Exportar a data.dat
def export_data_dat(network):
    from hcndp import export
    export.create_data_dat(network)

#%% <codecell> Optimizacion exacta
def exact_optimization(network,networks):
    while True:
        print("\n----------------------------------------------------------")
        print("Optimización exacta")
        print("----------------------------------------------------------\n")
        print("1. Optimización mono-objetivo")
        print("2. Representación de la red")
        print("3. Calcular medidas de desempeño")
        print("5. Exportar a Excel")
        print("6. Exportar a data.dat")

        print("2. Optimización multi-objetivo")
        print("3. Construir instancia")
        print("4. Definir solver")
        print("5. Generar optimización")
        print("6. Exportar resultados")
        print("x. Análisis de solución obtenida")
        print("7. Regresar al menú anterior")
        
        opcion1 = input("Selecciona una opción: \n")               
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            mono_objective_optima(network,networks)
            
        elif opcion1 == "2":
            print("Has seleccionado la Opción 2.")         

        elif opcion1 == "3":
            print("Has seleccionado la Opción 3.")
            
        elif opcion1 == "4":
            print("Has seleccionado la Opción 4.")
            
        elif opcion1 == "5":
            print("Has seleccionado la Opción 5.")
            
        elif opcion1 == "6":
            print("Has seleccionado la Opción 6.")
            
        elif opcion1 == "7":
            print("Has seleccionado la Opción 7.")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")

#%% <codecell> Optimización monobjetivo
def mono_objective_optima(network,networks):
    def get_objective_function(network):
        _menu_options = {
        '1': 'Minimizar congestión máxima (rho)',
        '2': 'Maximizar accesibilidad mínima (alpha)',
        '3': 'Maximizar continuidad mínimia (delta)',
        '4': 'Maximizar accesibilidad total (alpha)',
        '5': 'Minimizar usuarios en espera total (Lq_total)',
        '6': 'Maximizar continuidad total (delta total)',       
        '7': 'Salir al menú anterior'
        }   
        while True:
            print("\n----------------------------------------------------------")
            print("Selección de la función objetivo")
            print("----------------------------------------------------------\n")
            print("Definir función objetivo:")
            for i,j in _menu_options.items():
                print (f"{i}. {j}")            
            objective = int (input("Selecciona una opción: \n"))
            if 1 <= objective <= 6:
                return objective
            elif objective == "7":
              break
            else:
                print("Opción no válida. Inténtalo de nuevo.")
            
    def calculate_exact_optima(network,objective,networks) :
        from hcndp import optima
        from hcndp import network_data
        from hcndp.network_data import _I,_J,_K,_archivo,_name_network,_models

        _menu_options = {
        '1': 'Minimizar congestión máxima (rho)',
        '2': 'Maximizar accesibilidad mínima (alpha)',
        '3': 'Maximizar continuidad mínimia (delta)',
        '4': 'Maximizar accesibilidad total (alpha)',
        '5': 'Minimizar usuarios en espera total (Lq_total)',
        '6': 'Maximizar continuidad total (delta total)',
        '7': 'Salir al menú anterior'
        }
        _name=str(f"objective_{_menu_options[str(objective)]}")
        optima.set_model_abstract(objetivo=objective,
                                  nombre_modelo=_name,
                                  _menu_options=_menu_options,
                                  network=network,
                                  networks=networks)
        model=network.models[_name]
        optima.read_data_dat(network,model)
        optima.set_instance(model.model_abstract , model.data_dat, objective, model)
        if objective == 5:
            optima.solve_ipopt(network, model,model.instance)
        else:
            optima.solve_gurobi(network, model,model.instance)          
        optima.get_degrees_freedom(model.instance)           
        optima.set_solution_excel(network, model.instance)
        optima.set_solution_txt(network, model.instance)
        
        # Actualizo la red original con una nueva red
        optima.update_solution_post_optima(original_network=network,
                                           new_network=networks[_name])

        
    objective = get_objective_function(network)
    calculate_exact_optima(network, objective, networks)
    



    
#%% <codecell> Exportar optimización a nuevo objeto


if __name__ == "__main__":
    from main import I,J,K
    print (I)
    
            
            