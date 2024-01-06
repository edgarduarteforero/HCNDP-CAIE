# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 11:15:17 2024

@author: edgar
"""

def menu_multiobjective(network_original,problems_dict,multiobjective_dict):

    while True:
        print("\n----------------------------------------------------------")
        print("Selección del tipo de optimización multiobjetivo")
        print("----------------------------------------------------------\n")
        print(" 1. Método lexicográfico")
        print(" 2. Frontera de Pareto e-constraint")
        print("10. Salir")
        
        opcion1 = input("Selecciona una opción: \n")
        if opcion1 == "1":
            print("Has seleccionado la Opción 1.")
            try:     
                print("Ejecuto procedimiento lexicográfico")  
                # Creo el problema multiobjetivo    
                name_moo_problem="temporal"
                create_moo_problem_object(network_original,name_moo_problem, multiobjective_dict) 
                current_moo_problem = multiobjective_dict["temporal"]
                current_moo_problem.approach="lexicographic"

                # Pido al usuario los objetivos
                current_moo_problem.select_objectives()
                
                
                #Pido al usuario la técnica (exacta o búsqueda local)
                current_moo_problem.select_technique()
                
                # Actualizo nombre del problema en multiobjective_dict (Ya no es "temporal")
                clave_temporal = 'temporal'
                problem_temporal = multiobjective_dict[clave_temporal]
                multiobjective_dict[problem_temporal.objectives] = multiobjective_dict.pop(
                    clave_temporal)
                
                # Calculo las soluciones al problema
                current_moo_problem.calculate_lexicographic()
                
                input("Pulsa una tecla para continuar.")
                
            except AssertionError as error:
                print(error)
                print ("No puedo relizar el procedimiento.")

        if opcion1 == "2":
            print("Has seleccionado la Opción 1.")
            try:     
                print("Ejecuto procedimiento para construir frontera de Pareto")  
                # Creo el problema multiobjetivo    
                name_moo_problem="temporal"
                create_moo_problem_object(network_original,name_moo_problem, multiobjective_dict) 
                current_moo_problem = multiobjective_dict["temporal"]
                current_moo_problem.approach="Pareto"

                # Pido al usuario los objetivos
                current_moo_problem.select_objectives()
                        
                #Pido al usuario la técnica (exacta o búsqueda local)
                current_moo_problem.select_technique()
                
                # Actualizo nombre del problema en multiobjective_dict (Ya no es "temporal")
                clave_temporal = 'temporal'
                problem_temporal = multiobjective_dict[clave_temporal]
                multiobjective_dict[problem_temporal.objectives] = multiobjective_dict.pop(
                    clave_temporal)
                
                # Calculo las soluciones al problema
                current_moo_problem.calculate_pareto_front()
                
                input("Pulsa una tecla para continuar.")
                
            except AssertionError as error:
                print(error)
                print ("No puedo relizar el procedimiento.")


        elif opcion1 == "10":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


# %% <codecell> Crear multiobjective optimization problem


def create_moo_problem_object(network_original,name_moo_problem,multiobjective_dict):

    # Creamos un objeto multiobjective
    # new_name_solution=input(textwrap.dedent(f""" \
    # Ingresa el nombre de la solución.
    # Si pulsas enter se asigna '{name_solution}': """))
    # if not new_name_solution:  # Si la entrada está vacía
    new_name_problem = name_moo_problem
    multiobjective_dict[new_name_problem] = Multiobjective(objectives=None,
                                                            name_network=network_original.name,
                                                            method_multiobj=None,
                                                            network=network_original,
                                                            problems_multi_dict={})


# %% <codecell> Clase Multiobjective

