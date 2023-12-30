# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:58:33 2023

@author: edgar
"""

def menu_solutions(network_original,solutions_dict):
    import textwrap
    while True:
        print("\n----------------------------------------------------------")
        print(f"Vamos a agregar soluciones a la red {network_original.name}.")
        print("----------------------------------------------------------\n")
        print("Selecciona una opción:")
        print("1. Cargar tu propia solución")
        print("2. Obtener soluciones óptimas")
        print("3. Obtener soluciones por algoritmos de búsqueda")
        print("9. Salir")

        opcion = input("Selecciona una opción: \n")

        if opcion == "1":
            print("Has seleccionado la Opción 1.")
            print (textwrap.dedent(""" \
                  Vamos a ingresar tu propia solución.
                  Se utilizarán las variables sigma_jk, tao_ijk, z_ijk
                  del archivo de datos de excel.
                  Los flujos entre nodos de servicio 
                  se calculan dividiendo el flujo saliente de cada nodo 
                  en partes iguales. Consulta la matriz df_arcos."""))
            create_solution_object(network_original,solutions_dict,name_solution="solución_subóptima")
            print ("Se ha cargado tu solución propia.")
            input("Pulsa una tecla para continuar.")
            
        elif opcion == "2":
            print("Has seleccionado la Opción 2.")
            print (textwrap.dedent(""" \
                  Vamos a obtener soluciones óptimas.
                  A continuación ingresarás a un menú para escoger
                  la función objetivo y el solver respectivo.
                  """))
                  
            # Creo el objeto solution            
            create_solution_object(network_original,solutions_dict,name_solution="temporal")
            current_solution=solutions_dict["temporal"]
            
            # Pido al usuario el objetivo
            current_solution.menu_exact_optimization(new_network=current_solution.network_copy)
            
            # Actualizo nombre de la solución en solution_dict (Ya no es "temporal")
            clave_temporal = 'temporal'
            solucion_temporal = solutions_dict[clave_temporal]
            solutions_dict[solucion_temporal.description_objective] = solutions_dict.pop(clave_temporal)
            
            
            
            input("Pulsa una tecla para continuar.")

            
            
            
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

#%% <codecell> Crear objeto solución 
def create_solution_object(network_original,solutions_dict,name_solution):
    import textwrap
    
    # Creamos un objeto solution
    #new_name_solution=input(textwrap.dedent(f""" \
    #Ingresa el nombre de la solución. 
    #Si pulsas enter se asigna '{name_solution}': """))
    #if not new_name_solution:  # Si la entrada está vacía
    new_name_solution=name_solution
    solutions_dict[new_name_solution] = Solution(name_solution=new_name_solution,
                                              objective="Nulo",
                                              name_network=network_original.name)
    solution=solutions_dict[new_name_solution]
    
    # Inserto una copia de network original en la solución como network_copy
    solution.insert_network_object(network_original)
    
    # Actualizo las matrices de solution.network_copy
    solution.network_copy.merge_niveles_capac(_post_optima=False)
    solution.network_copy.create_df_asignacion(_post_optima=False)
    solution.network_copy.create_df_probs_kk()
    solution.network_copy.create_df_arcos(_post_optima=False)


#%% <codecell> Clase Solution

class Solution:
    
    def __init__(self,name_solution,objective,name_network):
        self.name_solution=name_solution
        self.objective=objective
        self.name_network=name_network
        
    def insert_network_object (self,network_original):
        import copy
        self.network_copy=copy.deepcopy(network_original)
    
    
    def menu_exact_optimization(self,new_network):
        while True:
            print("\n----------------------------------------------------------")
            print("Menú de Optimización exacta")
            print("----------------------------------------------------------\n")
            print("1. Optimización mono-objetivo")
            print("2. Optimización multi-objetivo")
            print("3. Regresar al menú anterior")
            
            opcion1 = input("Selecciona una opción: \n")               
            if opcion1 == "1":
                print("Has seleccionado la opción 1.")
                objective_and_description=new_network.get_objective_function()
                self.objective=objective_and_description[0]
                self.description_objective=objective_and_description[1]
                
            elif opcion1 == "2":
                print("Has seleccionado la Opción 2.")         
    
            elif opcion1 == "3":
                print("Has seleccionado la Opción 3.")
                break
    
            else:
                print("Opción no válida. Inténtalo de nuevo.")

    def calculate_exact_optima(self):
        
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



