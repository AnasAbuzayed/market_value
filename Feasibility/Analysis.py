# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/H2_CCGT

Description:
This script reproduces figure 2 All data used are cited in the main paper. 

"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('Figures')

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
          "small-batteries":"cyan",
          "large-batteries":"steelblue",
          'Nuclear':'indigo'}


#%% Read Data
print('Please enter scenario: A,B,C')
sc=input()
print('Please enter assumption: gas or cap')
m=input()

sc=sc.capitalize()
years=list(range(2019,2025))
ETS=list(range(25,308,25))
gas=list(range(10,61,10))

scenarios={}
p_scenario={}
for ETS_s in ETS:
    scenarios[ETS_s]={}
    p_scenario[ETS_s]={}
    for gp in gas:
        scenarios[ETS_s][gp]={}
        p_scenario[ETS_s][gp]={}
        for year in years:
            print(f'Scenario {sc} : {ETS_s}C_{gp}G_{year}')
            scenarios[ETS_s][gp][year]=pd.read_excel\
                (f'Results/{sc}_{m}/Merit_{ETS_s}C_{gp}G.xlsx',
                  index_col=0,parse_dates=True,
                  sheet_name=str(year))
            p_scenario[ETS_s][gp][year]=pd.read_excel\
                (f'Results/{sc}_{m}/Energy_{ETS_s}C_{gp}G.xlsx',
                  index_col=0,parse_dates=True,
                  sheet_name=str(year))


prices_scenarios=pd.DataFrame(0,index=ETS,
                              columns=gas)

for ETS_s in scenarios.keys():
    print(ETS_s)
    for gp in scenarios[ETS_s].keys():
        prices_scenarios.loc[ETS_s,gp]=\
            scenarios[ETS_s][gp][year].Price.mean()





#%% Average Electricity price
l=[]
for ETS_s in scenarios.keys():
    for gp in scenarios[ETS_s].keys():
        l.append(f'{ETS_s}C_{gp}G')

for year in years:
    
    times=pd.date_range(start=f'{year}-01-01',
                        end=f'{year}-12-31 23:00:00',
                        freq='H')


    Spot_ts=pd.DataFrame(0,index=times,columns=l) #Hourly Spot Prices
    
    for ETS_s in scenarios.keys():
        for gp in scenarios[ETS_s].keys():
            # for year in years:
    
            Spot_ts[f'{ETS_s}C_{gp}G'] = \
                scenarios[ETS_s][gp][year]['Price'] ### No Negative
    
    
    spot_avg=pd.DataFrame(0,index=scenarios.keys()
                    ,columns=gas) # Average Spot Prices
    
    
    for ETS_s in scenarios.keys():
        for gp in scenarios[ETS_s].keys():
            spot_avg.loc[ETS_s,gp]=Spot_ts[f'{ETS_s}C_{gp}G'].mean()
    
    
    fig, ax = plt.subplots(figsize=(10,10))
    sns.heatmap(spot_avg, linewidth=0.5,#mask=CM> 50,
                     cbar_kws={'label': f'Average Electricity Price - Scenario {sc}'},
                     cmap='RdYlGn', square=True, annot=True,
                     cbar=True,fmt=".1f",ax=ax,
                     center=35)
    ax.set_ylabel('CO2 Allowance [Eur/tCO2]')
    ax.set_xlabel('Gas Price [Eur/MWh]')
    plt.savefig(f'Figures/{m} - {sc} - Electricity prices - {year}.png',
                dpi=300,bbox_inches='tight')



y_results={}
for year in years:
    times=pd.date_range(start=f'{year}-01-01',
                        end=f'{year}-12-31 23:00:00',
                        freq='H')
    y_results[year]=pd.DataFrame(0,index=times,columns=l)
    for ETS_s in scenarios.keys():
        for gp in scenarios[ETS_s].keys():
                y_results[year][f'{ETS_s}C_{gp}G']=\
                    scenarios[ETS_s][gp][year]['Price'].copy()


dif_price=pd.DataFrame(0,index=years,columns=l)
for ETS_s in scenarios.keys():
    for gp in scenarios[ETS_s].keys():
        for year in scenarios[ETS_s][gp].keys():
            dif_price.loc[year,f'{ETS_s}C_{gp}G']=\
                y_results[year][f'{ETS_s}C_{gp}G'].mean()
        


Dif_abs=pd.DataFrame(0,index=scenarios.keys()
                ,columns=scenarios[ETS_s].keys())

for ETS_s in Dif_abs.index:
    for gp in Dif_abs.columns:
        Dif_abs.loc[ETS_s,gp]=dif_price[f'{ETS_s}C_{gp}G'].max()\
            -dif_price[f'{ETS_s}C_{gp}G'].min()


fig, ax = plt.subplots(figsize=(10,10))
sns.heatmap(Dif_abs, linewidth=0.5,#mask=CM> 50,
                 cbar_kws={'label': 'Average Electricity Price Deviation'},
                 cmap='RdYlGn_r', square=True, annot=True,
                 cbar=True,fmt=".1f",ax=ax,
                 )
