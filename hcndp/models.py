# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 07:32:43 2023

@author: edgar
"""

#  Clase modelo
class Model_pyomo:
    def __init__(self,model_abstract,instance,data_dat,solution,nombre_modelo):
        self.model_abstract=None
        self.instance=None
        self.data_dat=None
        self.solution=None
        self.nombre_modelo=None

    #%%  Definición del modelo abstracto
    def set_model_abstract(self,objetivo, nombre_modelo, _menu_options, new_network):
    
        # Cargamos las librerías de Pyomo
        import pyomo.environ as pyo
        import re
        import math
        
    
        # %%  Conjuntos
        # Defino el modelo y los conjuntos
        model = pyo.AbstractModel()
        model.I = pyo.Set()  # Nodos de demanda
        model.J = pyo.Set()  # Instalaciones
        model.K = pyo.Set()  # Servicios
    
        # %%  Parámetros
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
    
        # %%  Variables
        # Initializing Variables
    
        model.sigma = pyo.Var(
            model.J, model.K, domain=pyo.NonNegativeIntegers, initialize=1)
        # Cantidad de servidores asignados al nodo de servicio JK
    
        model.rho_max = pyo.Var(domain=pyo.NonNegativeReals,initialize=0) #within=pyo.NonNegativeReals,                                initialize=0,within=pyo.NonNegativeReals
       # model.rho_max=Var(within=NonNegativeReals,initialize=0,within=NonNegativeReals)#bounds=(0.00,0.99)  

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
    
        # %%  Restricciones
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
            return model.tao[i, j, k] <= model.w[i,j]*model.sigma[j, k]*model.c[j, k]
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
    
        # %%  Objetivo
        # Función objetivo
        match int(objetivo):
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
        
        # %%  Modelo abstracto en model_abstract
        self.model_abstract=model
    
    # %%  Cambio de la variable sigma por parámetro sigma 
    def var_sigma_to_param (self,model_abstract):
        import pyomo.environ as pyo
        
        # Eliminar la variable model.sigma del modelo
        model_abstract.del_component(model_abstract.sigma)

        # Crear un nuevo parámetro con los mismos índices y valores que model.sigma
        model_abstract.sigma = pyo.Param(model_abstract.J, model_abstract.K, initialize=0)
        #model_abstract.add_component(model_abstract.J, model_abstract.K)
        
        return model_abstract        