# %% <codecell> Crear modelo


def set_model_abstract(objetivo, nombre_modelo, _menu_options, network, networks):

    # Cargamos las librerías de Pyomo
    import pyomo.environ as pyo
    import re
    import math
    from hcndp import network_data
    import copy

    # %% <codecell> Conjuntos
    # Defino el modelo y los conjuntos
    model = pyo.AbstractModel()
    model.I = pyo.Set()  # Nodos de demanda
    model.J = pyo.Set()  # Instalaciones
    model.K = pyo.Set()  # Servicios

    # %% <codecell> Parámetros
    # Initializing Parameters
    # Tasas de transferencia
    model.r_q = pyo.Param(model.K, model.K, default=0)
    # Demanda de i para servicio k
    model.h = pyo.Param(model.I, model.K, default=0, mutable=True)
    model.d = pyo.Param(model.I, model.J, model.K)  # Distancia IJK ajustada
    model.x = pyo.Param(model.J, model.J)  # Enlaces j j'
    # Servidores máximos en cada jk. Capacidad de cada instalación.
    model.s = pyo.Param(model.J, model.K)
    model.c = pyo.Param(model.J, model.K)  # Capacidad de servidor jk
    model.w = pyo.Param(model.I, model.J)  # Enlaces i j
    model.M = pyo.Param()  # l número máximo de servidores en un solo jk (max de los s_jk)
    model.H = pyo.Param()  # La mayor demanda en los nodos de demanda
    model.e = pyo.Param()  # Un número muy pequeño
    # Binario si existe tasas de transferenciua
    model.r_bin_kk = pyo.Param(model.K, model.K, default=0)
    # Número máximo de servidores que se pueden contratar por servicio K. Capacidad de la red. sigma_max <= suma (s)
    model.sigma_max = pyo.Param(model.K)
    model.cap_max = pyo.Param()  # La capacidad máxima (s*c) que puede haber en un solo jk
    model.K_size = pyo.Param()  # El número de servicios del tratamiento
    model.J_size = pyo.Param()  # El número de servicios del tratamiento

    # %% <codecell> Variables
    # Initializing Variables

    model.sigma = pyo.Var(
        model.J, model.K, domain=pyo.NonNegativeIntegers, initialize=1)
    # Cantidad de servidores asignados al nodo de servicio JK

    model.rho_max = pyo.Var(within=pyo.NonNegativeReals,
                            initialize=0, bounds=(0.00, 0.99))
    # Máxima utilización en los nodos de servicio

    model.l_ijk = pyo.Var(model.I, model.J, model.K,
                          within=pyo.NonNegativeReals, initialize=1)
    # Tasa de arribos de clientes que pertenecen a i y que llegan a jk

    model.tao = pyo.Var(model.I, model.J, model.K,
                        within=pyo.NonNegativeReals, initialize=1)
    # flujo de  usuarios transferidos desde ik a jk

    model.fi = pyo.Var(model.I, model.J, model.K, model.J,
                       model.K, within=pyo.NonNegativeReals, initialize=1)
    # Proporción de usuarios de i transferidos entre j'k' y jk

    model.alpha_min = pyo.Var(within=pyo.NonNegativeReals, initialize=0)
    # Mínima accesibilidad en los nodos de demanda

    model.theta = pyo.Var(model.J, model.K, domain=pyo.Binary, initialize=0)
    # Variable artificial para determinar si hay capacidad instalada en jk

    model.alpha_ik = pyo.Var(
        model.I, model.K, domain=pyo.NonNegativeReals, initialize=0)
    # Accesibilidad de cada nodo de demanda ik

    model.rho_jk = pyo.Var(
        model.J, model.K, domain=pyo.NonNegativeReals, initialize=0, bounds=(0.00, 0.99))

    model.psi = pyo.Var(model.I, model.J, model.K,
                        domain=pyo.Binary, initialize=0)
    # Factor binario para asegurar que si tao_ijk>0 entonces tao_jik=0 y viceversa

    model.beta_ijk = pyo.Var(model.I, model.J, model.K,
                             domain=pyo.NonNegativeReals, initialize=0)
    # Variable auxiliar para linealizar la función de accesibilidad

    model.gamma = pyo.Var(model.I, model.J, model.K,
                          domain=pyo.Binary, initialize=0)
    # Variable artificial para determinar si hay clientes de i que visitan jk

    model.delta_ij = pyo.Var(
        model.I, model.J, domain=pyo.Binary, initialize=0, bounds=(0, 10))
    # Existe flujo desde i hasta j

    model.delta_i = pyo.Var(
        model.I, domain=pyo.NonNegativeIntegers, initialize=0, bounds=(0, 10))
    # Continuidad: Suma de lugares j visitados desde i

    model.delta_min = pyo.Var(domain=pyo.NonNegativeReals, initialize=0)
    # Continuidad mínima en la red

    model.Lq_jk = pyo.Var(
        model.J, model.K, domain=pyo.NonNegativeReals, initialize=0)
    # Longitud de cola en el sitio jk

    # %% <codecell> Restricciones
    # Restricciones
    def restr_uno_rule(model, i, k):
        # Flujos desde origen ik a nodo servicio ijk es hik
        # if k=='k01':
        #    return sum(model.tao[i,j,k] for j in model.J) == model.h[i,k]
        # else:
        #    return pyo.Constraint.Skip
        return sum(model.tao[i, j, k] for j in model.J) == model.h[i, k]
    model.restr_uno = pyo.Constraint(model.I, model.K, rule=restr_uno_rule)

    def restr_dos_rule(model, i, j, k):
        # Flujo entrante
        return model.l_ijk[i, j, k] == model.tao[i, j, k]+sum(model.fi[i, j_p, k_p, j, k] for j_p in model.J for k_p in model.K)
    model.restr_dos = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_dos_rule)

    def restr_tres_rule(model, i, jp, kp, k):
        # La suma de flujo saliente es igual al entrante
        # return model.l_ijk[i,jp,kp] >= sum(model.fi[i,jp,kp,j,k] for j in model.J for k in model.K)
        return model.l_ijk[i, jp, kp] * model.r_q[kp, k] == sum(model.fi[i, jp, kp, j, k] for j in model.J)
    model.restr_tres = pyo.Constraint(
        model.I, model.J, model.K, model.K, rule=restr_tres_rule)

    def restr_cuatro_rule(model, i, kp, kpp):
        # El porcentaje de pacientes que pasan de k' a k es r_k'k
        return sum(model.fi[i, jp, kp, j, k] for jp in model.J for j in model.J for k in model.K)*model.r_q[kp, kpp] == sum(model.fi[i, jp, kp, jpp, kpp] for jp in model.J for jpp in model.J)
    #model.restr_cuatro = pyo.Constraint (model.I,model.K,model.K, rule=restr_cuatro_rule)

    def restr_cinco_rule(model, i, jp, kp, j, k):
        # Existe flujo fi_ijkjk si hay enlace, hay probabilidad, y hay capacidad
        return model.fi[i, jp, kp, j, k] <= model.x[jp, j]*model.r_bin_kk[kp, k]*model.sigma[j, k]*model.c[j, k]
    model.restr_cinco = pyo.Constraint(
        model.I, model.J, model.K, model.J, model.K, rule=restr_cinco_rule)

    def restr_seis_rule(model, i, j, k):
        # Existe flujo tao_ijk si hay enlace, hay servidores en jk
        return model.tao[i, j, k] <= model.w[i, j]*model.sigma[j, k]*model.c[j, k]
    model.restr_seis = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_seis_rule)

    def restr_siete_rule(model, j, k):
        # Límites superiores para sigma
        return model.sigma[j, k] <= model.s[j, k]
    model.restr_siete = pyo.Constraint(model.J, model.K, rule=restr_siete_rule)

    def restr_ocho_rule(model, j, k):
        # Cálculo del rho_jk
        return model.rho_jk[j, k] * model.sigma[j, k] * model.c[j, k] == sum(model.l_ijk[i, j, k] for i in model.I)
    model.restr_ocho = pyo.Constraint(model.J, model.K, rule=restr_ocho_rule)

    def restr_nueve_rule(model, j, k):
        # Cálculo del rho_max
        return model.rho_max >= model.rho_jk[j, k]
    model.restr_nueve = pyo.Constraint(model.J, model.K, rule=restr_nueve_rule)

    # Nueva restricción
    # Nueva restricción
    def restr_nueve_rule_aux(model, j, k):
        return model.rho_jk[j, k] <= model.theta[j, k]
    model.restr_nueve_aux = pyo.Constraint(
        model.J, model.K, rule=restr_nueve_rule_aux)

    def restr_nueve_rule_aux_2(model, j, k):
        return model.theta[j, k] <= (model.rho_jk[j, k]) + (1-model.e)
    model.restr_nueve_aux_2 = pyo.Constraint(
        model.J, model.K, rule=restr_nueve_rule_aux_2)
    # Nueva restricción
    # Nueva restricción

    def restr_diez_rule(model, i, k):
        # Cálculo de alpha_ik
        # return model.alpha_ik[i,k] == sum ( model.sigma[j,k]*model.d[i,j,k] /
        #                                   sum (model.h[ip,kp]*model.d[ip,j,kp] for ip in model.I for kp in model.K)
        #                                    for j in model.J)
        return model.alpha_ik[i, k] == sum(model.beta_ijk[i, j, k] * model.d[i, j, k]*model.gamma[i, j, k] for j in model.J)*100
    model.restr_diez = pyo.Constraint(model.I, model.K, rule=restr_diez_rule)

    def restr_diez_rule_aux(model, i, j, k):
        # Cálculo de alpha_ik
        # return model.beta_ijk[i,j,k]*sum(model.l_ijk[ip,j,kp]*model.d[ip,j,kp] for ip in model.I for kp in model.K) == model.sigma[j,k]*model.d[i,j,k]*model.gamma[i,j,k]
        return model.beta_ijk[i, j, k]*sum(model.l_ijk[ip, j, k]*model.d[ip, j, k] for ip in model.I) == model.sigma[j, k]
    model.restr_diez_aux = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_diez_rule_aux)

    def restr_diez_rule_aux_2(model, i, j, k):
        # Si no hay capacidad sigma en jk, beta es cero.
        return model.beta_ijk[i, j, k] <= model.M*model.theta[j, k]
    model.restr_diez_aux_2 = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_diez_rule_aux_2)

    def restr_once_rule(model, i, k):
        # Cálculo del alpha min
        return model.alpha_min <= model.alpha_ik[i, k]
    model.restr_once = pyo.Constraint(model.I, model.K, rule=restr_once_rule)

    def restr_doce_rule(model, j, k):
        return model.sigma[j, k] / model.M <= model.theta[j, k]
    model.restr_doce = pyo.Constraint(model.J, model.K, rule=restr_doce_rule)

    def restr_doce_aux_2_rule(model, j, k):
        return model.theta[j, k] <= (model.sigma[j, k] / model.M) + (1-model.e)
    model.restr_doce_aux_2 = pyo.Constraint(
        model.J, model.K, rule=restr_doce_aux_2_rule)

    def restr_trece_rule(model, j, k):
        # Existe flujo tao_ijk si hay capacidad en jk (theta_jk)
        return sum(model.l_ijk[i, j, k] for i in model.I) / (model.sigma_max[k]*model.c[j, k]) <= model.theta[j, k]
    model.retr_trece = pyo.Constraint(model.J, model.K, rule=restr_trece_rule)

    def restr_trece_aux_2_rule(model, j, k):
        return model.theta[j, k] <= (sum(model.l_ijk[i, j, k] for i in model.I) / (model.sigma_max[k]*model.c[j, k])) + (1-model.e)
    model.restr_trece_aux_2 = pyo.Constraint(
        model.J, model.K, rule=restr_trece_aux_2_rule)

    def restr_catorce_rule(model, k):
        # Hay máximo sigma_max servidores en el sistema
        return sum(model.sigma[j, k] for j in model.J) <= model.sigma_max[k]
    model.restr_catorce = pyo.Constraint(model.K, rule=restr_catorce_rule)

    def restr_quince_rule(model, i, j, k):
        # No existe flujo simultáneo entre ijp y ipj
        # Se crea la restricción si wij+wji=2
        if pyo.value(model.w[i, j])+pyo.value(model.w[str(j).replace("j", "i"), str(i).replace("i", "j")]) != 2:
            return pyo.Constraint.Skip
        else:
            ip = re.findall(r'\d+', i)
            jp = re.findall(r'\d+', j)
            if ip == jp:
                return pyo.Constraint.Skip
            else:
                return model.tao[i, j, k] <= 0+model.H*(1-model.psi[i, j, k])
    model.restr_quince = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_quince_rule)

    def restr_dieciseis_rule(model, i, j, k):
        # No existe flujo simultáneo entre ij y jk
        # Se crea la restricción si wij+wji=2
        if pyo.value(model.w[i, j])+pyo.value(model.w[str(j).replace("j", "i"), str(i).replace("i", "j")]) != 2:
            return pyo.Constraint.Skip
        else:
            # Convierto tao_i2j3k1 en tao_i3j2k1
            ip = re.findall(r'\d+', i)
            jp = re.findall(r'\d+', j)
            if ip == jp:
                return pyo.Constraint.Skip
            else:
                ip = str(i).replace("i", "j")
                jp = str(j).replace("j", "i")
                return model.tao[jp, ip, k] <= 0+model.H*(model.psi[i, j, k])
    model.restr_dieciseis = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_dieciseis_rule)

    def restr_diecisiete_rule(model, i, jp, kp, j, k):
        # Si kp = k entonces el servidor destino debe ser el mismo servidor origen.
        if pyo.value(kp) == pyo.value(k) and pyo.value(jp) != pyo.value(j):
            return model.fi[i, jp, kp, j, k] == 0
        else:
            return pyo.Constraint.Skip
    model.restr_diecisiete = pyo.Constraint(
        model.I, model.J, model.K, model.J, model.K, rule=restr_diecisiete_rule)

    def restr_dieciocho_rule(model, i, j, k):
        # La distancia a recorrer por un usuario debe ser menor a la cobertura para que tenga servicio
        if pyo.value(model.d[i, j, k]) == 0:
            return model.l_ijk[i, j, k] == 0
        else:
            return pyo.Constraint.Skip
    model.restr_dieciocho = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_dieciocho_rule)

    def restr_diecinueve_rule(model, i, j, k):
        # Si existe flujo de clientes i en jk, gamma_ijk es 1.
        return model.l_ijk[i, j, k] / model.M <= model.gamma[i, j, k]
    model.restr_diecinueve = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_diecinueve_rule)

    def restr_diecinueve_aux_2_rule(model, i, j, k):
        return model.gamma[i, j, k] <= (model.l_ijk[i, j, k] / model.M) + (1-model.e)
    model.restr_diecinueve_aux_2 = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_diecinueve_aux_2_rule)

    def restr_veinte_rule(model, i, j):
        # Si existe flujo de clientes i en j, delta_ij es 1.
        return sum(model.gamma[i, j, k] for k in model.K) / model.K_size <= model.delta_ij[i, j]
    model.restr_veinte = pyo.Constraint(
        model.I, model.J, rule=restr_veinte_rule)

    def restr_veinte_aux_2_rule(model, i, j):
        return model.delta_ij[i, j] <= (model.gamma[i, j, k] for k in model.K / model.K_size) + (1-model.e)
    model.restr_veinte_aux_2 = pyo.Constraint(
        model.I, model.J, model.K, rule=restr_diecinueve_aux_2_rule)

    def restr_veintiuno_rule(model, i):
        # Creo delta i
        return model.delta_i[i] == model.J_size-sum(model.delta_ij[i, j] for j in model.J)
    model.restr_veintiuno = pyo.Constraint(model.I, rule=restr_veintiuno_rule)

    def restr_veintidos_rule(model, i):
        # Creo delta
        return model.delta_min <= model.delta_i[i]
    model.restr_veintidos = pyo.Constraint(model.I, rule=restr_veintidos_rule)

    # %% <codecell> Objetivo

    # Función objetivo
    match objetivo:
        case 1:
            model.obj = pyo.Objective(expr=model.rho_max, sense=pyo.minimize)

        case 2:
            model.obj = pyo.Objective(expr=model.alpha_min, sense=pyo.maximize)

        case 3:
            model.obj = pyo.Objective(expr=model.delta_min, sense=pyo.maximize)

        case 4:
            pass
           
        case 5:
            # Utilizo la aproximación de Sakasegawa 1977 para obtener Lq
            def obj_rule(model):
                sumaL_jk = 0
                for j in model.J:
                    for k in model.K:
                        num = model.rho_jk[j, k]**math.sqrt(
                            2*(pyo.value(model.sigma[j, k])+1))
                        denom = 1-model.rho_jk[j, k]
                        L_jk = num / denom
                        sumaL_jk += L_jk
                return sumaL_jk

            model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        case 6:
            pass
           
    # %% <codecell> Nuevo objeto en networks

    # Creo objeto Model_pyomo dentro de networks.network.models
    network.models[nombre_modelo] = network_data.Model_pyomo(
        model_abstract=model,
        instance=None,
        data_dat=None,
        solution=None,
        nombre_modelo=nombre_modelo)

    # Creo objeto network dentro de networks
    _copia = copy.deepcopy(networks[str(network.name)])
    networks[nombre_modelo] = _copia
    networks[nombre_modelo].models=None
    networks[nombre_modelo].name=nombre_modelo
    
