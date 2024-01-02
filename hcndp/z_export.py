# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 18:29:12 2023

@author: edgar
"""
           
def export_data(network):
    import pandas as pd
    import os
    output_file=os.getcwd()+'/output/'+network.name+'/salida_medicion.xlsx'
        
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Iterar a través del diccionario y escribir cada DataFrame en una hoja
        for sheet_name, df in network.file.items():
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=sheet_name, index=True)

def create_index_sheet(network):
    # TODO Personalizar el texto que explica cada hoja. 
    # Específicamente la variable sheet_ref
    
    #Creo una hoja con índices en el archivo de excel
    import openpyxl
    import os
    from openpyxl import Workbook
    #from openpyxl.styles import Hyperlink
    
    from openpyxl.styles import NamedStyle
    from openpyxl.styles import NamedStyle, Font, colors

    hyperlink_style = NamedStyle(name='Hyperlink', font=Font(color=colors.BLUE, underline='single'))


    
    # Nombre del archivo Excel
    excel_file = os.getcwd()+'/output/'+network.name+'/salida_medicion.xlsx'
    
    # Cargar el archivo existente
    workbook = openpyxl.load_workbook(excel_file)
    
    # Crear una nueva hoja para el índice
    index_sheet = workbook.create_sheet('Índice', 0)
    
    # Encabezado del índice
    index_sheet['A1'] = 'Hoja'
    index_sheet['B1'] = 'Referencia'
    index_sheet['C1'] = 'Enlace'
    
    # Obtener una lista de nombres de hojas en el archivo
    sheet_names = workbook.sheetnames
    
    # Llenar el índice con nombres de hojas, referencias y enlaces
    for row, sheet_name in enumerate(sheet_names, start=2):
        sheet_ref = f"'{sheet_name}'!A1"  # Referencia de celda en la hoja
        sheet_link = f'#{sheet_name}!A1'  # Enlace a la hoja
        index_sheet.cell(row=row, column=1, value=sheet_name)
        index_sheet.cell(row=row, column=2, value=sheet_ref)
        #index_sheet.cell(row=row, column=3, value=sheet_link)
        index_sheet.cell(row=row, column=3, value=sheet_link).style = hyperlink_style
        index_sheet.cell(row=row, column=3).hyperlink = sheet_link
        
    # Guardar el archivo actualizado
    workbook.save(excel_file)

def create_data_dat(network):
    import os
    from hcndp.data_functions import indices
    
    path=os.getcwd()+'/data/'+network.name+'/datos.dat'

    I=network.I
    J=network.J
    K=network.K 
    
    file= open(path,"w+")
    
    def indices_data_dat(letra,cantidad): # Se generan listas tipo j01,j02,j03
        file.write("set %s := "% letra)
        for i in range (1,cantidad+1):
            file.write(letra.lower()+f"{i:02d}"+" ")
        file.write(";\n\n")
    
    indices_data_dat("I",I)
    indices_data_dat("J",J)
    indices_data_dat("K",K)


    df_probs_kk=network.file['df_probs_kk']
    df_demanda=network.file['df_demanda']   
    df_capac=network.file['df_capac']
    df_flujos_jj=network.file['df_flujos_jj']
    df_asignacion=network.file['df_asignacion']
    df_w_ij=network.file['df_w_ij']
    df_sigma_max=network.file['df_sigma_max']
    
    
    #Escribo los r_q
    file.write("param %s := \n"%"r_q")
    file.write(df_probs_kk[['servicio_K','servicio_Kp','p_kkp']].to_string(header=False, index=False))
    file.write(";\n\n")
    
    #Escribo los h
    file.write("param %s := \n"%"h")
    file.write(df_demanda.reset_index()[['nombre_I','servicio_K','h_ik']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    #Escribo los s
    file.write("param %s := \n"%"s")
    file.write(df_capac.reset_index()[['nombre_J','servicio_K','s_jk']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    #Escribo los c
    file.write("param %s := \n"%"c")
    file.write(df_capac.reset_index()[['nombre_J','servicio_K','c_jk']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    #Escribo los x
    file.write("param %s := \n"%"x")
    file.write(df_flujos_jj.reset_index()[['nombre_J','nombre_Jp','x_jjp']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    
    #Escribo los d
    file.write("param %s := \n"%"d")
    file.write(df_asignacion[['nombre_I','nombre_J','servicio_K','f_dij']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    #Escribo los w
    file.write("param %s := \n"%"w")
    file.write(df_w_ij.reset_index()[['nombre_I','nombre_J','w_ij']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    # Escribo M. El número máximo de servidores en un solo jk (max de los s_jk)
    file.write("#Número máximo de s_jk \n")
    file.write("param %s := \n"%"M")
    file.write(str(df_capac['s_jk'].max()))
    file.write(";\n\n")
    
    # Escribo CDemanda máxima en los nodos de demandae haber en un solo jk (max de los s_jk *c_jk)
    file.write("#Máximo de los s_jk * c_jk \n")
    file.write("param %s := \n"%"cap_max")
    file.write(str(df_capac['s_jk*c_jk'].max()))
    file.write(";\n\n")
    
    # Escribo H (Demanda máxima en los nodos de demanda)
    file.write("#Demanda máxima en los nodos de demanda \n")
    file.write("param %s := \n"%"H")
    file.write(str(df_demanda['demanda_i'].max()))
    file.write(";\n\n")
    
    file.write("param %s := \n"%"e")
    file.write("10e-3")
    file.write(";\n\n")
    
    file.write("param %s := \n"%"r_bin_kk")
    file.write(df_probs_kk[['servicio_K','servicio_Kp','bin']].to_string(header=False, index=False))
    file.write(";\n\n")
    
    file.write("param %s := \n"%"sigma_max")
    file.write(df_sigma_max[['servicio_K','sigma_max']].to_string(header=False,index=False))
    file.write(";\n\n")
    
    file.write("param %s := \n"%"K_size")
    file.write(str(K))
    file.write(";\n\n")
    
    file.write("param %s := \n"%"J_size")
    file.write(str(J))
    file.write(";\n\n")
    
    file.close()

