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
import numpy as np
import os 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
createFolder('Output')

gas_corrected=pd.read_csv('Data/TTF_corrected.csv',index_col=0,
                          parse_dates=True)
oil_corrected=pd.read_csv('Data/oil_corrected.csv',index_col=0,
                          parse_dates=True)
coal_corrected=pd.read_csv('Data/coal_corrected.csv',index_col=0,
                          parse_dates=True)

load_original=pd.read_excel('Data/Load.xlsx',index_col=0,parse_dates=True)
impexp_original=pd.read_excel('Data/imports_exports_scheduled.xlsx',index_col=0,parse_dates=True)
PHS_original=pd.read_excel('Data/PHS_Load.xlsx',index_col=0,parse_dates=True)


EU_ETS_original=pd.read_excel('Data/ETS_DE.xlsx',parse_dates=True,index_col=0)

real_price_original=pd.read_excel('Data/Price.xlsx',parse_dates=True,index_col=0)


cap1=pd.read_excel('Data/Actual gen.xlsx',index_col=0,parse_dates=True)
cap2=pd.read_excel('Data/Forecasted gen.xlsx',index_col=0,parse_dates=True)

forecasted_cap_original=pd.concat([cap1,cap2],axis=1)

Actual_all_original=pd.read_excel('Data/Actual_generation_All.xlsx',index_col=0,parse_dates=True)
installed_capacity=pd.read_excel('Data/Installed_capacities.xlsx',index_col=0)