# %% <codecell> Instanciar


def read_data_dat(network,model):
    import os
    model.data_dat = os.getcwd()+'/data/'+network.name+'/datos.dat'


def set_instance(model_abstract, file_dat, objective, model):
    import pyomo.environ as pyo
    instance = model_abstract.create_instance(file_dat)
    model.instance = instance
    if objective == 4:
        model.instance.obj = \
            pyo.Objective(expr=sum(model.instance.alpha_ik[i, k] *
                                   sum(model.instance.h[i, kp]
                                       for kp in model.instance.K) for i in model.instance.I for k in model.instance.K)
                          / sum(sum(model.instance.h[i, kp] for kp in model.instance.K)
                                for i in model.instance.I for k in model.instance.K), sense=pyo.maximize)
    if objective == 5:
        for j in model.instance.J:
            for k in model.instance.K:
                model.instance.rho_jk[j, k].setlb(0.000000000000001)
                model.instance.rho_jk[j, k].value = 0.000000000000001
    if objective == 6:
        model.instance.obj = pyo.Objective(expr=sum(model.instance.delta_i[i] *
                                                    sum(model.instance.h[i, k] for k in model.instance.K) for i in model.instance.I) /
                                           sum(model.instance.h[i, k]
                                               for i in model.instance.I for k in model.instance.K),
                                           sense=pyo.maximize)


