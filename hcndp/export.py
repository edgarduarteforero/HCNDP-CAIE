# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 18:29:12 2023

@author: edgar
"""
           
def export_data(network):
    import pandas as pd
    import os
    output_file=os.getcwd()+'/output/'+'salida.xlsx'
        
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Iterar a través del diccionario y escribir cada DataFrame en una hoja
        for sheet_name, df in network.file.items():
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=sheet_name, index=False)
