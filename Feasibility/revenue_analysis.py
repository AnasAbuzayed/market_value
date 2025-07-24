# -*- coding: utf-8 -*-
"""
@author: Anas Abuzayed © 2025
https://github.com/AnasAbuzayed/market_value

Description:
This repository provides the code and supporting materials for the research article:

From Model Optimality to Market Reality: Do Electricity Markets Support Renewable Investments?

The study investigates the gap between model-based optimal dispatch and actual market outcomes in electricity markets, and evaluates how effectively price signals incentivize renewable expansion. 

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
sc=sc.capitalize()
m='gas'
year=2021
ETS=[25,300]
gas=[10,60]

scenarios={}
p_scenario={}
for ETS_s in ETS:
    scenarios[ETS_s]={}
    p_scenario[ETS_s]={}
    for gp in gas:
        print(f'Scenario {sc}_{m} : {ETS_s}C_{gp}G_{year}')
        scenarios[ETS_s][gp]=pd.read_excel\
            (f'Results/{sc}_{m}/Merit_{ETS_s}C_{gp}G.xlsx',
              index_col=0,parse_dates=True,
              sheet_name=str(year))
        p_scenario[ETS_s][gp]=pd.read_excel\
            (f'Results/{sc}_{m}/Energy_{ETS_s}C_{gp}G.xlsx',
              index_col=0,parse_dates=True,
              sheet_name=str(year))


#%%
tech1='Photovoltaics'
tech2='Wind onshore'
times=pd.date_range(start=f'{year}-01-01',
                    end=f'{year}-12-31 23:00:00',
                    freq='H')


l=[]
for ETS_s in scenarios.keys():
    for gp in scenarios[ETS_s].keys():
        l.append(f'{ETS_s}C_{gp}G')


Spot_ts=pd.DataFrame(0,index=times,columns=l) #Hourly Spot Prices

Energy_solar=pd.DataFrame(0,index=times,columns=l) # Hourly energy of tech
Energy_wind=pd.DataFrame(0,index=times,columns=l) # Hourly energy of tech

for ETS_s in scenarios.keys():
    for gp in scenarios[ETS_s].keys():
        # for year in years:

        Spot_ts[f'{ETS_s}C_{gp}G'] = \
            scenarios[ETS_s][gp]['Price'] 

        Energy_solar[f'{ETS_s}C_{gp}G'] =\
            p_scenario[ETS_s][gp][tech1].copy()

        Energy_wind[f'{ETS_s}C_{gp}G'] =\
            p_scenario[ETS_s][gp][tech2].copy()


case='300C_60G'
case='25C_10G'

# hours where solar is generating 
(Energy_solar[case]>0).sum()

# hours where solar generated and negative price
(Spot_ts[case][Energy_solar[case]!=0]<-0.01).sum()

# hours where solar generated and low price
# P.S. Onwind VOM is 2.7
(Spot_ts[case][Energy_solar[case]!=0]<=3).sum()\
    -(Spot_ts[case][Energy_solar[case]!=0]<-0.1).sum()

# hours where solar generated and not low price, e.g., biomass or NG cleared
(Spot_ts[case][Energy_solar[case]!=0]>3).sum()

# hours where solar generated and not low price, e.g., biomass or NG cleared
Spot_ts.loc[Energy_solar[case]!=0,[case]].loc[Spot_ts[case]>3].max()
Spot_ts.loc[Energy_solar[case]!=0,[case]].loc[Spot_ts[case]>3].mean()




Spot_ts['25C_10G'][Energy_solar['25C_10G']!=0]>3




# hours where solar generated and negative price
(Spot_ts['25C_10G'][Energy_solar['25C_10G']!=0]<-0.01).sum()


(Spot_ts['25C_10G'][Energy_wind['25C_10G']!=0]<-0.01).sum()
# hours where wind generated and negative price

(Spot_ts['25C_10G'][(Energy_solar['25C_10G']!=0)&
                    (Energy_solar['25C_10G']==0)]<-0.01).sum()
# hours where solar generated, wind didn't and negative price


(Spot_ts['25C_10G']<-.01).sum()
#all negative hours

low_commodity_price=Spot_ts['25C_10G'].copy()

price_distribution=pd.DataFrame(0,index=range(0,24,1),
                                columns=['Negative','Zero'])


price_distribution['Negative']=low_commodity_price[low_commodity_price<-.1].groupby(
    low_commodity_price[low_commodity_price<-.1].index.hour).count()

price_distribution['Zero']=low_commodity_price[(low_commodity_price>-.1)
                                            &
                                            (low_commodity_price<=0.01)].groupby(
                                                low_commodity_price[(low_commodity_price>-.1)
                                                                    &
                                                                    (low_commodity_price<=0.01)]\
                                                    .index.hour).count()

price_distribution.replace(np.nan,0,inplace=True)

price_distribution=price_distribution.add_suffix(' Clearing Price')



solar_generation_profile=pd.DataFrame(
    (Energy_solar['25C_10G'].groupby(times.hour).mean()\
     /Energy_solar['25C_10G'].max()))
solar_generation_profile.columns=['Photovoltaics generation profile']


solar_low_profile=pd.DataFrame(
    ((Energy_solar*Spot_ts)/(Energy_solar*Spot_ts).max())['25C_10G'])
solar_high_profile=pd.DataFrame(
    ((Energy_solar*Spot_ts)/(Energy_solar*Spot_ts).max())['300C_60G'])

solar_low_profile.columns=['Low - Revenue']
solar_high_profile.columns=['High - Revenue']




wind_generation_profile=pd.DataFrame(
    (Energy_wind['25C_10G'].groupby(times.hour).mean()\
     /Energy_wind['25C_10G'].max()))
wind_generation_profile.columns=['Onshore wind generation profile']


wind_low_profile=pd.DataFrame(
    ((Energy_wind*Spot_ts)/(Energy_wind*Spot_ts).max())['25C_10G'])
wind_high_profile=pd.DataFrame(
    ((Energy_wind*Spot_ts)/(Energy_wind*Spot_ts).max())['300C_60G'])

wind_low_profile.columns=['Low - Revenue']
wind_high_profile.columns=['High - Revenue']








high_revenue_monthly=pd.concat([(Energy_solar*Spot_ts)['300C_60G'].groupby(times.month).sum(),
                           (Energy_wind*Spot_ts)['300C_60G'].groupby(times.month).sum()],
                          axis=1)/1e6
high_revenue_monthly.columns=['High - Solar','High - Wind']

low_revenue_monthly=pd.concat([(Energy_solar*Spot_ts)['25C_10G'].groupby(times.month).sum(),
                           (Energy_wind*Spot_ts)['25C_10G'].groupby(times.month).sum()],
                          axis=1)/1e6
low_revenue_monthly.columns=['Low - Solar','Low - Wind']

revenue_all=pd.concat([high_revenue_monthly,
                       low_revenue_monthly],axis=1)
revenue_all=revenue_all[['High - Solar','Low - Solar',
             'High - Wind','Low - Wind']]



Spot_profile_low=pd.DataFrame({'Wholesale Price: Low':
                               Spot_ts['25C_10G'].groupby(times.hour).mean()/Spot_ts['25C_10G'].max()})
Spot_profile_high=pd.DataFrame({'Wholesale Price: High':
                               Spot_ts['300C_60G'].groupby(times.hour).mean()/Spot_ts['300C_60G'].max()})

    
    
    
    
    
# ## Idea 1
# fig, ax = plt.subplots(2,2,figsize=(18,8))
# #Subplot 1
# solar_generation_profile.\
#     plot(ax=ax[0,0])
# wind_generation_profile.\
#     plot(ax=ax[0,0])
# Spot_profile_low.\
#     plot(ax=ax[0,0])
# Spot_profile_high.\
#     plot(ax=ax[0,0])
# ax[0,0].set_xticks(list(range(0,24,1)))
# ax[0,0].set_ylabel('Normalized profiles')
# ax[0,0].set_xlabel('Hour of the day')
# ax[0,0].legend(fontsize=9)
# ax[0,0].grid(which='major', axis='both',
#          linestyle='-', linewidth='0.5', color='gray')
# #Subplot 2
# price_distribution.plot(kind='bar',ax=ax[0,1])
# ax[0,1].set_ylabel('Frequency')
# ax[0,1].set_xlabel('Hour of the day')
# ax[0,1].set_xticks(list(range(0,24,1)))
# ax[0,1].grid(which='major', axis='both',
#          linestyle='-', linewidth='0.5', color='gray')
# #Subplot 3
# low_revenue_monthly.plot(kind='bar',ax=ax[1,0])
# ax[1,0].set_ylabel('Revenue in Million Euro')
# ax[1,0].set_xlabel('Month of the year')
# ax[1,0].grid(which='major', axis='both',
#          linestyle='-', linewidth='0.5', color='gray')
# #Subplot 4
# high_revenue_monthly.plot(kind='bar',ax=ax[1,1])
# ax[1,1].set_ylabel('Revenue in Million Euro')
# ax[1,1].set_xlabel('Month of the year')
# ax[1,1].grid(which='major', axis='both',
#          linestyle='-', linewidth='0.5', color='gray')












## Another idea





fig, ax = plt.subplots(2,2,figsize=(18,8))
#Subplot 1
solar_low_profile.groupby(times.hour).mean().\
    plot(ax=ax[0,0],lw=2)
solar_high_profile.groupby(times.hour).mean().\
    plot(ax=ax[0,0],lw=2)
solar_generation_profile.\
    plot(ax=ax[0,0],lw=2)
ax[0,0].set_xticks(list(range(0,24,1)))
ax[0,0].set_ylabel('Normalized profiles')
ax[0,0].set_xlabel('Hour of the day\n (a)')
ax[0,0].grid(which='major', axis='both',
         linestyle='-', linewidth='0.5', color='gray')
#Subplot 2
wind_low_profile.groupby(times.hour).mean().\
    plot(ax=ax[0,1],lw=2)
wind_high_profile.groupby(times.hour).mean().\
    plot(ax=ax[0,1],lw=2)
wind_generation_profile.\
    plot(ax=ax[0,1],lw=2)
ax[0,1].set_xticks(list(range(0,24,1)))
ax[0,1].set_ylabel('Normalized profiles')
ax[0,1].set_xlabel('Hour of the day\n (b)')
ax[0,1].grid(which='major', axis='both',
         linestyle='-', linewidth='0.5', color='gray')
#Subplot 3
revenue_all.plot(kind='bar',ax=ax[1,0],alpha=0.8)
ax[1,0].set_ylabel('Revenue in Million Euro')
ax[1,0].set_xlabel('Month of the year\n (c)')
ax[1,0].grid(which='major', axis='both',
         linestyle='-', linewidth='0.5', color='gray')
#Subplot 4
price_distribution.plot(kind='bar',ax=ax[1,1],
                                                 alpha=0.8)
ax[1,1].set_ylabel('Frequency')
ax[1,1].set_xlabel('Hour of the day\n (d)')
ax[1,1].set_xticks(list(range(0,24,1)))
ax[1,1].grid(which='major', axis='both',
         linestyle='-', linewidth='0.5', color='gray')
fig.tight_layout(pad=1)
plt.savefig('Figures/Revenue Analysis.png',
            dpi=300,bbox_inches='tight')

             
