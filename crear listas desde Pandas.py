# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 15:37:59 2022

@author: edgar
"""

################################################3
#Importar datos desde Excel con Pandas
import pandas as pd
file='salida.xlsx'

#Cargamos el libro

#df=pd.read_excel(file, header=0, sheet_name="df_probs")

import numpy as np
import pandas as pd
l=[]
for j in range (1,27):
    for k in range (1,11):
        for j_ in range (1,27):
            for k_ in range (1,11):
                texto="j"+f"{j:02d}","k"+f"{k:02d}","j_"+f"{j_:02d}","k_"+f"{k_:02d}"
                #l.append(str(texto))
                l.append(["j"+f"{j:02d}","k"+f"{k:02d}","j_"+f"{j_:02d}","k_"+f"{k_:02d}"])
                print("j"+f"{j:02d}","k"+f"{k:02d}","j_"+f"{j_:02d}","k_"+f"{k_:02d}")


df=pd.DataFrame(l)


writer = pd.ExcelWriter('Libro3.xlsx', engine='xlsxwriter')

#Escribimos los datos de un dataframe en el archivo de Excel
df.to_excel(writer,"Hoja1")

#writer.save()
writer.close()
