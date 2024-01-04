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
                print ("No puedo imprimir las imágenes.")
                print ("Revisa si has importado los datos.")

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
        self.menu_options = {
           '1': 'Rho --> Alpha --> Delta',
           '2': ' Rho --> Delta --> Alpha',
           '3': ' Alpha --> Rho --> Delta',
           '4': ' Alpha --> Delta --> Rho',
           '5': ' Delta --> Rho --> Alpha',
           '6': ' Delta --> Alpha --> Rho',
           '7': ' Delta = k --> Rho --> Alpha',
           '8': ' Delta = k --> Alpha --> Delta',
           '9': ' Rho --> Alpha',
           '10': ' Alpha --> Rho'}
        
        
    def select_objectives(self):
        
        _menu_options = self.menu_options
    
        while True:
            print("\n----------------------------------------------------------")
            print("Selección de objetivos y su orden")
            print("----------------------------------------------------------\n")            
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
           '1': 'Técnicas exactas',
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

    
    def anchor_points(self,matrix_problems_lexi,problem_lexi):
         from hcndp import solutions
         import pyomo.environ as pyo
         
         #problem_lexi es una fila de matreix_problems_lexi
         # Creo el objeto solution
         solutions.create_solution_object(
                 network_original=self.network, 
                 problems_dict=self.problems_multi_dict, 
                 name_solution=problem_lexi[1])
         
         current_solution = self.problems_multi_dict[problem_lexi[1]]
         
         # Ingeso el objetivo
         current_solution.objective = problem_lexi[0]
         current_solution.description_objective = problem_lexi
         current_solution.name_solution = problem_lexi[1]
         
         # Obtener solución para primer objetivo
         if problem_lexi[0]==1:
             current_solution.construct_model()
         
         elif problem_lexi[0]==2:
            current_solution.construct_model()
            model=current_solution.pyo_model.model_abstract
            
            _var_obj_actual=model.alpha_min
            _sense=pyo.maximize
            
            # MAximizar alpha min
            # Agrego restricción y agrego función objetivo 
            self.lexicograf(model,
                       _var_obj_anterior='rho_max', 
                       _func_obj_anterior='Min_Rho_Max')
            
            model.del_component(model.obj)
            model.obj = pyo.Objective(expr=_var_obj_actual,sense=_sense) 
            del current_solution.pyo_model.instance
            
         elif problem_lexi[0]==3:
            current_solution.construct_model()
            
            model=current_solution.pyo_model.model_abstract
            
            _var_obj_actual=model.alpha_min
            _sense=pyo.maximize

            # MAximizar alpha min
            # Agrego restricción y agrego función objetivo             
            self.lexicograf(model,
                       _var_obj_anterior='rho_max', 
                       _func_obj_anterior='Min_Rho_Max')
            
            # MAximizar delta min
            # Agrego restricción y agrego función objetivo             
            self.lexicograf(model,
                       _var_obj_anterior='alpha_min', 
                       _func_obj_anterior='Max_Alpha_Min')
            
            _var_obj_actual=model.delta_min
            _sense=pyo.maximize
            
            model.del_component(model.obj)
            model.obj = pyo.Objective(expr=_var_obj_actual,sense=_sense) 
            del current_solution.pyo_model.instance
                        
            
         current_solution.construct_instance()
         current_solution.execute_solver()
         self.anclas.append([problem_lexi[1],pyo.value(current_solution.pyo_model.instance.obj)])
         print (self.anclas)
         
    def lexicograf(self,model,_var_obj_anterior,_func_obj_anterior):
        import pyomo.environ as pyo
        restriccion = getattr(model, _var_obj_anterior) <= pyo.value(self.problems_multi_dict[_func_obj_anterior].pyo_model.instance.obj)
        setattr(model, f'restriccion_{_var_obj_anterior}', pyo.Constraint(expr=restriccion))

    
    def calculate_lexicographic(self):
        
        if self.objectives_sequence==1:
            matrix_problems_lexi=[[1,"Min_Rho_Max"],
                                  [2,"Max_Alpha_Min"],
                                  [3,"Max_Delta_Min"]]
            
            #%% Primer objetivo
            self.anchor_points(matrix_problems_lexi,problem_lexi=matrix_problems_lexi[0])
            

            #%% Segundo objetivo
            self.anchor_points(matrix_problems_lexi,problem_lexi=matrix_problems_lexi[1])
             
            #%% Tercer objetivo
            self.anchor_points(matrix_problems_lexi,problem_lexi=matrix_problems_lexi[2])
            
            
    
    
   