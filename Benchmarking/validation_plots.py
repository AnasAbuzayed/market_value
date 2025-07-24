# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 04:27:07 2025

@author: Anas
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (mean_squared_error, 
                             mean_absolute_error)
from sklearn.metrics import r2_score
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')

gas_corrected=pd.read_csv('Data/TTF_corrected.csv',index_col=0,
                          parse_dates=True)
oil_corrected=pd.read_csv('Data/oil_corrected.csv',index_col=0,
                          parse_dates=True)
coal_corrected=pd.read_csv('Data/coal_corrected.csv',index_col=0,
                          parse_dates=True)
EU_ETS_original=pd.read_excel('Data/ETS_DE.xlsx',parse_dates=True,index_col=0)
real_price_original=pd.read_excel('Data/Price.xlsx',parse_dates=True,index_col=0)


gas_corrected=gas_corrected.reindex(EU_ETS_original.index).ffill()
coal_corrected=coal_corrected.reindex(EU_ETS_original.index).ffill()
oil_corrected=oil_corrected.reindex(EU_ETS_original.index).ffill()



temp=pd.concat([real_price_original,gas_corrected,
                oil_corrected,coal_corrected,
                ],axis=1)

temp.columns=['DA Auction','Natural Gas','Oil','Coal']





fig, ax = plt.subplots(figsize=(11,6))
temp.resample('D').mean().plot(lw=0.9,ax=ax,
                                  color=['#235ebc','r','k','#9e5a01'],alpha=0.7)
plt.ylabel('Eur/MWh',fontsize=14)
plt.xlabel('')
plt.grid()
ax.set_yticks(range(-50,750,150))
ax2=ax.twinx()
EU_ETS_original.resample('D').mean().plot(lw=0.9,ax=ax2,color=['#2ca02c'],alpha=0.7)
plt.ylabel('Eur/tCO2',fontsize=14)
ax2.set_yticks(range(0,101,10))
lines, labels = ax.get_legend_handles_labels()
lines.extend(ax2.get_legend_handles_labels()[0])
labels.extend(ax2.get_legend_handles_labels()[1])
for line in lines:
    line.set_linewidth(2.0)
ax.legend(lines,labels,ncol=2, loc="upper left",fontsize=14)
ax2.legend("")
plt.savefig('Figures/Commodoties',dpi=300,bbox_inches='tight')





years=list(range(2019,2025))
scenarios={}
model_price=real_price_original.copy()
model_price.columns=['Model']

for year in years:
    scenarios[year]=pd.read_excel\
        (f'Output/{year}.xlsx',
          index_col=0,parse_dates=True)
    model_price.loc[str(year)]=scenarios[year].copy()


price_both=pd.concat([model_price,
                      real_price_original],axis=1)
price_both.columns=['Model','Real']

price_both.groupby(price_both.index.year).mean()
price_both.groupby(price_both.index.year).describe()[[('Model','std'),('Real','std')]]


q=0.0
price_both=price_both[(price_both<=price_both.quantile(1-q))
            &
            (price_both>=price_both.quantile(q).iloc[1])]

price_both.dropna(inplace=True)


price_both.corr()




(price_both.resample('D').max() - price_both.resample('D').min()).resample('Y').mean()



print('quantile',q)
for year in years:
    temp=price_both.loc[str(year)]
    std=round(temp.describe().loc['std','Model'],2)
    temp=temp.resample('D').mean()
    x=np.array(temp.Real.dropna())
    y=np.array(temp.Model.dropna())
    # x[x==np.nan]=np.median(x[x!=np.nan])
    # y[y==np.nan]=0
    
    MAE=mean_absolute_error(y,x)
    RMSE=mean_squared_error(y,x, squared=False)
    print(year,'corr:',round(temp.corr().iloc[0,1],2),
          'std:',std,'RMSE:',round(RMSE,2),'MAE:',round(MAE,2),
          'R2:',round(r2_score(x,y),2))

q=0.01
price_both=price_both[(price_both<=price_both.quantile(1-q))
            &
            (price_both>=price_both.quantile(q).iloc[1])]

price_both.dropna(inplace=True)


price_both.corr()




(price_both.resample('D').max() - price_both.resample('D').min()).resample('Y').mean()



print('quantile',q)
for year in years:
    temp=price_both.loc[str(year)]
    std=round(temp.describe().loc['std','Model'],2)
    temp=temp.resample('D').mean()
    x=np.array(temp.Real.dropna())
    y=np.array(temp.Model.dropna())
    # x[x==np.nan]=np.median(x[x!=np.nan])
    # y[y==np.nan]=0
    
    MAE=mean_absolute_error(y,x)
    RMSE=mean_squared_error(y,x, squared=False)
    print(year,'corr:',round(temp.corr().iloc[0,1],2),
          'std:',std,'RMSE:',round(RMSE,2),'MAE:',round(MAE,2),
          'R2:',round(r2_score(x,y),2))


#special case
temp=price_both.loc['2021-06-01':'2022-05-31']
temp=temp.resample('D').mean()
x=np.array(temp.Real.dropna())
y=np.array(temp.Model.dropna())
MAE=mean_absolute_error(y,x)
RMSE=mean_squared_error(y,x, squared=False)
print('Special case','RMSE:',round(RMSE,2),'MAE:',round(MAE,2),
      'corr:',round(temp.corr().iloc[0,1],2),'R2:',round(r2_score(x,y),2))


#plot
fig, ax = plt.subplots(figsize=(11,6))
price_both.resample('D').mean().plot(lw=0.6,alpha=0.7,ax=ax)
plt.ylabel('Eur/MWh',fontsize=14)
plt.xlabel('')
plt.grid()
plt.legend(fontsize=14)
plt.savefig('Figures/DA_vs_Model',dpi=300,bbox_inches='tight')

