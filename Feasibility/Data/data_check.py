# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 23:39:27 2025

@author: Anas
"""

import pandas as pd 
import os

files={}
for file in os.listdir():
    print(file)
    if file[-4:] =='xlsx':
        
        df=pd.read_excel(file,index_col=0
                         ,parse_dates=True)
        l=[]
        for idx in df.index:
            try:        
                print(df.loc[idx].sum()+2)
            except:
                l.append(idx)
        files[file]=l



df=pd.read_excel('Forecasted gen.xlsx',index_col=0
                 ,parse_dates=True)


df.groupby([df.index.week,df.index.year]).sum().sum(axis=1).idxmin()


