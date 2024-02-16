# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:58:33 2023

@author: edgar
"""


def menu_solutions(network_original, problems_dict):
    import textwrap
    import pandas as pd
    import numpy as np
    
    while True:
        print("\n----------------------------------------------------------")
        print(f"Vamos a agregar soluciones a la red {network_original.name}.")
        print("menu_solutions@solutions.py")
        print("----------------------------------------------------------\n")
        print("Selecciona una opción:")
        print("1. Cargar tu propia solución")
        print("2. Obtener soluciones mono-objetivo")
        
        print("4. Indicadores (KPI) y gráficos de soluciones")
        print("9. Salir")

        opcion = input("Selecciona una opción: \n")

        def mostrar_soluciones(problems_dict):
            print("Selecciona una opción:")
            for i, (clave, descripcion) in enumerate(problems_dict.items(), start=1):
                print(f"{i}. {clave}")

        if opcion == "1":
            print("Has seleccionado la Opción 1.")
            print(textwrap.dedent(""" \
                  Vamos a ingresar tu propia solución.
                  Se utilizarán las variables sigma_jk, tao_ijk, z_ijk
                  del archivo de datos de excel.
                  Los flujos entre nodos de servicio 
                  se calculan dividiendo el flujo saliente de cada nodo 
                  en partes iguales. Consulta la matriz df_arcos."""))
            create_solution_object(
                network_original, problems_dict, name_solution="solución_subóptima")
            

            print("Se ha cargado tu solución propia.")
            input("Pulsa una tecla para continuar.")

        elif opcion == "2":
            print("Has seleccionado la Opción 2.")
            print(textwrap.dedent(""" \
                  Vamos a obtener soluciones mono-objetivo.
                  A continuación ingresarás a un menú para escoger
                  la función objetivo y el solver respectivo.
                  """))

            # Creo el objeto solution
            create_solution_object(
                network_original, problems_dict, name_solution="temporal")
            current_solution = problems_dict["temporal"]

            # Pido al usuario el objetivo
            current_solution.optimizar=True
            current_solution.menu_mono_optimization(new_network=current_solution.network_copy,
                                                     problems_dict=problems_dict,)
            
            # Se ha escogido optimización exacta
            if current_solution.optimizar==True and current_solution.tecnica=='Exacta':
                # Calculo la solución óptima
                #current_solution.calculate_exact_optima()                
                current_solution.construct_model()
                current_solution.construct_instance()
                current_solution.execute_solver()
            
                
            
            # Se ha escogido optimización Aproximada
            if current_solution.optimizar==True and current_solution.tecnica=="Aproximación":
                #Creo la representación de la red
                from hcndp import network
                network_repr=network.Network_representation(network_original.I,
                                                            network_original.J,
                                                            network_original.K,
                                                            network_original.archivo,
                                                            network_original.file)
                path_repr=network.Path_representation(network_original.K, 
                                                      network_original.archivo,
                                                      network_original.file)
                
                # Asignación de recurso σ_k para cada nodo de oferta j 
                for _k in path_repr.nodes_services.keys():
                    if _k !=  'k00':
                        #print ("Asignación de recursos para: ", _k)
                        network_repr.asignacion_recursos(path_repr,_k)
                        #for _i,_j in network.nodes_supply.items():
                         #   if _j.capac_instal_sigma != 0:
                                #print (_i,_j.capac_instal_sigma)
            
                
                # Para k=0 creo valores de λ_ijk0 
                # El valor de λ_ijk0 es igual a la demanda que hay en cada nodo ik0.
                for _,_j in network_repr.nodes_supply.items():
                    for _p,_i in _j.matriz_λ.iterrows():
                        if _i['nombre_I'].replace('i','j')==_i['nombre_J'] and _i['servicio_K']=='k00':
                            _j.matriz_λ.loc[_p, 'λ_ijk'] = network_repr.nodes_demand[_i['nombre_I']].demand
            
                # Construyo primera solución
                path_repr.edges_ser_ser_R=dict(sorted(path_repr.edges_ser_ser_R.items()))
                
                for _i in path_repr.edges_ser_ser_R.values():
                    k=_i.source
                    kp=_i.target
                
                    if k < kp:
                        network_repr.asignacion_flujos_δ(network_repr,path_repr,k)
                    
                        # Solución entre k y kp*
                        network_repr.solucion_entre_k_kp(network=network_repr,_k=k,
                                                         _kp=kp,
                                                         archivo=network_original.file)
                        network_repr.obtencion_π(network_repr,k,kp)
                        network_repr.construyo_λ(network_repr,kp)
                
                    elif k == kp:
                        network_repr.asignacion_π_ciclos(network_repr,k,kp)
                
                    elif k > kp:
                        network_repr.asignacion_π_ciclos(network_repr,kp,k)
                    
                
                
                # Construyo una matriz g con los arribos externos, es decir los ϕi.j.k0jk
                from hcndp.data_functions import indices

                _lista_i=indices("i",network_original.I)
                _lista_j=indices("j",network_original.J)
                _lista_k=indices("k",network_original.K)
                
                #_lista_k_00=_lista_k
                #_lista_k_00.append('k00')
                from itertools import product
                _lista = list(product(_lista_i, _lista_j,_lista_k))
                _g=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
                _g['tao_ijk'] = 0.0
                _g=_g.sort_values(by=['nombre_I', 'nombre_J','servicio_K'])
                
                def arribos_externos(poblacion_origen,servicio_origen,nodo_destino):
                    suma_acumulativa=0
                    for clave,valor in network_repr.edges_sup_sup_X.items():
                        if valor.node_demand_pop == poblacion_origen and valor.service_source==servicio_origen and valor.target==nodo_destino :
                            suma_acumulativa += valor.flow_sup_sup_phi
                    return suma_acumulativa
                    
                _g['tao_ijk']=_g.apply (lambda row: arribos_externos(row['nombre_I'],'k00',row['nombre_J']+row['servicio_K']),axis=1)
                _g=np.array(_g['tao_ijk']) # Lista de arribos externos ijk
                _g=np.reshape(_g,([network_original.I,network_original.J*(network_original.K)])) # Matriz de arribos externos de i por (jk)
                
                
                # Construyo las matrices con las probabilidades π  
                _lista = list(product(_lista_i, _lista_j,_lista_k,_lista_j,_lista_k))
                _π=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K', 'nombre_Jp','servicio_Kp'])
                _π['π_ijkjk'] = 0.0   
                _π=_π.sort_values(by=['nombre_I','nombre_J', 'servicio_K','nombre_Jp','servicio_Kp'])
                _π['p*π'] = 0.0
                
                for _,_fila in _π.iterrows():
                    _i=_fila['nombre_I']
                    _j=_fila['nombre_J']
                    _k=_fila['servicio_K']
                    _jp=_fila['nombre_Jp']
                    _kp=_fila['servicio_Kp']
                    for _nombre,_arco in network_repr.edges_sup_sup_X.items():
                        if  _nombre == _i+_j+_k+_jp+_kp:
                            _π.loc[_,'π_ijkjk'] = _arco.flow_sup_sup_perc
                    
                    for _nombre,_arco in path_repr.edges_ser_ser_R.items():
                        if  _nombre == _k+_kp:
                            _π.loc[_,'p*π'] = _arco.transfer_percentage  * _π.loc[_,'π_ijkjk']
               
                    
               
                # Calculo los flujos entrantes lambda ijk basado en redes de Jackson
                _lista = list(product(_lista_i, _lista_j,_lista_k))
                _df_asignacion=pd.DataFrame(_lista, columns=['nombre_I', 'nombre_J','servicio_K'])
                _df_asignacion["lambda_ijk"] = 0.0
                _df_asignacion=_df_asignacion.sort_values(by=['nombre_I','nombre_J', 'servicio_K'])
                _df_asignacion.set_index(['nombre_I', 'nombre_J','servicio_K'],inplace=True)
                #Para cada i cálculo el lambda ijk
                _fila=0
                for i in _lista_i:
                    probs=_π.loc[(_π['nombre_I']==_lista_i[_fila])]
                    probs=probs.sort_values(by=['nombre_J', 'servicio_K','nombre_Jp','servicio_Kp'])
                    #probs=np.array(probs['π_ijkjk'])
                    probs=np.array(probs['p*π'])
                    probs=np.reshape(probs,([network_original.J*(network_original.K),network_original.J*(network_original.K)]))
                    _df_asignacion.loc[i,'lambda_ijk']=np.matmul(_g[_fila],np.linalg.inv(np.identity(len(probs))-(probs)))
                    _fila+=1
                
                for _,_j in network_repr.nodes_supply.items():
                    if _j.service!='k00':
                        _j.matriz_λ=_df_asignacion.loc[(slice(None),_j.place,_j.service),:]
                        _j.matriz_λ.reset_index(inplace=True)
                        _j.matriz_λ = _j.matriz_λ.rename(columns={'lambda_ijk': 'λ_ijk'})
                
                # Actualizo el df_asignacion en network
                network_repr.df_asignacion=_df_asignacion
                
                # Llevar solución a un df_solucion
                _lista=[] 
                for _i,_j in network_repr.edges_sup_sup_X.items():
                    _lista.append([_j.node_demand_pop,_j.source,_j.target,_j.flow_sup_sup_perc,_j.flow_sup_sup_phi])
                df_solucion = pd.DataFrame(_lista, columns=['nombre_I', 'origen', 'destino','π','ϕ'])
                
                current_solution.solution=df_solucion
                print (df_solucion)
                # %% Exportar resultados 
                # TODO Generar solución en el mismo formato que la solución exacta
                #current_solution.network_copy.create_folders()
                #current_solution.set_solution_excel()
                #current_solution.set_solution_txt()
                
                
            input("Pulsa una tecla para continuar.")






        # elif opcion == "3":
        #     print("Has seleccionado la Opción 3.")
        #     calculate_kpi(network)

        elif opcion == "4":
            print("\nHas seleccionado la Opción 4.")
            print("\n----------------------------------------------------------")
            print ("KPI de soluciones y gráficos.")
            print("\n----------------------------------------------------------")
            print ("Estas son las soluciones construidas:/n")
            
            # Listar las soluciones existentes
            mostrar_soluciones(problems_dict)

            # Obtener la elección del usuario
            try:
                from hcndp import kpi
                from hcndp import figures
                from hcndp import export
                
                numero_elegido = int(input("Ingresa el número de la solución elegida: "))
                solucion_elegida = list(problems_dict.keys())[numero_elegido - 1]
                
                # Realizar el procedimiento con la opción seleccionada
                print(f"\nRealizando el procedimiento para la opción: {solucion_elegida}")
                current_solution=problems_dict[solucion_elegida]
                
                if current_solution.objective=="Nulo":
                    # Si no hay función objetivo (Solución ingresada por usuario)
                    _post_optima=False
                    kpi.calculate_kpi(current_solution,_post_optima)
                    print (f"\nAhora escoge el gráfico que deseas para la solución {solucion_elegida}")
                    figures.show_menu_figures(current_solution)
                    export.export_data(current_solution.network_copy)
                    export.create_index_sheet(current_solution.network_copy)
                    print (f"\Gráficos y archivo de datos exportados a la carpeta de la soución {solucion_elegida}")

                else:
                    # Si hay función objetivo (resultado de optimización)
                    _post_optima=True
                    kpi.calculate_kpi(current_solution,_post_optima)
                    print (f"\Ahora escoge el gráfico que deseas para la solución {solucion_elegida}")
                    figures.show_menu_figures(current_solution)
                    export.export_data(current_solution.network_copy)
                    export.create_index_sheet(current_solution.network_copy)
                    print (f"\Gráficos y archivo de datos exportados a la carpeta de la soución {solucion_elegida}")
            
            except (ValueError, IndexError) as e:
                print (e)
                print("Error: Ingresa un número válido de la lista.")


        elif opcion == "9":
            print("Saliendo del programa.")
            break

        else:
            print("\nOpción no válida. Inténtalo de nuevo.")

# %% <codecell> Crear objeto solución


def create_solution_object(network_original, problems_dict, name_solution):
    import textwrap

    # Creamos un objeto solution
    # new_name_solution=input(textwrap.dedent(f""" \
    # Ingresa el nombre de la solución.
    # Si pulsas enter se asigna '{name_solution}': """))
    # if not new_name_solution:  # Si la entrada está vacía
    new_name_solution = name_solution
    problems_dict[new_name_solution] = Problem(name_solution=new_name_solution,
                                                 objective="Nulo",
                                                 name_network=network_original.name)
    solution = problems_dict[new_name_solution]

    # Inserto una copia de network original en la solución como network_copy
    solution.insert_network_object(network_original)
    
    # Actualizo las matrices de solution.network_copy
    solution.network_copy.merge_niveles_capac(_post_optima=False)
    solution.network_copy.create_df_asignacion(_post_optima=False)
    solution.network_copy.create_df_probs_kk()
    solution.network_copy.create_df_arcos(_post_optima=False)
    
    # Actualizar nombre de solution.network_copy
    solution.network_copy.name_solution=solution.name_solution

    
    