ax.set_ylabel('CO2 Allowance [Eur/tCO2]')
ax.set_xlabel('Gas Price [Eur/MWh]')
plt.savefig(f'Figures/{m} - {sc} - prices difference years.png',
            dpi=300,bbox_inches='tight')



#%% Market Value

"""
The capture price/market value is defined as the volume weighted average 
spot market price for a renewable technology, reliant on the
total production of that technology and baseload 
power prices in a given period.
Capture price can be aggregated based on frequency (Hourly, Daily, Weekly, Monthly, Yearly)
"""
freq='Y'
for year in years:    
    for tech in ['Photovoltaics','Wind onshore']:    
        times=pd.date_range(start=f'{year}-01-01',
                            end=f'{year}-12-31 23:00:00',
                            freq='H')


        Spot_ts=pd.DataFrame(0,index=times,columns=l) #Hourly Spot Prices
        
        Energy=pd.DataFrame(0,index=times,columns=l) # Hourly energy of tech
        
        for ETS_s in scenarios.keys():
            for gp in scenarios[ETS_s].keys():
                # for year in years:
        
                Spot_ts[f'{ETS_s}C_{gp}G'] = \
                    scenarios[ETS_s][gp][year]['Price'] 
        
                Energy[f'{ETS_s}C_{gp}G'] =\
                    p_scenario[ETS_s][gp][year][tech].copy()
        
        
        Revenue= (Energy*Spot_ts).groupby(pd.Grouper(freq=freq)).sum()
        Total_energy=Energy.groupby(pd.Grouper(freq=freq)).sum()
        
        market_value=(Revenue/Total_energy).mean()
        
        
        spot_avg=pd.DataFrame(0,index=scenarios.keys()
                        ,columns=gas) # Average Spot Prices
        spot_avg_rate=pd.DataFrame(0,index=scenarios.keys()
                        ,columns=gas) # Average Spot Prices for capture rate
        MV=pd.DataFrame(0,index=scenarios.keys()
                        ,columns=gas) # Market value for heatplot
        
        for ETS_s in scenarios.keys():
            for gp in scenarios[ETS_s].keys():
                MV.loc[ETS_s,gp]=market_value[f'{ETS_s}C_{gp}G']
                spot_avg.loc[ETS_s,gp]=Spot_ts[f'{ETS_s}C_{gp}G'].mean()
                spot_avg_rate.loc[ETS_s,gp]=Spot_ts[f'{ETS_s}C_{gp}G']\
                    [Energy[f'{ETS_s}C_{gp}G']!=0].mean()


        
        
                
        
        
        
        fig, ax = plt.subplots(figsize=(10,10))
        sns.heatmap(MV, linewidth=0.5,#mask=CM> 50,
                          cbar_kws={'label': f"Average {tech} "
                                    f"Market Value [Eur/MWh]"},
                          cmap='RdYlGn', square=True, annot=True,
                          cbar=True,fmt=".1f",ax=ax,
                          center=75)
        ax.set_ylabel('CO2 Allowance [Eur/tCO2]')
        ax.set_xlabel('Gas Price [Eur/MWh]')
        plt.savefig(f'Figures/{m} - {sc} -{tech} - Market Value - {year}.png',
                    dpi=300,bbox_inches='tight')




        
        



#%% Area plot: Dispatch
# year=2021
# times=pd.date_range(start=f'{year}-01-01',
#                     end=f'{year}-12-31 23:00:00',
#                     freq='H')

# ETS_s=100
# gp=60
# start=f'{year}-07-10'
# end=f'{year}-07-12'
# p_scenario[ETS_s][gp][year]
# p_scenario[ETS_s][gp][year].groupby(times.month).sum()['Photovoltaics']



# temp=scenarios[ETS_s][gp][year].loc[start:end,'Price'].copy()


# temp_p=p_scenario[ETS_s][gp][year].loc[start:end].copy()/1e3

# temp_p.drop(['PHS','large-batteries','small-batteries'],
#             axis=1,inplace=True)


# temp_p.drop((temp_p.max()[temp_p.max() < 1.]).index,axis=1,inplace=True)

# pu=pd.read_excel('Data/Weather_profiles.xlsx',
#                    index_col=0,parse_dates=True,
#                    sheet_name=str(year))
# Installed_capacities=pd.read_excel('Data/scenario_capacities.xlsx',
#                                    index_col=0,sheet_name=sc)

# curtailed=pu.loc[start:end]*Installed_capacities.loc[2019,pu.columns]

# curtailed-=temp_p[curtailed.columns]

# curtailed[(curtailed<0.01)&(curtailed>-0.01)]=0

# curtailed[curtailed>0]

# ax=temp_p.plot(kind='area',lw=0,
#             color=[colors[col] for col in temp_p.columns])
# curtailed.plot(ax=ax,lw=0,
#                kind='area',
#                color=[colors[col] for col in curtailed.columns])
# plt.legend("")
# ax.set_ylim(-50,180)
# ax2=ax.twinx()
# temp.plot(ax=ax2,lw=2,color='magenta')




