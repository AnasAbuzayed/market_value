# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 06:56:01 2025

@author: Anas
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.dates as mdates
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')

cmap='Spectral_r'
ETS_s=300
gp=60
ref_year=2021
times=pd.date_range(start=f'{ref_year}-01-01',
                    end=f'{ref_year}-12-31 23:00:00',
                    freq='H')

years_merit={}
p_scenario={}
scenarios=['A','B','C']
m='gas'
for sc in scenarios:
    print(sc)
    years_merit[sc]=pd.read_excel\
        (f'Results/{sc}_{m}/Merit_{ETS_s}C_{gp}G.xlsx',
          index_col=0,parse_dates=True,
          sheet_name=str(ref_year))
    p_scenario[sc]=pd.read_excel\
        (f'Results/{sc}_{m}/Energy_{ETS_s}C_{gp}G.xlsx',
          index_col=0,parse_dates=True,
          sheet_name=str(ref_year))

v_max=350
v_min=-50


# Hours start at 0, length 2



days=np.arange(8760/24)+1
hours = np.arange(24)
scenarios=['A',0,'B',0,'C']


normalizer = Normalize(v_min, v_max)
im = cm.ScalarMappable(norm=normalizer,cmap=cmap)


fig, axes = plt.subplots(nrows=len(scenarios)+1,figsize=(18,10),
                         gridspec_kw={'height_ratios': [2,0.5]*int((len(scenarios)+1)/2)})
plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=1, 
                    wspace=0.4, 
                    hspace=0.4)

for i,sc in enumerate(scenarios):
    if sc == 0 :
        continue
    temp = years_merit[sc]['Price']
    temp = temp.values.reshape(len(hours), len(days), order="F")
    days=pd.date_range(f'1/1/{ref_year}', periods=len(days), freq='D')
    data=pd.DataFrame({'Price':years_merit[sc]['Price']})
    data['date']=data.index
    data=data.groupby(data.date.dt.month).mean().T


    mesh=axes[i].pcolormesh(days, hours, temp,cmap=cmap,
                            vmin= v_min, vmax= v_max)
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    axes[i].xaxis.set_major_locator(mdates.MonthLocator())
    axes[i].set_yticks(labels=list(range(0,25,4)),ticks=list(range(0,25,4)),
                       rotation='horizontal')
    axes[i].set_ylabel("Hour of the day",fontsize=11)
    ax2 = axes[i].twinx()   
    ax2.set_yticks([])
    ax2.set_ylabel("Average Price\n{} Eur/MWh"\
                   .format(round(years_merit[sc]['Price'].mean(),2), )
                   ,fontsize=11)


    

    axes[i+1].imshow(data,aspect='auto',cmap=cmap,vmin=0,vmax=500)
    axes[i+1].set_yticks([])
    axes[i+1].set_xticks([])
    # axes[i+1].set_ylabel("Mean",fontsize=11)
    axes[i+1].set_xlabel(f"Scenario {sc}",fontsize=11)


cb=fig.colorbar(im, ax=axes.ravel().tolist(),cmap=cmap)
cb.set_label(label='Eur/MWh',weight='bold',fontsize=16)
plt.savefig('Figures/Hourly Prices.png', dpi=600,bbox_inches='tight')