# %% <codecell> Clase Problem

class Problem:

    def __init__(self, name_solution, objective, name_network):
        self.name_solution = name_solution
        self.objective = objective
        self.name_network = name_network

# %% Funciones complementarias
    def insert_network_object(self, network_original):
        import copy
        self.network_copy = copy.deepcopy(network_original)

    def menu_mono_optimization(self, new_network, problems_dict):
        while True:
            print("\n----------------------------------------------------------")
            print("Menú de Optimización y Mejora")
            print("menu_mono_optimization@solutions.py")
            print("----------------------------------------------------------\n")
            print("1. Solución exacta (Optimización)")
            print("2. Solución aproximada (Algoritmos de búsqueda)")
            print("3. Regresar al menú anterior")

            opcion1 = input("Selecciona una opción: \n")
            if opcion1 == "1":
                print("Has seleccionado la opción 1.")
                print("Búsqueda por métodos exactos (Optimización).")
                self.optimizar=True
                self.tecnica="Exacta"
                # Presento menú de funciones objetivo disponibles
                objective_and_description = new_network.get_objective_function()
                
                if self.network_copy.optimizar==True:
                    self.objective = objective_and_description[0]
                    self.description_objective = objective_and_description[1]
                    self.name_solution = objective_and_description[1]
    
                    # Actualizo nombre de la solución en solution_dict (Ya no es "temporal")
                    clave_temporal = 'temporal'
                    solucion_temporal = problems_dict[clave_temporal]
                    problems_dict[solucion_temporal.description_objective] = problems_dict.pop(
                        clave_temporal)
                    problems_dict[solucion_temporal.description_objective].network_copy.name_solution = \
                        problems_dict[solucion_temporal.description_objective].name_solution 

                    break 
                
                elif self.network_copy.optimizar==False:
                    self.optimizar=False
                    break
                objective_and_description = new_network.get_objective_function()
                
            elif opcion1 == "2":
                print("Has seleccionado la Opción 2.")
                print ("Búsqueda por algoritmos de aproximación.")
                self.optimizar=True
                self.tecnica="Aproximación"
                # Presento menú de funciones objetivo disponibles
                objective_and_description = new_network.get_objective_function()
                
                if self.optimizar==True and self.tecnica=="Aproximación":
                    self.objective = objective_and_description[0]
                    self.description_objective = objective_and_description[1]
                    self.name_solution = objective_and_description[1]
                    # Actualizo nombre de la solución en solution_dict (Ya no es "temporal")
                    clave_temporal = 'temporal'
                    solucion_temporal = problems_dict[clave_temporal]
                    problems_dict[solucion_temporal.description_objective] = problems_dict.pop(
                        clave_temporal)
                    problems_dict[solucion_temporal.description_objective].network_copy.name_solution = \
                        problems_dict[solucion_temporal.description_objective].name_solution 
                
                    break 
                
                elif self.network_copy.optimizar==False:
                    self.optimizar=False
                    break
                objective_and_description = new_network.get_objective_function()
                
            elif opcion1 == "3":
                print("Has seleccionado la Opción 3.")
                self.optimizar=False
                break

            else:
                print("Opción no válida. Inténtalo de nuevo.")

    def solve_gurobi(self):
        
        network = self.network_copy
        model = self.pyo_model
        instance = self.pyo_model.instance

        # Solución por Gurobi
        import pyomo.environ as pyo
        import os

        opt = pyo.SolverFactory('gurobi', tee=True)
        opt.options['NonConvex'] = 2
        opt.options['MIPFocus'] = 3
        #opt.options['Heuristics'] = 0
        #opt.options['Presolve']  =2
        opt.options['TimeLimit'] = 500

        global out
        out = 0
        _output = os.getcwd()+'/output/'+network.name+'/'
        
        if self.name_solution == "pareto_front":
            # Crear directorio
            _output = os.getcwd()+'/output/'+'pareto_front_'+str(self.epsilon)+'/'
            if not os.path.exists(_output):
                # Crea el directorio
                os.makedirs(_output)
                
        results = opt.solve(instance, tee=True, warmstart=False,
                            logfile=_output+'logfile_name.log')
        
        # Accessing solver status: http://www.pyomo.org/blog/2015/1/8/accessing-solver
        if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
            out = "optimal and feasible"
            # results.write()
            print(results)
            # instance.display()
            # instance.pprint()
            instance.rho_max.pprint()
            instance.alpha_min.pprint()
            instance.delta_min.pprint()
            model.solution = {}
            model.solution['out'] = "optimal and feasible"
            model.solution['results'] = results
            model.solution['rho_max'] = pyo.value(instance.rho_max)
            model.solution['alpha_min'] = pyo.value(instance.alpha_min)
            model.solution['delta_min'] = pyo.value(instance.delta_min)
            
            # Export to LP
            instance.write(_output+"model.lp", format='lp')
                
        elif (results.solver.termination_condition == pyo.TerminationCondition.infeasible):
            out = "infeasible"
        elif (results.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit):
            out = "MaxTimeLimit"
            print("MaxTimeLimit")
        else:
            out = "error"
            print("Solver Status: ",  results.solver.status)
        self.out=out
        
    def solve_ipopt(self):
        network = self.network_copy
        model = self.pyo_model
        instance = self.pyo_model.instance

        # Solución por ipopt
        # Instalar ipopt así: conda install -c conda-forge ipopt=3.11.1
        import pyomo.environ as pyo
        import os

        opt = pyo.SolverFactory('ipopt')

        _output = os.getcwd()+'/output/'+network.name+'/'

        #results=opt.solve(instance, tee=True, logfile=_output+'logfile_name.log')

        results = opt.solve(instance,
                            tee=True
                            )
        print(results)
        instance.obj.pprint()
        instance.rho_max.pprint()
        instance.alpha_min.pprint()
        instance.delta_min.pprint()
        model.solution = {}
        model.solution['out'] = "optimal and feasible"
        model.solution['results'] = results
        model.solution['rho_max'] = pyo.value(instance.rho_max)
        model.solution['alpha_min'] = pyo.value(instance.alpha_min)
        model.solution['delta_min'] = pyo.value(instance.delta_min)
        
    def get_degrees_freedom(self):
        instance = self.pyo_model.instance
        # Todo: import the degrees_of_freedom function from the idaes.core.util.model_statistics package
        from idaes.core.util.model_statistics import degrees_of_freedom
        from idaes.core.util.model_statistics import report_statistics
        print("Degrees of Freedom =", degrees_of_freedom(instance))
        print("Statistics =", report_statistics(instance))

    def set_solution_excel(self):
        import numpy as np
        import pyomo.environ as pyo
        import pandas as pd
        import xlsxwriter
        import os
        import openpyxl

        network = self.network_copy
        instance = self.pyo_model.instance

        # Obtengo los valores de las variables según el modelo de optimización
        # Estas líneas se hacen si el método es exacto.
        tao_ijk = np.array([[i, j, k, pyo.value(instance.tao[i, j, k])]
                           for i in instance.I for j in instance.J for k in instance.K])
        h_ik = np.array([[i, k, pyo.value(instance.h[i, k])]
                        for i in instance.I for k in instance.K])
        l_ijk = np.array([[i, j, k, pyo.value(instance.l_ijk[i, j, k])]
                         for i in instance.I for j in instance.J for k in instance.K])
        c_jk = np.array([[j, k, pyo.value(instance.c[j, k])]
                        for j in instance.J for k in instance.K])
        s_jk = np.array([[j, k, pyo.value(instance.s[j, k])]
                        for j in instance.J for k in instance.K])

        fi_ijkjk = np.array([[i, j, k, jp, kp, pyo.value(instance.fi[i, j, k, jp, kp])]
                            for i in instance.I for j in instance.J for k in instance.K for jp in instance.J for kp in instance.K])
        df_l_ijk = pd.DataFrame(
            l_ijk, columns=['nombre_I', 'nombre_J', 'servicio_K', 'lambda_ijk'])
        fi_jkjk = pd.DataFrame(fi_ijkjk, columns=[
                               'nombre_I', 'nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp', 'fi_jkjk'])
        fi_jkjk = fi_jkjk.merge(
            df_l_ijk, on=['nombre_I', 'nombre_J', 'servicio_K'], how='left')
        fi_jkjk['fi_jkjk'] = pd.to_numeric(fi_jkjk['fi_jkjk'])
        fi_jkjk['lambda_ijk'] = pd.to_numeric(fi_jkjk['lambda_ijk'])
        fi_jkjk = fi_jkjk.groupby(
            ['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp']).sum(['lambda_ijk'])

        prob_fi_jkjk = fi_jkjk.groupby(
            ['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp']).sum(['lambda_ijk'])
        prob_fi_jkjk['fi_jkjk'] = prob_fi_jkjk['fi_jkjk'] / \
            prob_fi_jkjk['lambda_ijk']
        prob_fi_jkjk.fillna(0, inplace=True)
        prob_fi_jkjk.reset_index(inplace=True)

        #fi_jkjk = pd.DataFrame(fi_ijkjk,columns=['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp','fi_jkjk'])
        # fi_jkjk['fi_jkjk']=pd.to_numeric(fi_jkjk['fi_jkjk'])
        # fi_jkjk=fi_jkjk.groupby(['nombre_J','servicio_K','nombre_Jp','servicio_Kp']).sum().reset_index()
        #fi_jkjk['fi_jkjk']=fi_jkjk.groupby(['nombre_J','servicio_K']).apply(lambda x: x['fi_jkjk']/x['fi_jkjk'].sum()).reset_index()['fi_jkjk']
        # fi_jkjk=fi_jkjk.fillna(0)
        prob_fi_jkjk = prob_fi_jkjk.to_numpy()
        prob_fi_jkjk = prob_fi_jkjk[:, :-1]

        alpha_ik = np.array([[i, k, pyo.value(instance.alpha_ik[i, k])]
                            for i in instance.I for k in instance.K])
        rho_jk = np.array([[j, k, pyo.value(instance.rho_jk[j, k])]
                          for j in instance.J for k in instance.K])
        f_ijk = np.array([[i, j, k, pyo.value(instance.tao[i, j, k])]
                         for i in instance.I for j in instance.J for k in instance.K])
        l_jk = np.array([[j, k, sum(pyo.value(instance.l_ijk[i, j, k])
                        for i in instance.I)] for j in instance.J for k in instance.K])
        sigma_jk = np.array([[j, k, pyo.value(instance.sigma[j, k])]
                            for j in instance.J for k in instance.K])
        theta_jk = np.array([[j, k, pyo.value(instance.theta[j, k])]
                            for j in instance.J for k in instance.K])
        # Escritura de archivo en Excel
        #output = os.getcwd()+'/output/'+network.name+'/salida_optimizacion.xlsx'
        if self.name_solution != "pareto_front":
            output = os.getcwd()+'/output/'+self.name_solution+'/salida_optimizacion.xlsx'
            
            # Verificar si el directorio existe, y si no, crearlo
            directorio = os.path.dirname(output)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
            workbook = xlsxwriter.Workbook(output)
            workbook.close()
            path = output
        elif self.name_solution == "pareto_front":            
            output = os.getcwd()+'/output/'+'pareto_front_'+str(self.epsilon)+'/salida_optimizacion.xlsx'
            
            # Verificar si el directorio existe, y si no, crearlo
            directorio = os.path.dirname(output)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
            workbook = xlsxwriter.Workbook(output)
            workbook.close()
            path = output
        
        with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            writer.workbook = openpyxl.load_workbook(path)
            pd.DataFrame(l_jk).to_excel(writer, sheet_name='l_jk')
            pd.DataFrame(l_ijk).to_excel(writer, sheet_name='l_ijk')
            pd.DataFrame(f_ijk, columns=['nombre_I', 'nombre_J', 'servicio_K', 'tao_ijk']).to_excel(
                writer, sheet_name='f_ijk')  # Corresponde a los tao_ijk

            pd.DataFrame(prob_fi_jkjk, columns=['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp', 'Probs']).to_excel(
                writer, sheet_name='prob_fi_jkjk')

            pd.DataFrame(sigma_jk).to_excel(writer, sheet_name='sigma')
            pd.DataFrame(fi_ijkjk, columns=['nombre_I', 'nombre_J', 'servicio_K', 'nombre_Jp',
                         'servicio_Kp', 'fi_ijkjk']).to_excel(writer, sheet_name='fi_ijkjk')

        print(f"Se exportó exitosamente el archivo de Excel en {path}")
        self.detailed_solution={'tao_ijk':tao_ijk,
                                'h_ik':h_ik,
                                'l_ijk':l_ijk,
                                'c_jk':c_jk,
                                's_jk':s_jk,
                                'fi_ijkjk':fi_ijkjk,
                                'df_l_ijk':df_l_ijk,
                                'fi_jkjk':fi_jkjk,
                                'prob_fi_jkjk':prob_fi_jkjk,
                                'alpha_ik':alpha_ik,
                                'rho_jk':rho_jk,
                                'f_ijk':f_ijk,
                                'l_jk':l_jk,
                                'sigma_jk':sigma_jk,
                                'theta_jk':theta_jk
                                }
    def set_solution_txt(self):

        ##########################################
        #Imprimir resultados en un achivo ####
        ##########################################
        import os

        network = self.network_copy
        instance = self.pyo_model.instance

        #output = os.getcwd()+'/output/'+network.name+'/modeloysolucion.txt'
        output = os.getcwd()+'/output/'+self.name_solution+'/modeloysolucion.txt'
        
        # Verificar si el directorio existe, y si no, crearlo
        directorio = os.path.dirname(output)
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        with open(output, 'w') as output_file:
            # output_file.write(instance.pprint())
            instance.pprint(output_file)

        output = os.getcwd()+'/output/'+self.name_solution+'/solucion.txt'
        if self.name_solution == "pareto_front":
            output = os.getcwd()+'/output/'+'pareto_front_'+str(self.epsilon)+'/solucion.txt'
  
        # Verificar si el directorio existe, y si no, crearlo
        directorio = os.path.dirname(output)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        instance.display(output)

        print(f"Se exportó exitosamente el archivo de texto en {output}")

    
    def calculate_kpi_before_optim(self,network_copy,_post_optima=False):
        from hcndp import kpi
        kpi.set_lambda_jk(self,network_copy,_post_optima=False)
        kpi.set_lambda_ijk(self,network_copy,_post_optima=False)
        kpi.set_phi_ijkjk(self,network_copy)
        kpi.set_prop_tao(self,network_copy)
        kpi.set_prob_k(self,network_copy)

