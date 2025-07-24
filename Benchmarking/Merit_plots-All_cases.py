# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/market_value

Description:
This repository provides the code and supporting materials for the research article:

From Model Optimality to Market Reality: Do Electricity Markets Support Renewable Investments?

The study investigates the gap between model-based optimal dispatch and actual market outcomes in electricity markets, and evaluates how effectively price signals incentivize renewable expansion. 

"""

import pypsa
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import Circle
from matplotlib.offsetbox import AnnotationBbox, DrawingArea, TextArea
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')

n=pypsa.Network('Output/2021.nc')
colors = {
          "Hydro" : "#4adbc8",
          "Lignite" : "#9e5a01",
          "Hard coal" : "#707070",
          "Oil" : "k",
          "VOLL" : "#4B0082",
          "Natural gas" : "#b20101",
          "Bioenergy" : "#0c6013",
          "Wind offshore" : "#6895dd",
          "Wind onshore" : "#235ebc",
          "Photovoltaics" : "#f9d002",
          "Waste":"#8a1caf",
          "PHS":"#08ad97",
          'Nuclear':'indigo'}
def roundup(x):
    return x if x % 5== 0 else x + 5- x % 5
hour='2021-07-22 16:00:00'
hour1='2021-02-07 15:00:00'
x=(n.loads_t.p.loc[hour].sum() - n.storage_units_t.p.loc[hour,'DE0 PHS'])/1e3
temp=pd.concat([n.generators_t.p.loc[hour],
                n.generators_t.marginal_cost.loc[hour]],axis=1)
temp1=pd.concat([n.generators_t.p.loc[hour1],
                n.generators_t.marginal_cost.loc[hour1]],axis=1)



temp.columns=['capacity','Marginal Cost']
temp1.columns=['capacity','Marginal Cost']
temp1.drop(n.generators_t.p_max_pu.columns,inplace=True)


temp=temp[temp.capacity!=0]
temp1=temp1[temp1.capacity!=0]




temp=pd.concat([temp,temp1],axis=0)
# temp=temp.T

temp['Marginal Cost'].fillna(0,inplace=True)




temp=temp.sort_values(by='Marginal Cost')
temp.capacity=temp.capacity.cumsum()/1e3

temp['carrier']=n.generators.carrier.loc[temp.index]

# temp['Marginal Cost'].replace(0,1,inplace=True)

x=64
y = np.interp(x, temp.capacity, 
              temp['Marginal Cost'])


fig,ax=plt.subplots(figsize=(17, 6))
plt.bar(temp.capacity,
        temp['Marginal Cost'],
        width=-temp.capacity.diff().fillna(0),
        color=[colors[col] for col in temp.carrier],
        lw=1,align='edge')
plt.grid()
patches=[]
for tech in temp.carrier.unique():
    patches.append(mpatches.Patch(color=colors[tech], label=tech))
patches.append(mpatches.Patch(color='orange', label='Market Equilibrium',
                              linestyle='--',fill=False,lw=2))
ax.legend(handles=patches,loc='best',ncol=2,
          fontsize=11,fancybox=True,frameon=True,
          title='Technologies',title_fontsize=14)
plt.plot([80,80],[-10,80],
         color = 'orange', 
         linestyle = '--',
         label='Market Equilibrium',lw=6)
plt.plot([20,20],[-40,15],
         color = 'orange', 
         linestyle = '--',
         label='Market Equilibrium',lw=6)
plt.plot([40,40],[-15,20],
         color = 'orange', 
         linestyle = '--',
         label='Market Equilibrium',lw=6)

circle_points = [(77, 80, '1'), (18, -28, '2'), (38, 5, '3')]
for x_val, y_val, label in circle_points:
    da = DrawingArea(30, 30, 0, 0)  

    circ = Circle((15, 15), 14, fill=False, edgecolor='black', linewidth=1.5)
    da.add_artist(circ)

    txt = TextArea(label, textprops=dict(color='black', weight='bold', ha='center', va='center', fontsize=10))
    ab = AnnotationBbox(da, (x_val, y_val), xycoords='data', frameon=False, box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

    ax.text(x_val, y_val, label, ha='center', va='center',
            fontsize=18, fontweight='bold', color='black', zorder=6)
    


plt.xlabel('Power Plants Capacity [GW]')
plt.xlim(0,roundup(temp.capacity.max())+1)
plt.xticks(list(range(0,int(roundup(temp.capacity.max()))+1,5)))
plt.ylabel('Marginal Cost in €/MWh')
plt.savefig('Figures/Case',dpi=300,bbox_inches='tight')
