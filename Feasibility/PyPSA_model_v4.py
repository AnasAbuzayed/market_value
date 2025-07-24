# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 03:15:02 2025

@author: Anas
"""
import pypsa
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

print('Please enter scenario: A,B,C')
sc=input()

print('Please enter method: cap or gas\ngas increases NG capacities to satisfy the high demand periods\ncap imposes a price cap of 1000 Eur/MWh to take care of the high demand periods when generation stack is not enough')
method=input()


createFolder(f'Results/{sc}')

solver_options={ 'threads': 64}

real_price_original=pd.read_excel('Data/Price.xlsx',parse_dates=True,index_col=0)
real_price_original.columns=['Price']
impexp_original=pd.read_excel('Data/imports_exports_scheduled.xlsx',index_col=0,parse_dates=True)

costs=pd.read_excel('Data/model costs.xlsx',index_col=0)

Installed_capacities=pd.read_excel('Data/scenario_capacities.xlsx',
                                   index_col=0,sheet_name=sc)


years=list(range(2019,2025)) #2025
scenarios={}
energy={}
ETS=list(range(25,301,25))
gas=list(range(10,61,10))
for EU_ETS in ETS:
    print(EU_ETS)
    scenarios[EU_ETS]={}
    energy[EU_ETS]={}
    for gp in gas:
        print(gp)
        scenarios[EU_ETS][gp]={}
        energy[EU_ETS][gp]={}
        writer = pd.ExcelWriter(f'Results/{sc}_{method}/Merit_{EU_ETS}C_{gp}G.xlsx')
        writer_e = pd.ExcelWriter(f'Results/{sc}_{method}/Energy_{EU_ETS}C_{gp}G.xlsx')

        for year in years:
            year=str(year)
            print(year)
            
            load=pd.read_excel('Data/Load.xlsx',
                               index_col=0,parse_dates=True,
                               sheet_name=year)
            PHS=pd.read_excel('Data/PHS_Load.xlsx',
                               index_col=0,parse_dates=True,
                               sheet_name=year)
            cap1=pd.read_excel('Data/Actual gen.xlsx',
                               index_col=0,parse_dates=True,
                               sheet_name=year)
            cap2=pd.read_excel('Data/Weather_profiles.xlsx',
                               index_col=0,parse_dates=True,
                               sheet_name=year)
            pu=pd.read_excel('Data/Weather_profiles.xlsx',
                               index_col=0,parse_dates=True,
                               sheet_name=year)
            impexp=impexp_original.loc[year]

            cap2*=(Installed_capacities.\
                   loc[2019,cap2.columns]*1e3) #adapt profile to capacity
            
            
            
            
            times=pd.date_range(start=f'{year}-01-01',
                                end=f'{year}-12-31 23:00:00',
                                freq='H')
            
            
            PHS.index=impexp.index=\
                load.index=cap2.index\
                    =times
            
            
            # load represents total consumption but includes PHS and Import/Export.
            ## correct for PHS load, imports & exports
            # by adding PHS, we correct the load and add electricity used to pump water
            load=load.add(PHS['Hydro pumped storage consumption'],axis=0)
            
            #by definition, trade is part of forecasted load from SMARD
            # negative values ==> import, positive ==> export
            # keep the line below to exclude trade (import/export)
            # comment to include trade (import/export)
            # load=load.add(impexp['Net export [MWh]'],axis=0)


            load*=((Installed_capacities.loc[2019,'load']/
                    (load.sum()/1e6)).sum()) # Based on Netzentwicklungsplan scenario
            
            
            
            
            
            
            
            
            #adapt plant capacities to year 
            data=pd.read_csv('Data/corrected_power_plants.csv',index_col=0)
            data['max_hours']=0
            data.loc['PHS','max_hours']=8
            data.loc['PHS','efficiency']=0.87


            data.loc['small-batteries']=data.loc['PHS']
            data.loc['small-batteries','carrier2']='small-batteries'
            data.loc['small-batteries','efficiency']=0.9
            data.loc['small-batteries','max_hours']=2.5
            # data.loc['small-batteries','availability']=1
            
            data.loc['large-batteries']=data.loc['PHS']
            data.loc['large-batteries','carrier2']='large-batteries'
            data.loc['large-batteries','efficiency']=0.9
            data.loc['large-batteries','max_hours']=2

            cond=np.where(data.carrier2\
                          .isin(Installed_capacities.columns))
            data=data.iloc[cond]
            

            
            for col in Installed_capacities.columns: #Scenario: Correct Capacities
                # print(col)
                if col=='Natural gas':
                    idxs=data.loc[(data.carrier2=='Natural gas')
                                  &
                                  (data.status=='operating')
                                  &
                                  (data.efficiency<=0.47)].index
                    s=data.loc[idxs,'capacity'].sum()
                    s1=Installed_capacities.loc[2019,'OCGT'].max()*1e3
                    f=s1/s
                    data.loc[idxs,'capacity']*=f
                    idxs=data.loc[(data.carrier2=='Natural gas')
                                  &
                                  (data.status=='operating')
                                  &
                                  (data.efficiency>0.47)].index
                    s=data.loc[idxs,'capacity'].sum()
                    s1=Installed_capacities.loc[2019,'CCGT'].max()*1e3
                    f=s1/s
                    data.loc[idxs,'capacity']*=f
                else:
                    s=data.loc[(data.carrier2==col)
                               &
                               (data.status=='operating')
                               ,'capacity'].sum()
                    s1=Installed_capacities.loc[2019,col].max()*1e3
                    f=s1/s
                    data.loc[(data.carrier2==col)
                               &
                               (data.status=='operating')
                               ,'capacity']*=f
            
            data.capacity[data.status=='operating']*=data.availability
            data.mustrun[data.status=='operating']*=data.capacity

            
            costs.loc['Natural gas','fuel']=gp
            
            for fuel in costs.index:
                data.loc[data.carrier2==\
                         fuel,'fuel']=costs.loc[fuel,'fuel']
            data['fuel']/=data['efficiency']
            
            
            data['CO2 Allowance'] = data['emission_factor'] * \
                EU_ETS \
                    / data['efficiency']
            
            data['Marginal Cost'] = data['CO2 Allowance'] \
                + data['fuel'] + data['VOM']

            data.loc[data.efficiency==1,'Marginal Cost'] = 0 ## RES to zero

            if method != 'cap':
            #to make NG big enough to satisfy the demand or VOLL takes care of the high demand periods            
                data.loc[data.carrier2=='Natural gas','capacity']*=2

            price_temp=real_price_original.loc[year]
            select=price_temp[price_temp<0]\
                .groupby(price_temp.index.hour).mean()
            select.replace(np.nan,0,inplace=True)
            select.columns=['Price']
                        
            marginal_costs=pd.DataFrame(0,
                                        index=times,
                                        columns=data.index)
            marginal_costs[marginal_costs.columns]=data['Marginal Cost']
            
            for hour in times:
                
                res=cap2.loc[hour].sum()
                demand=load.Load.loc[hour]
                mustrun=data.mustrun.sum()
                storage=data.loc[
                    ['PHS','small-batteries','large-batteries'],
                    ['capacity','efficiency']]
                storage.efficiency=storage.efficiency.pow(2)
                storage=storage.prod(axis=1).sum()

                if res >= demand-mustrun + storage:
                    cols=data.loc[data.mustrun!=0].index
                    marginal_costs.loc[hour,cols] =\
                        marginal_costs.loc[hour,pu.columns]=\
                            select.loc[hour.hour,'Price']
            for col in pu.columns:
                x=0.0001 if col=='Wind offshore' else 0.001 if col=='Wind onshore' else 0.01
                marginal_costs[col]-=x


            pu['Hydro']=cap1['Hydro']/(cap1['Hydro'].max())


            n=pypsa.Network()
            n.set_snapshots(times)
            n.add('Bus','DE0 0')
            n.add('Load','DE0 0',
                  bus='DE0 0',p_set=load['Load'])
            
            for idx in data.index:
                if data.loc[idx,'max_hours']!=0:                    
                    n.add('StorageUnit',f'DE0 {idx}',bus='DE0 0',
                          p_nom=data.loc[idx,'capacity'],
                          max_hours=data.loc[idx,'max_hours'],
                          carrier=idx,
                          marginal_cost=0.01,
                          efficiency_dispatch=data.loc[idx,'efficiency'],
                          efficiency_store=data.loc[idx,'efficiency'],
                          state_of_charge_set=np.ones((len(times)))*np.nan)
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

            n.pnl('StorageUnit')['state_of_charge_set'].loc[times[-1]]=0
            
            n.lopf(solver_name='gurobi',
                   solver_options=solver_options,
                   solver_dir= '/home/local/tmp_pypsa')
            # n.export_to_netcdf(f'Results/{sc}_{method}/Net_{EU_ETS}C_{gp}G_{year}.nc')
            
            merit=pd.DataFrame(0,times, ['Price','Tech','Demand'])
            bus='DE0 0'
            for hour in times:
                g=(n.generators_t.p[n.generators.index[n.generators.bus==bus]].loc[hour] > 0.01)
                merit.loc[hour,'Price'] = n.generators_t.marginal_cost.loc[hour,g[g==True].index].max()
                    
                try:
                    idx=n.generators_t.marginal_cost.loc[hour,g[g==True].index].idxmax()
                    merit.loc[hour,'Tech'] = n.generators.loc[idx,'carrier']
                except:
                    merit.loc[hour,'Tech'] ='Storage'
                    merit.loc[hour,'Price'] = 0


                if merit.loc[hour,'Price'] <0:
                    L1=list(n.generators_t.marginal_cost.loc[hour,g[g==True].index].index)
                    L2=[i for i in n.generators_t.p_max_pu.columns if i in L1]
                    if L2:
                        gen=n.generators_t.marginal_cost.loc[hour,L2].idxmin()
                        merit.loc[hour,'Tech']=n.generators.loc[gen,'carrier']
                merit.loc[hour,'Demand'] = n.loads_t.p.loc[hour,'DE0 0'] - n.storage_units_t.p.loc[hour].sum()
                if merit.loc[hour,'Tech'] =='Storage':
                    merit.loc[hour,'Demand'] = n.storage_units_t.p.loc[hour].sum()

            scenarios[EU_ETS][gp][year]=merit.copy()
            p_by_carrier=n.generators_t.p.groupby(n.generators.carrier,axis=1).sum()
            s_by_carrier=n.storage_units_t.p.groupby(n.storage_units.carrier,axis=1).sum()
            
            energy[EU_ETS][gp][year]=pd.concat([p_by_carrier,s_by_carrier],axis=1)

        for (name, df),(name1,df1) in zip(scenarios[EU_ETS][gp].items(),
                            energy[EU_ETS][gp].items()):
            df.to_excel(writer, sheet_name=str(name))
            df1.replace(np.nan,0).to_excel(writer_e, sheet_name=str(name))
        writer.close()
        writer_e.close()