# %% Función principal

    # %% Crear modelo abstracto

    def construct_model(self):

        _menu_options = {
            '1': 'Minimizar congestión máxima (rho)',
            '2': 'Maximizar accesibilidad mínima (alpha)',
            '3': 'Maximizar continuidad mínima (delta)',
            '4': 'Maximizar accesibilidad total (alpha)',
            '5': 'Minimizar usuarios en espera total (Lq_total)',
            '6': 'Maximizar continuidad total (delta total)',
            '7': 'Salir al menú anterior'
        }
        objective = self.objective

        # Creo objeto Model_pyomo dentro de solution
        from hcndp import models
        self.pyo_model = models.Model_pyomo(
            model_abstract=None,
            instance=None,
            data_dat=None,
            solution=None,
            nombre_modelo=self.name_solution)

        # Lleno pyo_model con el modelo abstracto
        self.pyo_model.set_model_abstract(objetivo=objective,
                                          nombre_modelo=self.name_solution,
                                          _menu_options=_menu_options,
                                          new_network=self.network_copy
                                          )

        # Calculo kpi necesarios (solution)
        self.calculate_kpi_before_optim(network_copy=self.network_copy,
                                        _post_optima=False)

        # Creo el archivo data_dat (network)
        self.network_copy.create_data_dat()

    # %% Instanciar (model)
    def construct_instance(self):
        import os
        import pyomo.environ as pyo
        
        #self.pyo_model.data_dat = os.getcwd()+'/data/'+self.network_copy.name+'/datos.dat'
        self.pyo_model.data_dat = os.getcwd()+'/data/'+self.name_network+'/datos.dat'
        
        self.pyo_model.instance = self.pyo_model.model_abstract.create_instance(self.pyo_model.data_dat)

        if self.objective== 4:
            self.pyo_model.instance.obj = \
                pyo.Objective(expr=sum(self.pyo_model.instance.alpha_ik[i, k] *
                                       sum(self.pyo_model.instance.h[i, kp]
                                           for kp in self.pyo_model.instance.K) for i in self.pyo_model.instance.I for k in self.pyo_model.instance.K)
                              / sum(sum(self.pyo_model.instance.h[i, kp] for kp in self.pyo_model.instance.K)
                                    for i in self.pyo_model.instance.I for k in self.pyo_model.instance.K), sense=pyo.maximize)
        if self.objective == 5:
            for j in self.pyo_model.instance.J:
                for k in self.pyo_model.instance.K:
                    self.pyo_model.instance.rho_jk[j, k].setlb(
                        0.000000000000001)
                    self.pyo_model.instance.rho_jk[j,
                                                   k].value = 0.000000000000001

        if self.objective == 6:
            self.pyo_model.instance.obj = pyo.Objective(expr=sum(self.pyo_model.instance.delta_i[i] *
                                                        sum(self.pyo_model.instance.h[i, k] for k in self.pyo_model.instance.K) for i in self.pyo_model.instance.I) /
                                                        sum(self.pyo_model.instance.h[i, k]
                                                            for i in self.pyo_model.instance.I for k in self.pyo_model.instance.K),
                                                        sense=pyo.maximize)

    # %% Resolver
    def execute_solver(self):
        if self.objective == 5:
            self.solve_ipopt()
        else:
            self.solve_gurobi()
        self.get_degrees_freedom()

        # %% Exportar resultados
        self.network_copy.create_folders()
        self.set_solution_excel()
        self.set_solution_txt()

        # %% Exportar solución

        # Imprimir contenidos de una variable #####
        # for v in instance.component_objects(Var):
        #    for index in instance.v:
        #        print('{0} = {1}'.format(instance.v[index], value(instance.v[index])))

        #########################################

        # optima.set_solution_excel(network, model.instance)
        # optima.set_solution_txt(network, model.instance)

        # # Actualizo la red original con una nueva red
        # optima.update_solution_post_optima(original_network=network,
        #                                     new_network=networks[_name])

        # Creo objeto network dentro de networks
        # _copia = copy.deepcopy(networks[str(network.name)])
        # networks[nombre_modelo] = _copia
        # networks[nombre_modelo].models=None
        # networks[nombre_modelo].name=nombre_modelo