for year in range(2019,2025):
    year=str(year)
    print(year)

    
    

    
    times=pd.date_range(start=f'{year}-01-01',
                        end=f'{year}-12-31 23:00:00',
                        freq='H')
    
    ## Select year only
    load=load_original.loc[year]
    PHS=PHS_original.loc[year]
    EU_ETS=EU_ETS_original.loc[year]
    real_price=real_price_original.loc[year]
    Actual_all=Actual_all_original.loc[year]
    impexp=impexp_original.loc[year]
    forecasted_cap=forecasted_cap_original.loc[year]
    pu=pd.read_excel('Data/Weather_profiles.xlsx',
                       index_col=0,parse_dates=True,
                       sheet_name=year)
    
    cap_year=cap2.loc[year]
    
    pu=cap_year/cap_year.max()
    # pu=cap_year/installed_capacity.loc[int(year),cap_year.columns]

    impexp.index= PHS.index=forecasted_cap.index=\
        EU_ETS.index=load.index=real_price.index\
            =cap_year.index=pu.index=Actual_all.index=\
                times
    
    # load represents total consumption but includes PHS and Import/Export.
    ## correct for PHS load, imports & exports
    # by adding PHS, we correct the load and add electricity used to pump water
    load=load.add(PHS['Hydro pumped storage consumption']*-1,axis=0)
    
    #by definition, trade is part of forecasted load from SMARD
    # negative values ==> import, positive ==> export
    # keep the line below to exclude trade (import/export)
    # comment to include trade (import/export)
    # load=load.add(impexp['Net export [MWh]'],axis=0)
    
    
    #adapt plant capacities to year 
    data=pd.read_csv('Data/corrected_power_plants.csv',index_col=0)

    for col in Actual_all.columns:
        # if year =='2024' ==> todo in 2024 for nuclear
        s=data.loc[(data.carrier2==col)&
                   (data.status!='reserve'),'capacity'].sum()
        # if col in pu.columns:            
        s1=Actual_all[col].max()
        # else:
        #     s1=installed_capacity.loc[int(year),col]
        f=s1/s
        data.loc[(data.carrier2==col)&
                   (data.status!='reserve'),'capacity']*=f
    data.loc['PHS','capacity']=installed_capacity.loc[int(year),'PHS']
    data.capacity*=data.availability
    data.mustrun*=data.capacity
    
    cont=['Hard coal','Natural gas','Oil']
    gas=gas_corrected.reindex(times).ffill()
    oil=oil_corrected.reindex(times).ffill()
    coal=coal_corrected.reindex(times).ffill()
    
    cont=pd.DataFrame(0,index=times,columns=cont)
    cont['Hard coal']=coal
    cont['Natural gas']=gas
    cont['Oil']=oil
    cont['ETS']=EU_ETS
    
    
    price_temp=real_price_original.loc[year]
    select=price_temp[price_temp<0]\
        .groupby(price_temp.index.hour).mean()
    select.replace(np.nan,0,inplace=True)
    select.columns=['Price']
    
    marginal_costs=pd.DataFrame(0,index=times,columns=data.index)
    for pp in marginal_costs.columns:
        carrier=data.loc[pp,'carrier2']
        vom=data.loc[pp,'VOM']
        emissions=data.loc[pp,'emission_factor']
        eff=data.loc[pp,'efficiency']
        fuel=data.loc[pp,'fuel']
    
        if data.loc[pp,'carrier2'] in cont.columns:
            marginal_costs[pp] = vom+ cont[carrier].values/eff\
                + (cont['ETS']*emissions/eff)
        else:
            marginal_costs[pp] = vom + \
                (cont['ETS']*emissions/eff) +\
                    (fuel/eff)
    

    
    for hour in times:
        res=(pu.loc[hour]*data.loc[pu.columns,'capacity']).sum()
        demand=load.Load.loc[hour]
        mustrun=data.mustrun.sum()
        # storage=data.loc['PHS','capacity']
        if res >= demand-mustrun:
            cols=data.loc[data.mustrun!=0].index
            marginal_costs.loc[hour,cols] =\
                marginal_costs.loc[hour,pu.columns]=\
                    select.loc[hour.hour,'Price']
    
    for col in pu.columns:
        x=0.0001 if col=='Wind offshore' else 0.001 if col=='Wind onshore' else 0.01
        marginal_costs[col]-=x
    





    
    pu['Hydro']=forecasted_cap['Hydro']/(forecasted_cap['Hydro'].max())
    
    
    
    
    
    n=pypsa.Network()
    n.set_snapshots(times)
    n.add('Bus','DE0 0')
    n.add('Load','DE0 0',
          bus='DE0 0',p_set=load['Load'])
    
    for idx in data.index:
        if idx=='PHS':
            # continue
            n.add('StorageUnit',f'DE0 {idx}',bus='DE0 0',
                  p_nom=data.loc[idx,'capacity'],
                  max_hours=8,carrier=idx,
                  efficiency_dispatch=0.87,
                  efficiency_store=0.87)
        else:
            if data.loc[idx,'carrier2'] in pu.columns:
                p_max_pu=pu[data.loc[idx,'carrier2']].values
            else:
                p_max_pu=1.
            mc=marginal_costs[idx].values
            n.add('Generator',f'DE0 {idx}',bus='DE0 0',
                  p_nom=data.loc[idx,'capacity'],
                  carrier=data.loc[idx,'carrier2'],
                  marginal_cost=mc,
                  p_max_pu=p_max_pu)

    n.add("Generator", bus="DE0 0",
          name='DE0 VOLL',
          carrier='VOLL', 
          marginal_cost=pd.Series(1e3,index=times),
          p_nom=1e6
          )


    n.lopf(solver_name='gurobi')
    n.export_to_netcdf(f'Output/{year}.nc')
    merit=pd.DataFrame(0,times, ['Price'])
    bus='DE0 0'
    for hour in times:
        g=(n.generators_t.p[n.generators.index[n.generators.bus==bus]].loc[hour] > 0.1)
        merit.loc[hour,'Price'] = n.generators_t.marginal_cost.loc[hour,g[g==True].index].max()

    writer = pd.ExcelWriter(f'Output/{year}.xlsx')
    for i, (name, df) in enumerate(merit.items()):
        df.to_excel(writer, sheet_name=str(i))
    writer.close()