class Multiobjective:

    def __init__(self, objectives, name_network, method_multiobj, network, problems_multi_dict):
        self.objectives= None
        self.name_network = None
        self.method_multiobj= None
        self.network=network
        self.problems_multi_dict={}
        self.anclas=[]
        self.menu_options_lexicog = {
           '1': ' Rho --> Alpha --> Delta',
           '2': ' Rho --> Delta --> Alpha',
           '3': ' Alpha --> Rho --> Delta',
           '4': ' Alpha --> Delta --> Rho',
           '5': ' Delta --> Rho --> Alpha',
           '6': ' Delta --> Alpha --> Rho',
           '7': ' No disponible: Delta = k --> Rho --> Alpha',
           '8': ' No disponible: Delta = k --> Alpha --> Delta',
           '9': ' Rho --> Alpha',
           '10': ' Alpha --> Rho'}
        self.menu_options_Pareto = {
            '1': ' Rho --> Alpha ',
            '2': ' No disponible Alpha --> Rho',
            '3': ' No disponible Rho--> Delta',
            '4': ' No disponible Delta --> Alpha',
            }
        
        
    def select_objectives(self):
        import textwrap
        if self.approach=="lexicographic":
            _menu_options = self.menu_options_lexicog
        elif self.approach =="Pareto":
            _menu_options = self.menu_options_Pareto
        while True:
            print("\n----------------------------------------------------------")
            print("Selección de objetivos y su orden")
            print("----------------------------------------------------------\n")            
            print(textwrap.dedent(""" \
                  Las variables de los objetivos son:
                  Rho: Máxima congestión encontrada entre los nodos de servicio. 
                  Alpha: Mínima accesibilidad entre los nodos de demanda.
                  Delta: Mínima continuidad para las combinaciones de demanda y servicio."""))
            for i, j in _menu_options.items():
                print (f"{i} : {j}")            
            opcion1 = int(input("Selecciona una opción: \n"))
            if 1<=opcion1 <= 10:
                self.objectives=_menu_options[str(opcion1)]
                self.objectives_sequence=opcion1
                break
            elif opcion1 > 10:
                break
            else:
                print("Opción no válida. Inténtalo de nuevo.")

    def select_technique(self):
        
        _menu_options = {
           '1': 'Técnicas exactas (Uso de solvers como Gurobi y ipopt)',
           '2': 'Algoritmo de búsqueda',
        }
        while True:
            print("\n----------------------------------------------------------")
            print("Selección de técnica de optimización")
            print("----------------------------------------------------------\n")            
            for i, j in _menu_options.items():
                print (f"{i} : {j}")            
            opcion1 = int(input("Selecciona una opción: \n"))
            if opcion1 == 1:
                self.method_multiobj= _menu_options[str(opcion1)]
                break
            elif opcion1 == 2:
                self.method_multiobj= _menu_options[str(opcion1)]
                break
            else:
                print("Opción no válida. Inténtalo de nuevo.")

    
    def anchor_points(self,matrix_problems_lexi,objective_lexi):
         from hcndp import solutions
         import pyomo.environ as pyo
         
         #problem_lexi es una fila de matrix_problems_lexi
         # Creo el objeto solution
         problem_lexi=matrix_problems_lexi[objective_lexi]
         solutions.create_solution_object(
                 network_original=self.network, 
                 problems_dict=self.problems_multi_dict, 
                 name_solution=problem_lexi[1])
         
         current_solution = self.problems_multi_dict[problem_lexi[1]]
         
         # Ingreso el objetivo
         current_solution.objective = problem_lexi[0]
         current_solution.description_objective = problem_lexi
         current_solution.name_solution = problem_lexi[1]
         
         # Obtener solución para cada objetivo
         if problem_lexi[0]==1:
             current_solution.construct_model()
             model=current_solution.pyo_model.model_abstract
             _var_obj_actual=problem_lexi[4]
             _sense=problem_lexi[5]
             model.del_component(model.obj)
             model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense)
         
         elif problem_lexi[0]==2:
            current_solution.construct_model()
            model=current_solution.pyo_model.model_abstract
            
            _var_obj_actual=problem_lexi[4]
            _sense=problem_lexi[5] #Minimize=1, maximize=-1
            
            # Maximizar alpha min
            # Agrego restricción y agrego función objetivo 
            # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
            if matrix_problems_lexi[0][4]=="rho_max":
                operador="<="
            else:
                operador=">="
            #Example problem_lexi=[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]
            self.lexicograf(model,
                            _var_obj_anterior=matrix_problems_lexi[0][4],
                            _func_obj_anterior=matrix_problems_lexi[0][1],
                            operador=operador)
            
            model.del_component(model.obj)
            model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense) 
            del current_solution.pyo_model.instance
            
         elif problem_lexi[0]==3:
            current_solution.construct_model()
            model=current_solution.pyo_model.model_abstract
            
            _var_obj_actual=problem_lexi[4]
            _sense=problem_lexi[5] #Minimize=1, maximize=-1


            # Maximizar alpha min
            # Agrego restricción y agrego función objetivo    
            # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
            if matrix_problems_lexi[0][4]=="rho_max":
                operador="<="
            else:
                operador=">="
            #Example problem_lexi=[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]
            self.lexicograf(model,
                            _var_obj_anterior=matrix_problems_lexi[0][4],
                            _func_obj_anterior=matrix_problems_lexi[0][1],
                            operador=operador)
        
            # Maximizar delta min
            # Agrego restricción y agrego función objetivo   
            # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
            if matrix_problems_lexi[1][4]=="rho_max":
                operador="<="
            else:
                operador=">="
            
            self.lexicograf(model,
                            _var_obj_anterior=matrix_problems_lexi[1][4],
                            _func_obj_anterior=matrix_problems_lexi[1][1],
                            operador=operador)
            
            
            model.del_component(model.obj)
            model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense) 
            del current_solution.pyo_model.instance

         current_solution.construct_instance()
         current_solution.execute_solver()
         _rho_max=pyo.value(current_solution.pyo_model.instance.rho_max)
         _alpha_min=pyo.value(current_solution.pyo_model.instance.alpha_min)
         _delta_min=pyo.value(current_solution.pyo_model.instance.delta_min)
         self.anclas.append([problem_lexi[1],
                             pyo.value(current_solution.pyo_model.instance.obj),
                            _rho_max,
                            _alpha_min,
                            _delta_min]
                            )
         
         # Convertir anclas en diccionario
         self.diccionario_anclas = {}
         for i in self.anclas:
            clave = i[0]
            valores = i[1:]
            self.diccionario_anclas[clave] = valores
         
         print (self.anclas)  
    
    def lexicograf(self,model,_var_obj_anterior,_func_obj_anterior, operador):
        import pyomo.environ as pyo
        if operador=="<=":
            restriccion = getattr(model, _var_obj_anterior) <= pyo.value(self.problems_multi_dict[_func_obj_anterior].pyo_model.instance.obj)
        elif operador == ">=":
            restriccion = getattr(model, _var_obj_anterior) <= pyo.value(self.problems_multi_dict[_func_obj_anterior].pyo_model.instance.obj)
        elif operador == "==":
            restriccion = getattr(model, _var_obj_anterior) == pyo.value(self.problems_multi_dict[_func_obj_anterior].pyo_model.instance.obj)
        
        setattr(model, f'restriccion_{_var_obj_anterior}', pyo.Constraint(expr=restriccion))

    
    def calculate_lexicographic(self):
        
        if self.objectives_sequence==1:
            matrix_problems_lexi=[[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],
                                  [2,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [3,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1]]    
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
            
        elif self.objectives_sequence==2:
            matrix_problems_lexi=[[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],
                                  [2,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1],
                                  [3,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1]]
                                  
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
        
        
        elif self.objectives_sequence==3:
            matrix_problems_lexi=[[1,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [2,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],
                                  [3,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1]]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
    
        elif self.objectives_sequence==4:
            matrix_problems_lexi=[[1,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [2,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1],
                                  [3,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
            
        elif self.objectives_sequence==5:
            matrix_problems_lexi=[[1,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1],
                                  [2,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],
                                  [3,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1]]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
            
        elif self.objectives_sequence==6:
            matrix_problems_lexi=[[1,"Max_Delta_Min","model.delta_min","maximize","delta_min",-1],
                                  [2,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [3,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
            self.anchor_points(matrix_problems_lexi,objective_lexi=2)
        
        elif self.objectives_sequence==9:
            matrix_problems_lexi=[[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],
                                  [2,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1]]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
        
        elif self.objectives_sequence==10:
            matrix_problems_lexi=[[1,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [2,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
        
    def calculate_pareto_front(self):
        import pandas as pd
        from deepdiff import DeepDiff #Importo para poder comparar dos arrays
        import numpy as np
        import winsound
        import time

        # Construyo puntos ancla
        if self.objectives_sequence==1:
            matrix_problems_lexi=[[1,"Max_Alpha_Min","model.alpha_min","maximize","alpha_min",-1],
                                  [2,"Min_Rho_Max","model.rho_max","minimize","rho_max",1],]
            self.anchor_points(matrix_problems_lexi,objective_lexi=0)          
            self.anchor_points(matrix_problems_lexi,objective_lexi=1)
        
        # Construyo un objeto model llamado 'principal'
        from hcndp import solutions
        import pyomo.environ as pyo
        
        #problem_lexi es una fila de matrix_problems_lexi
        # Creo el objeto solution
        objective_lexi=1
        problem_lexi=matrix_problems_lexi[objective_lexi]
        solutions.create_solution_object(
                network_original=self.network, 
                problems_dict=self.problems_multi_dict, 
                name_solution="principal")
        
        current_solution = self.problems_multi_dict["principal"]
        current_solution.construct_model()
        model=current_solution.pyo_model.model_abstract
        current_solution.objective = problem_lexi[0]
        current_solution.description_objective = problem_lexi
        current_solution.name_solution = 'pareto_front'

        # Variable para aplicar el e-constraint        
        model.s2=pyo.Var(within=pyo.NonNegativeReals,initialize=0)

        #Agrego restricción e constraint
        model.eps2=pyo.Param(mutable=True)
        def restr_epsilon_alpha_rule(model):
            return model.alpha_min - model.s2 == model.eps2 #
        model.restr_epsilon_alpha = pyo.Constraint(rule=restr_epsilon_alpha_rule)
        
        
        #Agrego función objetivo
        # Verificar si el atributo 'obj' existe en el modelo
        if hasattr(model, 'obj'):
            model.del_component(model.obj)

        #La constante 'denominador_s' es el rango de la i-ésima función objetivo 
        #(accesibilidad) en el payoff table
        _alpha_min_0=self.anclas[0][2]
        _alpha_min_1=self.anclas[1][2]
        denominador_s2=abs(_alpha_min_0-_alpha_min_1)
        
        model.obj = pyo.Objective(expr=model.rho_max * 100 + (10**-6) * (model.s2)/denominador_s2
                            , sense=pyo.minimize) #/ 348 ,sense=minimize)
        
        # Construyo la instancia
        current_solution.construct_instance()
        
        # Construyo matrices para guardar resultados
        global df_soluciones_rho, df_soluciones_alpha_ik,df_soluciones_tao_ijk
        global df_soluciones_fi_jkjk,df_soluciones_sigma,df_soluciones_fi_ijkjk
        
        df_soluciones_rho=pd.DataFrame()
        df_soluciones_alpha_ik=pd.DataFrame()
        df_soluciones_tao_ijk=pd.DataFrame()
        df_soluciones_fi_jkjk=pd.DataFrame()
        df_soluciones_sigma=pd.DataFrame()
        df_soluciones_fi_ijkjk=pd.DataFrame()

        
        
        # Número de puntos a obtener
        puntos_requeridos= int(input("\nIngresa el número de puntos para la frontera:"))

        
        # Soluciones del lexicográfico
        rho_opt=self.diccionario_anclas['Min_Rho_Max'][1:3]
        rho_opt[0]*=100
        acc_opt=self.diccionario_anclas['Max_Alpha_Min'][1:3]
        acc_opt[0]*=100
        
        # Construir estructura de datos: salida_resultados, points_used, 
        # puntos_revisados, soluciones
        salida_resultados=np.array([rho_opt,acc_opt])
        points_used=np.array([rho_opt+acc_opt+[1,1]])
        fila=0
        factor=0
        # Inicio cronómetro
        start_time = time.time()
        tiempo=[start_time]
        puntos_revisados = np.vstack((np.array([rho_opt]), acc_opt))
        soluciones=[] #Lista con las estadísticas de cada solución encontrada
        
        while len(salida_resultados) <= puntos_requeridos:
            global precision
            precision = 10
            
            #Calculo un punto medio epsilon
            epsilon=self.calculo_i2(fila,factor,points_used)
            print ("Cálculo de un nuevo epsilon")
            print ("---------------------------")
            print ("fila en points used es", fila)
            print ("factor es", factor)
            print ("punto medio entre",points_used[fila,1]," y ", points_used[fila,3])
            print ("el epsilon i es:", epsilon)
            epsilon=round(epsilon,precision)
            print ("el epsilon redondeado es:", epsilon)
            print ()
            print ("Cálculo de un nuevo punto para el epsilon hallado")
            print ("-------------------------------------------------")
            
            #Obtengo un punto en frontera
            if epsilon in puntos_revisados:
                print ("El punto ", epsilon, "ya había sido evaluado.")   
                # Construyo el punto obtenido para que sea revisado por dominancia y repetición
                a= np.where(puntos_revisados==epsilon)[0][0]
                b= np.where(puntos_revisados==epsilon)[1][0]
                punto_obtenido=[puntos_revisados[a,0],puntos_revisados[a,0]*100,puntos_revisados[a,b],"distancia corta"]
            else: #Obtengo un punto obtenido desde optimización
                print ("Punto no evaluado, procedo a optimización")
                punto_obtenido=self.frontera(val2=epsilon,val3=3,current_solution=current_solution)
                puntos_revisados=np.vstack((puntos_revisados,[punto_obtenido[0],punto_obtenido[2]])) #Agrego los puntos hallados a una matriz de puntos_Revisados
            print ("El nuevo punto es:", punto_obtenido[0:4])
            #input()
            
            #Verifico si el punto obtenido es dominado. En tal caso, altero.
            dominado=self.dominancia(punto_obtenido[0],punto_obtenido[2],points_used[fila,2],points_used[fila,3],points_used[fila,0],points_used[fila,1])
            punto_repetido=self.repetido(punto_obtenido[0:4],salida_resultados)
            winsound.Beep(500, 1000)
            #if len(salida_resultados)>= 20:
            #    input("Press Enter to continue...")
            print (dominado,punto_repetido)
            #input()
            
            while dominado=="dominado" or punto_repetido=="Si":
                print("Punto dominado= ",dominado,". Punto repetido= ",punto_repetido,". ")
                #print("Punto repetido", punto_obtenido)
                #fila=fila-1
                #vuelvo a definir la solución inicial para ipopt
                #for i in instance.I:
                #    for j in instance.J:
                #        for k in instance.K:
                #            #instance.fi[i,j,k]=value(instance.inic_fi[i,j,k])
                #            instance.tao[i,j,k]=value(instance.inic_tao[i,j,k])
                #            instance.l_ijk[i,j,k]=value(instance.inic_l_ijk[i,j,k])
                #input()
                
                factor=factor+1
                if factor > 10:
                    punto_obtenido[3]=="distancia corta"
                    break
                print ("Incremento factor a ", factor,"y calculo nuevo epsilon")
                epsilon=round(self.calculo_i2(fila,factor,points_used),precision)
                print ("nuevo epsilon:", epsilon)
                #input()
                
                if abs(punto_obtenido[2] - epsilon) <=10**-precision: #El ajuste por factor es demasiado pequeño
                    punto_obtenido[3]="distancia corta"
                    dominado=""
                    punto_repetido=""
                    print ("solución con distancia corta: ",punto_obtenido [0:4])
                    #break
                else:
                    print ("Ahora Epsilon es ", epsilon)
                    punto_obtenido=self.frontera(val2=epsilon,val3=3,current_solution=current_solution)
                    print("Remplazo el punto dominado / repetido por", punto_obtenido[0:4], "y evalúo nuevamente si es dominado o repetido.")
                    dominado=self.dominancia(punto_obtenido[0],punto_obtenido[2],points_used[fila,2],points_used[fila,3],points_used[fila,0],points_used[fila,1])
                    punto_repetido=self.repetido(punto_obtenido,salida_resultados)
                #input()
            
            # Verifico si la solución fue factible
            if punto_obtenido[3]=="optimal and feasible": 
                print ("optimal and feasible")
                #input()
                salida_resultados=np.vstack((salida_resultados,[punto_obtenido[0],punto_obtenido[2]])) #... agrego a salida_resultados
                print ("agrego solución a salida_resultados",[punto_obtenido[0],punto_obtenido[2]] )
                print ("tiempo", time.time()-start_time)
                tiempo.append(time.time() - start_time)
                
                
                # LÍNEA ELIMINADA!!!!!
                #self.analisis_solucion(current_solution,soluciones,epsilon) #Analizo la solución obtenida y la agrego a la lista soluciones[]
                
                # Agrego el detalle de la solución a una matriz
                #input()
                
                
                #Si se alcanza el número de puntos requeridos se interrumpe el programa
                if len(salida_resultados) == puntos_requeridos: 
                    print ("Se alcanzaron los puntos requeridos")
                    break 
                    #input()
                
                # Hago  una nueva iteración 
                else: 
                    #Ordeno salida_resultados
                    salida_resultados = salida_resultados[salida_resultados[:, 1].argsort()[::-1]]
                    print ("resultados ordenados",salida_resultados)
                    #input()
                    # Encuentro la mayor distancia euclideana
                    contador=0
                    distance_mayor=0
                    while contador < len(salida_resultados)-1:
                        #PAra calcular las distancias tengo que normalizar los datos encontrados
                        salida_resultados_estand=(salida_resultados-salida_resultados.min(axis=0))/(salida_resultados.max(axis=0)-salida_resultados.min(axis=0))
                        distance =abs(salida_resultados_estand[contador][1]-salida_resultados_estand[contador+1][1])
                        #distance =np.linalg.norm(salida_resultados_estand[contador]-salida_resultados_estand[contador+1])
                        print ("distancia",distance)
                        if (salida_resultados_estand[contador,1]-salida_resultados_estand[contador+1,1])/salida_resultados_estand[contador+1,1] <= 0.0001:
                            distance=0
                            print ("Distancia ajustada por ser muy corta.")
                        if distance > distance_mayor and salida_resultados[contador][1] - salida_resultados[contador+1][1] > 10**(-precision):
                            distance_mayor = distance 
                            puntos_mayor = np.hstack((salida_resultados [contador], salida_resultados[contador+1]))
                        contador=contador+1
                    print("distancia  mayor",distance_mayor)
                    
                    
                    # Encuentro los puntos con la mayor distancia euclideana
                    print ("puntos_mayor",puntos_mayor)
                    #input()
                    
                    
                    # Verifico si los puntos con la mayor distancia euclideana están en points_used en una misma  línea
                    existe_punto_en_points_used=0
                    index=-1 #índice para saber qué elemento de points_used estoy usando
                    for punto in points_used:
                        #print ("evaluo este punto de points_used: ",punto)
                        #print ("lo comparo con puntos mayor: ",puntos_mayor)
                        index+=1
                        #Si se cumple la siguiente condición, no hay diferencias entre los vectores,
                        #DeepDiff encuentra diferencias. Si el resultado está vacío, no hay diferencias
                        if DeepDiff (punto[:4],puntos_mayor,significant_digits=5) =={} or DeepDiff (puntos_mayor[[2,3,0,1]],punto[:4],significant_digits=5) == {}:
                            print ("puntos mayor está en points_used,  no lo agrego")
                            existe_punto_en_points_used=1
                            fila=index
                    #input()
                    
                    # Si los dos puntos ya están en points_used, tengo que subdividir
                    if existe_punto_en_points_used==1: 
                        factor=factor+1
                        print ("Ahora factor vale: ", factor)
        
                        #if points_used[fila,5] > 2**(points_used[fila,4]-1):
                        #    points_used[fila,4]=points_used[fila,4]+1
                        #    points_used[fila,5]=1
                        #else:
                        #    points_used[fila,5]=points_used[fila,5]+1
                    
                    #Los puntos_mayor no están en points_used. Se agregan a points_used
                    else: 
                        print ("puntos_mayor no está en points used, agrego puntos mayor a points used:",puntos_mayor)
                        #tengo que odenar puntos_mayor de punto menor a punto mayor
                        if puntos_mayor[1]> puntos_mayor[3]:
                            puntos_mayor=puntos_mayor[[2,3,0,1]]
                            
                        points_used=np.vstack((points_used,np.hstack((puntos_mayor,[1,1]))))
                        points_used[:,-2:]=1 ###################### Cambio todos los n1 y n2 a 1
                        fila=len(points_used)-1
                        factor=0
                        print ("agregué un punto nuevo, ahora tengo: ", fila, "puntos.")
                    print ("points used ahora es:", points_used)
                    #input()
                    
                    
            #Si la solución hallada no es factible  
            elif punto_obtenido[3]=="infeasible": 
                 print ("Se obtuvo infactible")
                
                 factor = factor+1
                
                 print ("ahora factor es: ", factor)
                 #if points_used[fila,5] > 2**(points_used[fila,4]-1):
                 #   points_used[fila,4]=points_used[fila,4]+1
                 #   points_used[fila,5]=1
                 #else:
                 #   points_used[fila,5]=points_used[fila,5]+1
                 #input()
                    
            #Si pyomo generó error
            elif punto_obtenido[3]=="error": 
                 print ("No se alcanzó a solucionar")
                 factor = factor+1
                
                 print ("ahora factor es: ", factor)
                 #input()
                
            elif punto_obtenido[3]=="distancia corta":
                # Tengo que generar un nuevo par de soluciones
                    #Ordeno salida_resultados
                    print ("Tengo solución con distancia corta, ordeno y genero nueva solución con mayor distancia siguiente")
                    salida_resultados = salida_resultados[salida_resultados[:, 1].argsort()[::-1]]
                    print ("resultados ordenados",salida_resultados)
                    
                    # Encuentro la mayor distancia euclideana
                    contador=0
                    distance_mayor=0
                    while contador < len(salida_resultados)-1:
                        #PAra calcular las distancias tengo que normalizar los datos encontrados
                        salida_resultados_estand=salida_resultados/salida_resultados.max(axis=0)
                        distance =abs(salida_resultados_estand[contador][1]-salida_resultados_estand[contador+1][1])
                        #distance =np.linalg.norm(salida_resultados_estand[contador]-salida_resultados_estand[contador+1])
                        print ("distancia",distance)
                        if distance > distance_mayor and salida_resultados[contador][1] - salida_resultados[contador+1][1] > 10**(-precision):
                            distance_mayor = distance 
                            puntos_mayor = np.hstack((salida_resultados [contador], salida_resultados[contador+1]))
                        contador=contador+1
                    print("distancia  mayor",distance_mayor)
                    
                    
                    # Encuentro los puntos con la mayor distancia euclideana
                    print ("puntos_mayor",puntos_mayor)
                    
                    # Verifico si los puntos con la mayor distancia euclideana están en points_used en una misma  línea
                    existe_punto_en_points_used=0
                    index=-1 #índice para saber qué elemento de points_used estoy usando
                    for punto in points_used:
                        #print ("evaluo este punto de points_used: ",punto)
                        #print ("lo comparo con puntos mayor: ",puntos_mayor)
                        index+=1
                        #Si se cumple la siguiente condición, no hay diferencias entre los vectores,
                        #DeepDiff encuentra diferencias. Si el resultado está vacío, no hay diferencias
                        if DeepDiff (punto[:4],puntos_mayor,significant_digits=5) =={} or DeepDiff (puntos_mayor[[2,3,0,1]],punto[:4],significant_digits=5) == {}:
                            print ("puntos mayor está en points_used,  no lo agrego")
                            existe_punto_en_points_used=1
                            fila=index
                            
                    # Si los dos puntos ya están en points_used, tengo que subdividir
                    if existe_punto_en_points_used==1: 
                        factor=factor+1
                        print ("Ahora factor vale: ", factor)
        
                        #if points_used[fila,5] > 2**(points_used[fila,4]-1):
                        #    points_used[fila,4]=points_used[fila,4]+1
                        #    points_used[fila,5]=1
                        #else:
                        #    points_used[fila,5]=points_used[fila,5]+1
                    
                    #Los puntos_mayor no están en points_used. Se agregan a points_used
                    else: 
                        print ("puntos_mayor no está en points used, agrego puntos mayor a points used:",puntos_mayor)
                        #tengo que odenar puntos_mayor de punto menor a punto mayor
                        if puntos_mayor[1]> puntos_mayor[3]:
                            puntos_mayor=puntos_mayor[[2,3,0,1]]
                            
                        points_used=np.vstack((points_used,np.hstack((puntos_mayor,[1,1]))))
                        points_used[:,-2:]=1 ###################### Cambio todos los n1 y n2 a 1
                        fila=len(points_used)-1
                        factor=0
                        print ("agregué un punto nuevo, ahora tengo: ", fila, "puntos.")
                    print ("points used ahora es:", points_used)
                    #input()
            
            else:
                print ("ocurrió un error en pyomo")
                factor=factor+1
                print ("ahora factor es: ", factor)
                input()
                
            ### Imprimo gráfico 
            import numpy as np
            import math
            import matplotlib.pyplot as plt
            x=salida_resultados[:,0]
            y=salida_resultados[:,1]
            fig = plt.figure(figsize=(8,6))
            #plt.plot(x, y, 'o', color='darkred')
            #plt.xlabel(r'$\rho_{max}$',fontsize=20)
            #plt.ylabel(r"$A_{min}$", fontsize=20)
            #plt.legend(["Pareto front solutions"])
            #input()
            
            print ("termino iteración con",len(salida_resultados), " puntos.")
            #input("Press Enter to analyze the obtained solution...")
            #input()
            
        
        '''
        # Obtener solución para cada objetivo
        if problem_lexi[0]==1:
            current_solution.construct_model()
            model=current_solution.pyo_model.model_abstract
            _var_obj_actual=problem_lexi[4]
            _sense=problem_lexi[5]
            model.del_component(model.obj)
            model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense)
        
        elif problem_lexi[0]==2:
           current_solution.construct_model()
           model=current_solution.pyo_model.model_abstract
           
           _var_obj_actual=problem_lexi[4]
           _sense=problem_lexi[5] #Minimize=1, maximize=-1
           
           # Maximizar alpha min
           # Agrego restricción y agrego función objetivo 
           # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
           if matrix_problems_lexi[0][4]=="rho_max":
               operador="<="
           else:
               operador=">="
           #Example problem_lexi=[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]
           self.lexicograf(model,
                           _var_obj_anterior=matrix_problems_lexi[0][4],
                           _func_obj_anterior=matrix_problems_lexi[0][1],
                           operador=operador)
           
           model.del_component(model.obj)
           model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense) 
           del current_solution.pyo_model.instance
           
        elif problem_lexi[0]==3:
           current_solution.construct_model()
           model=current_solution.pyo_model.model_abstract
           
           _var_obj_actual=problem_lexi[4]
           _sense=problem_lexi[5] #Minimize=1, maximize=-1
        
        
           # Maximizar alpha min
           # Agrego restricción y agrego función objetivo    
           # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
           if matrix_problems_lexi[0][4]=="rho_max":
               operador="<="
           else:
               operador=">="
           #Example problem_lexi=[1,"Min_Rho_Max","model.rho_max","minimize","rho_max",1]
           self.lexicograf(model,
                           _var_obj_anterior=matrix_problems_lexi[0][4],
                           _func_obj_anterior=matrix_problems_lexi[0][1],
                           operador=operador)
        
           # Maximizar delta min
           # Agrego restricción y agrego función objetivo   
           # Si la restricción usa rho entonces va con <=, de lo contrario, va con >=
           if matrix_problems_lexi[1][4]=="rho_max":
               operador="<="
           else:
               operador=">="
           
           self.lexicograf(model,
                           _var_obj_anterior=matrix_problems_lexi[1][4],
                           _func_obj_anterior=matrix_problems_lexi[1][1],
                           operador=operador)
           
           
           model.del_component(model.obj)
           model.obj = pyo.Objective(expr=getattr(model, _var_obj_actual),sense=_sense) 
           del current_solution.pyo_model.instance
        
        current_solution.construct_instance()
        current_solution.execute_solver()
        self.anclas.append([problem_lexi[1],pyo.value(current_solution.pyo_model.instance.obj)])
        print (self.anclas)  
        '''
    
    # Fórmula adaptada para asegurar mejores resultados
    def calculo_i2 (self,fila,factor,points_used):
        bisec=self.funcion_bisec(factor)
        epsilon=points_used[fila,1]+(points_used[fila,3]-points_used[fila,1])*bisec
        return epsilon   
    
    # Función para obtener la solución a un problema
    def frontera(self,val2,val3,current_solution):
        import pyomo.environ as pyo
        import numpy as np
        import pandas as pd
        import xlsxwriter
        import os
        import openpyxl
        
        #instance = model.create_instance("datos.dat") 
        instance=current_solution.pyo_model.instance
        instance.eps2 = val2
        instance.eps3 = val3
        
        opt = pyo.SolverFactory('gurobi',tee=True)
        opt.options['NonConvex'] = 2
        opt.options['TimeLimit']=50
        #opt.options['MIPGap']=0.01
        #opt.options['MIPFocus']= 3 #
        
        results=opt.solve(instance)
        results
        #solucion=[value(instance.inic_rho_max),value(instance.inic_alpha_min)]
        # Accessing solver status: http://www.pyomo.org/blog/2015/1/8/accessing-solver
        if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
            out="optimal and feasible"
        elif (results.solver.termination_condition == pyo.TerminationCondition.infeasible):
            out="infeasible"
        
        else:
            out="error"
            print ("Solver Status: ",  results.solver.status)
    
        ## Obtengo los valores de las variables según el modelo de optimización
        tao_ijk = np.array([[i,j,k,pyo.value(instance.tao[i,j,k])] for i in instance.I for j in instance.J for k in instance.K])
        h_ik = np.array([[i,k,pyo.value(instance.h[i,k])] for i in instance.I for k in instance.K])
        l_ijk = np.array([[i,j,k,pyo.value(instance.l_ijk[i,j,k])] for i in instance.I for j in instance.J for k in instance.K])
        c_jk = np.array([[j,k,pyo.value(instance.c[j,k])] for j in instance.J for k in instance.K])
        s_jk = np.array([[j,k,pyo.value(instance.s[j,k])] for j in instance.J for k in instance.K])
    
        fi_ijkjk = np.array([[i,j,k,jp,kp,pyo.value(instance.fi[i,j,k,jp,kp])] for i in instance.I for j in instance.J for k in instance.K for jp in instance.J for kp in instance.K])
        
        df_l_ijk=pd.DataFrame(l_ijk,columns=['nombre_I','nombre_J','servicio_K','lambda_ijk'])
        fi_jkjk = pd.DataFrame(fi_ijkjk,columns=['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp','fi_jkjk'])
        fi_jkjk=fi_jkjk.merge(df_l_ijk, on=['nombre_I','nombre_J', 'servicio_K'], how='left')
        fi_jkjk['fi_jkjk']=pd.to_numeric(fi_jkjk['fi_jkjk'])
        fi_jkjk['lambda_ijk']=pd.to_numeric(fi_jkjk['lambda_ijk'])
        fi_jkjk=fi_jkjk.groupby(['nombre_J','servicio_K','nombre_Jp','servicio_Kp']).sum(['lambda_ijk'])
    
    
        prob_fi_jkjk=fi_jkjk.groupby(['nombre_J','servicio_K','nombre_Jp','servicio_Kp']).sum(['lambda_ijk'])
        prob_fi_jkjk['fi_jkjk']=prob_fi_jkjk['fi_jkjk']/prob_fi_jkjk['lambda_ijk']
        prob_fi_jkjk.fillna(0,inplace=True)
        prob_fi_jkjk.reset_index(inplace=True)
        prob_fi_jkjk=prob_fi_jkjk.to_numpy()
        prob_fi_jkjk = prob_fi_jkjk[:, :-1] 
    
        alpha_ik = np.array([[i,k,pyo.value(instance.alpha_ik[i,k])] for i in instance.I for k in instance.K ])
        rho_jk=np.array([[j,k,pyo.value(instance.rho_jk[j,k])] for j in instance.J for k in instance.K])
        f_ijk=np.array ([[i,j,k,pyo.value(instance.tao[i,j,k])] for i in instance.I for j in instance.J for k in instance.K])
        l_jk=np.array  ([[j,k,sum(pyo.value(instance.l_ijk[i,j,k]) for i in instance.I)] for j in instance.J for k in instance.K])
        sigma_jk=np.array ([[j,k,pyo.value(instance.sigma[j,k])] for j in instance.J for k in instance.K])
        theta_jk=np.array ([[j,k,pyo.value(instance.theta[j,k])] for j in instance.J for k in instance.K])
               
        ### Escribo en un archivo de Excel
        #output = os.getcwd()+'/output/'+network.name+'/salida_optimizacion.xlsx'
        output = os.getcwd()+'/output/'+current_solution.name_solution+'/salida_optimizacion.xlsx'
        # Verificar si el directorio existe, y si no, crearlo
        directorio = os.path.dirname(output)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        # workbook = xlsxwriter.Workbook(output)
        # workbook.close()
        # path = output
    
        # with pd.ExcelWriter(path, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        #     writer.book = openpyxl.load_workbook(path)
        #     pd.DataFrame(l_jk).to_excel(writer, sheet_name='l_jk')
        #     pd.DataFrame(l_ijk).to_excel(writer, sheet_name='l_ijk')
        #     pd.DataFrame(f_ijk).to_excel(writer, sheet_name='f_ijk') #Corresponde a los tao_ijk
        #     pd.DataFrame(prob_fi_jkjk).to_excel(writer, sheet_name='prob_fi_jkjk')
        #     pd.DataFrame(sigma_jk).to_excel(writer, sheet_name='sigma')
        #     pd.DataFrame(fi_ijkjk).to_excel(writer,sheet_name='fi_ijkjk')

        # Crear el libro con xlsxwriter
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Crear hojas y agregar datos
            pd.DataFrame(l_jk).to_excel(writer, sheet_name='l_jk')
            pd.DataFrame(l_ijk).to_excel(writer, sheet_name='l_ijk')
            pd.DataFrame(f_ijk).to_excel(writer, sheet_name='f_ijk')
            pd.DataFrame(prob_fi_jkjk).to_excel(writer, sheet_name='prob_fi_jkjk')
            pd.DataFrame(sigma_jk).to_excel(writer, sheet_name='sigma')
            pd.DataFrame(fi_ijkjk).to_excel(writer, sheet_name='fi_ijkjk')
        
        
        ### Devuelvo rho, rho*100, alpha min, el estado de la solución, y los tao, fi, rho y alphas de cada solución 
        return [pyo.value(instance.obj),pyo.value(instance.rho_max*100),pyo.value(instance.alpha_min),out,tao_ijk,fi_jkjk,rho_jk, alpha_ik,fi_ijkjk]

    
    def dominancia(self,x1,y1,x2,y2,x3,y3): #x1y1 es el punto obtenido, x2y2 es el punto que está arriba y x3y3 es el que está abajo
        #Para un valor de y1, el modelo busca un valor de x1. x1 puede estar por encima de x2 (dominado), por debajo de x3 (error) o entre x2 y x3 (no dominado)
        print ("Evaluando dominancia entre punto obtenido ",x1,",",y1,", punto arriba ",x2,",",y2," y punto abajo ",x3,",",y3)
        x1=round(x1,precision)
        y1=round(y1,precision)
        x2=round(x2,precision)
        y2=round(y2,precision)
        x3=round(x3,precision)
        y3=round(y3,precision)
        if x1>x2 and y1<y2:
            #tengo un punto dominado
            return "dominado"
        elif x3>x1 :
            return "dominado" #En este caso hay un error en ipopt y está generando un punto que no está en la frontera.
        else:
            return "no dominado"     
        
    # Función para verificar si un punto_obtenido ya está en salida_resultados:
    def repetido(self,punto_obtenido,salida_resultados):
        import numpy as np
        #if np.around(punto_obtenido[1:3],1) in np.around(salida_resultados,1):
        #if [punto_obtenido[0],punto_obtenido[2]] in salida_resultados:
        if  np.isin(salida_resultados.tolist(), [punto_obtenido[0],punto_obtenido[2]]).all(axis=1).any():
        #if punto_obtenido[1:3] in salida_resultados:
            repetido="Si" #El punto obtenido ya está en salida_resultados
        else:
            repetido="No"
        return repetido
    
    def analisis_solucion(self,current_solution,soluciones,epsilon):
        from hcndp import kpi
        import pandas as pd
        
        # Si hay función objetivo (resultado de optimización)
        _post_optima=True
        kpi.calculate_kpi(current_solution,_post_optima)
        
        #print (f"\Ahora escoge el gráfico que deseas para la solución {solucion_elegida}")
        #figures.show_menu_figures(current_solution)
        #export.export_data(current_solution.network_copy)
        #export.create_index_sheet(current_solution.network_copy)
        #print (f"\Gráficos y archivo de datos exportados a la carpeta de la soución {solucion_elegida}")
    
        #Importo los resultados de calculate kpi
        I=current_solution.network_copy.I 
        J=current_solution.network_copy.J
        K=current_solution.network_copy.K
        df_accesibilidad=current_solution.network_copy.file['df_accesibilidad']
        df_capac=current_solution.network_copy.file['df_capac']
        df_asignacion=current_solution.network_copy.file['df_asignacion']
        df_w_ij=current_solution.network_copy.file['df_w_ij']
        df_flujos_jkjk=current_solution.network_copy.file['df_flujos_jkjk']
        df_fi_ijkjk=current_solution.network_copy.file['df_flujos_ijkjk']
        
        # Agrego estadísticas de la solución a la lista "soluciones"
        soluciones.append(
         [str(I)+str(J)+str(K),
             df_accesibilidad['R'].min(),
             df_accesibilidad['R'].max(), #
             df_accesibilidad['R'].mean(),
             df_accesibilidad['R'].std(),
             df_capac['rho'].min(),
             df_capac['rho'].max(),
             df_capac['rho'].mean(),
             df_capac['rho'].std(),
             #df_asignacion['y_ijk'][df_asignacion['y_ijk'] > 0].count(), #Arcos asignados ij para k=1
             0,
             df_w_ij['w_ij'][df_w_ij['w_ij']>0].count(), #Arcos posibles w_ij
             df_flujos_jkjk['p_jjkk'][df_flujos_jkjk['p_jjkk']>0].count(), #Arcos asignados jkjk. Son los mismos phi 
             df_flujos_jkjk['p_kkp_True_False'][df_flujos_jkjk['p_kkp_True_False']>0].count(), #Arcos posibles jkj 
             I, #Número de nodos de demanda
             J, #Número de nodos de servicio
             df_flujos_jkjk[df_flujos_jkjk['nombre_J']!=df_flujos_jkjk['nombre_Jp']].
              groupby(['nombre_J','nombre_Jp'])['p_jjkk_True_False'].sum().mean(), #Grado promedio de nodos de servicio (se usa el j, no el jk)
             df_flujos_jkjk[df_flujos_jkjk['nombre_J']!=df_flujos_jkjk['nombre_Jp']].
              groupby(['nombre_J','nombre_Jp'])['p_jjkk_True_False'].sum().max(), #Grado máximo de nodos de servicio (se usa el j, no el jk)
             df_flujos_jkjk[df_flujos_jkjk['nombre_J']!=df_flujos_jkjk['nombre_Jp']].
              groupby(['nombre_J','nombre_Jp'])['p_jjkk_True_False'].sum().min(), #Grado mínimo de nodos de servicio (se usa el j, no el jk)
         ])
         
        # Verifico si df_soluciones_rho existe
        global df_soluciones_rho
        if len(df_soluciones_rho.columns)== 0:
            df_soluciones_rho=df_capac.loc[:,df_capac.columns=='rho'] #Creo un dataframe para almacenar los rho jk que se van generando
            df_soluciones_rho=df_soluciones_rho.set_axis([*df_soluciones_rho.columns[:-1], epsilon], axis=1)
        else:
            df_soluciones_rho=pd.merge(df_soluciones_rho,df_capac['rho'],left_on=['nombre_J','servicio_K'],right_on=['nombre_J','servicio_K'], how='left')
            df_soluciones_rho=df_soluciones_rho.set_axis([*df_soluciones_rho.columns[:-1], epsilon], axis=1)
        
        # Verifico si df_soluciones_alpha_ik existe
        global df_soluciones_alpha_ik
        if len(df_soluciones_alpha_ik.columns)== 0:
            df_soluciones_alpha_ik=df_accesibilidad.loc[:,df_accesibilidad.columns=='R'] #Creo un dataframe para almacenar los alpha_ik que se van generando
            df_soluciones_alpha_ik=df_soluciones_alpha_ik.set_axis([*df_soluciones_alpha_ik.columns[:-1], epsilon], axis=1)
        else:
            df_soluciones_alpha_ik=pd.merge(df_soluciones_alpha_ik,df_accesibilidad['R'],left_on=['nombre_I','servicio_K'],right_on=['nombre_I','servicio_K'], how='left')
            df_soluciones_alpha_ik=df_soluciones_alpha_ik.set_axis([*df_soluciones_alpha_ik.columns[:-1], epsilon], axis=1)
            
        
        # Verifico si df_soluciones_tao_ijk existe
        global df_soluciones_tao_ijk
        if len(df_soluciones_tao_ijk.columns)== 0:
            df_soluciones_tao_ijk=df_asignacion.set_index(['nombre_I','nombre_J','servicio_K'],drop=False).loc[:,df_asignacion.columns=='y_ijk']        
            df_soluciones_tao_ijk=df_soluciones_tao_ijk.set_axis([*df_soluciones_tao_ijk.columns[:-1], epsilon], axis=1)
        else:
            df_soluciones_tao_ijk=pd.merge(df_soluciones_tao_ijk,
                                           df_asignacion.set_index(['nombre_I','nombre_J','servicio_K'],drop=False)['y_ijk'],
                                           left_on=['nombre_I','nombre_J','servicio_K'],right_on=['nombre_I','nombre_J','servicio_K'], how='left')
            df_soluciones_tao_ijk=df_soluciones_tao_ijk.set_axis([*df_soluciones_tao_ijk.columns[:-1], epsilon], axis=1) #prueba
            
        
        # Verifico si df_soluciones_fi_jkjk existe
        global df_soluciones_fi_jkjk
        if len(df_soluciones_fi_jkjk.columns)== 0:
            df_soluciones_fi_jkjk=df_flujos_jkjk.set_index(['nombre_J','servicio_K','nombre_Jp','servicio_Kp'],drop=False).loc[:,df_flujos_jkjk.columns=='p_jjkk']        
            df_soluciones_fi_jkjk=df_soluciones_fi_jkjk.set_axis([*df_soluciones_fi_jkjk.columns[:-1], epsilon], axis=1)
    
        else:
            df_soluciones_fi_jkjk=pd.merge(df_soluciones_fi_jkjk,
                                           df_flujos_jkjk.set_index(['nombre_J','servicio_K','nombre_Jp','servicio_Kp'],drop=False)['p_jjkk'],
                                           left_on=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'],right_on=['nombre_J','servicio_K','nombre_Jp','servicio_Kp'], how='left')
            df_soluciones_fi_jkjk=df_soluciones_fi_jkjk.set_axis([*df_soluciones_fi_jkjk.columns[:-1], epsilon], axis=1) #prueba
            
        
        # Verifico si df_soluciones_sigma existe
        global df_soluciones_sigma
        if len(df_soluciones_sigma.columns)== 0:
            df_soluciones_sigma=df_capac.loc[:,df_capac.columns=='sigma_jk'] #Creo un dataframe para almacenar los sigma jk que se van generando
            df_soluciones_sigma=df_soluciones_sigma.set_axis([*df_soluciones_sigma.columns[:-1], epsilon], axis=1)
        else:
            df_soluciones_sigma=pd.merge(df_soluciones_sigma,df_capac['sigma_jk'],left_on=['nombre_J','servicio_K'],right_on=['nombre_J','servicio_K'], how='left')
            df_soluciones_sigma=df_soluciones_sigma.set_axis([*df_soluciones_sigma.columns[:-1], epsilon], axis=1)
        
        # Verifico si df_soluciones_fi_ijkjk existe
        global df_soluciones_fi_ijkjk
        if len(df_soluciones_fi_ijkjk.columns)== 0:
            df_soluciones_fi_ijkjk=df_fi_ijkjk.set_index(['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp'],drop=False).loc[:,df_fi_ijkjk.columns=='fi_ijkjk'] #Creo un dataframe para almacenar los fi_ijkjk que se van generando
            df_soluciones_fi_ijkjk.set_axis([*df_soluciones_fi_ijkjk.columns[:-1], epsilon], axis=1, inplace=True)
        else:
            df_soluciones_fi_ijkjk=pd.merge(df_soluciones_fi_ijkjk,
                                            df_fi_ijkjk.set_index(['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp'],drop=False)['fi_ijkjk'],
                                            left_on=['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp'],right_on=['nombre_I','nombre_J','servicio_K','nombre_Jp','servicio_Kp'], how='left')
            df_soluciones_fi_ijkjk.set_axis([*df_soluciones_fi_ijkjk.columns[:-1], epsilon], axis=1, inplace=True)
        
    
    # Función para generar los factores de las bisecciones:
    def funcion_bisec(self,factor):
        '''
        El método pide dividir las líneas entre dos puntos ancla y obtener un punto medio. 
        La coordenada en y de ese punto medio corresponde a:
        y1+(y2-y1)*salida
        El factor se va haciendo cada vez más pequeño. Primero se divide la línea en dos, luego en cuatro,
        luego en ocho y así sucesivamente. 
        La función genera la variable "salida" que define la fracción del segmento que se va a utilizar para hallar el nuevo punto.
        '''
        num=1
        denom=2
        n=0
        while n<=factor:
            
            #print (salida)
            if num==denom:
                denom=denom*2
                num=1
                salida=num/denom
                num+=1
            else:
                salida=num/denom
                num+=1
            n+=1
        return salida    