# %% <codecell> Resolver

def solve_gurobi(network, model, instance):
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
    elif (results.solver.termination_condition == pyo.TerminationCondition.infeasible):
        out = "infeasible"
    elif (results.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit):
        out = "MaxTimeLimit"
        print("MaxTimeLimit")
    else:
        out = "error"
        print("Solver Status: ",  results.solver.status)


def solve_ipopt(network,model, instance):
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


# %% <codecell> Grados de libertad
def get_degrees_freedom(instance):
    # Todo: import the degrees_of_freedom function from the idaes.core.util.model_statistics package
    from idaes.core.util.model_statistics import degrees_of_freedom
    from idaes.core.util.model_statistics import report_statistics
    print("Degrees of Freedom =", degrees_of_freedom(instance))
    print("Statistics =", report_statistics(instance))

# %% <codecell> Exportar solución


def set_solution_excel(network,instance):
    import numpy as np
    import pyomo.environ as pyo
    import pandas as pd
    import xlsxwriter
    import os
    import openpyxl
    # Obtengo los valores de las variables según el modelo de optimización
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
    output = os.getcwd()+'/output/'+network.name+'/salida_optimizacion.xlsx'
    workbook = xlsxwriter.Workbook(output)
    workbook.close()
    path = output
    with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        writer.workbook = openpyxl.load_workbook(path)
        pd.DataFrame(l_jk).to_excel(writer, sheet_name='l_jk')
        pd.DataFrame(l_ijk).to_excel(writer, sheet_name='l_ijk')
        pd.DataFrame(f_ijk, columns=['nombre_I', 'nombre_J', 'servicio_K', 'tao_ijk']).to_excel(
            writer, sheet_name='f_ijk')  # Corresponde a los tao_ijk
        
        pd.DataFrame(prob_fi_jkjk, columns=['nombre_J', 'servicio_K', 'nombre_Jp', 'servicio_Kp','Probs']).to_excel(
            writer, sheet_name='prob_fi_jkjk')
        
        pd.DataFrame(sigma_jk).to_excel(writer, sheet_name='sigma')
        pd.DataFrame(fi_ijkjk, columns=['nombre_I', 'nombre_J', 'servicio_K', 'nombre_Jp',
                     'servicio_Kp', 'fi_ijkjk']).to_excel(writer, sheet_name='fi_ijkjk')