def update_solution_post_optima(original_network, new_network):
    from hcndp import read_data
    import os
    print("Ejecutando update_solution_post_optima")
    input()
    new_network.create_folders()
    path = os.getcwd()+'/data/'+original_network.name+'/'+new_network.archivo

    import shutil

    # Combinar las rutas para obtener las rutas completas
    ruta_origen = os.getcwd()+'/output/'+original_network.name + \
        '/'+'salida_optimizacion.xlsx'
    ruta_destino = os.getcwd()+'/output/'+new_network.name + \
        '/'+'salida_optimizacion.xlsx'

    # Intentar copiar el archivo
    try:
        # shutil.copy() realiza una copia superficial del archivo
        shutil.copy(ruta_origen, ruta_destino)
        print(
            f"Archivo '{new_network.archivo}' /salida_optimizacion.xlsx copiado con éxito.")
    except FileNotFoundError:
        print(
            f"El archivo '{new_network.archivo}' /salida_optimizacion.xlsx no fue encontrado en carpeta origen.")
    except PermissionError:
        print(
            f"No tienes permisos para copiar el archivo {new_network.name} /salida_optimizacion.xlsx .")
    except Exception as e:
        print(f"Error inesperado: {e}")

    read_data.read_parameters(new_network)
    read_data.read_file_excel(new_network, path)
    read_data.delete_surplus_data(new_network)
    read_data.merge_niveles_capac(new_network, post_optima=True)
    read_data.create_df_asignacion(new_network, post_optima=True)
    read_data.create_df_probs_kk(new_network)
    read_data.create_df_arcos(new_network, post_optima=True)


# %% <codecell> main
if __name__ == "__main__":
    from hcndp import network_data
    #import os
