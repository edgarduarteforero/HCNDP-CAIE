# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:49:18 2024

@author: edgar
"""

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
for i in range (1,27):
    for j in range (1,27):
        for k in range (1,11):
                texto="i"+f"{i:02d}","j"+f"{j:02d}","k"+f"{k:02d}"
                #l.append(str(texto))
                l.append(["i"+f"{i:02d}","j"+f"{j:02d}","k"+f"{k:02d}"])
                print("i"+f"{i:02d}","j"+f"{j:02d}","k"+f"{k:02d}")


df=pd.DataFrame(l)


writer = pd.ExcelWriter('Libro3.xlsx', engine='xlsxwriter')

#Escribimos los datos de un dataframe en el archivo de Excel
df.to_excel(writer,"Hoja1")

#writer.save()
writer.close()