def set_solution_txt(network,instance):

    ##########################################
    #Imprimir resultados en un achivo ####
    ##########################################
    import os

    output = os.getcwd()+'/output/'+network.name+'/modeloysolucion.txt'

    with open(output, 'w') as output_file:
        # output_file.write(instance.pprint())
        instance.pprint(output_file)

    instance.display(os.getcwd()+'/output/'+network.name+'/solucion.txt')

    # Imprimir contenidos de una variable #####
    # for v in instance.component_objects(Var):
    #    for index in instance.v:
    #        print('{0} = {1}'.format(instance.v[index], value(instance.v[index])))

    #########################################


def update_solution_post_optima(original_network,new_network):
    from hcndp import read_data
    import os 
    print ("Ejecutando update_solution_post_optima")
    input()
    new_network.create_folders()
    path=os.getcwd()+'/data/'+original_network.name+'/'+new_network.archivo
    
    import shutil
    
    # Combinar las rutas para obtener las rutas completas
    ruta_origen = os.getcwd()+'/output/'+original_network.name+'/'+'salida_optimizacion.xlsx'
    ruta_destino = os.getcwd()+'/output/'+new_network.name+'/'+'salida_optimizacion.xlsx'
    
    # Intentar copiar el archivo
    try:
        # shutil.copy() realiza una copia superficial del archivo
        shutil.copy(ruta_origen, ruta_destino)
        print(f"Archivo '{new_network.archivo}' /salida_optimizacion.xlsx copiado con éxito.")
    except FileNotFoundError:
        print(f"El archivo '{new_network.archivo}' /salida_optimizacion.xlsx no fue encontrado en carpeta origen.")
    except PermissionError:
        print(f"No tienes permisos para copiar el archivo {new_network.name} /salida_optimizacion.xlsx .")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    read_data.read_parameters(new_network)
    read_data.read_file_excel(new_network,path)
    read_data.delete_surplus_data(new_network)
    read_data.merge_niveles_capac(new_network,post_optima=True)
    read_data.create_df_asignacion(new_network,post_optima=True)
    read_data.create_df_probs_kk(new_network)
    read_data.create_df_arcos(new_network,post_optima=True)


# %% <codecell> main
if __name__ == "__main__":
    from hcndp import network_data
    #import os

    _model_abstract = set_model_abstract(lexicografico=0)

    model = network_data.Model_pyomo(
        model_abstract=_model_abstract, instance=None, data_dat=None, solution=None)

    model.data_dat = read_data_dat(model)
    model.instance = set_instance(model.model_abstract, model.data_dat)

    solve_gurobi(model.instance)

    get_degrees_freedom(model.instance)

    set_solution_excel(model.instance)
    set_solution_txt(model.instance)

