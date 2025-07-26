from numpy import linspace, array, minimum
from pandas import DataFrame, to_datetime
from restclient import RestClient
from veplots import plotcanvas
from energinetdata import CapacitiesVE as CapVE
from energinetdata import ConsumptionProductionVE as CoprVE

print('Getting dataset')
coprve = CoprVE(start='2022-01-01T01:00', end='2023-01-01T01:00')
print('Converting to dataframe')
dfcons = coprve.getAsDataFrame() #.unstack()
print('Dataset retrieved. Data:')
#print(dfcons.columns
print(dfcons)
print('')
print('Data as sums:')
print(dfcons.sum())

dict_scale_args = dict(
    newcap_offshore= 8000,  # Global capacity addition in 2024. https://www.gwec.net/gwec-news/wind-industry-installs-record-capacity-in-2024-despite-policy-instability
    newcap_onshore = 109000,   # see above
    newcap_solar   = 597000,  # Global capacity addition in 2024. https://www.solarpowereurope.org/insights/outlooks/global-market-outlook-for-solar-power-2025-2029/detail
    #    mult_offshore=3.5,
    #    mult_onshore=3.5,
    #    mult_solar=3.5,
    )

batt_energy_capacity = 160 # GWh battery added globally in in 2024.
batt_discharge_power_capacity = 60 # GW battery added globally in in 2024, from memory, can be wrong
batt_charge_power_capacity = 30 # GW. Wild assumption.
batt_discharge_eff = 0.9
batt_charge_eff = 0.9
batt_start_soc = 0.5

const_power_output = 7.0 # GW. The power we want to deliver constantly as if we were a power plant.



dfscaled = coprve. get_with_rescaled_cap(**dict_scale_args)
print('')
print('Data scaled, sums:')
print(dfscaled.sum())

# Loop through scenarios for different desired power output
for const_power_output in [10,17, 18.46, 18.47, 27.6, 27.65, 37.36, 37.37, 46.81, 46.82, 50 ]:
    # Simulate battery operation. 
    # Cannot be vectorized easily, because each hour will depend on the previous hour.
    # So we loop through the dataset.
    dfbattery = DataFrame(index = dfscaled.index, columns = ['Stored at start, GWh', 'VE, GW', 'Charged, GW', 'Output VE+batt, GW', 'Output excess, GWh', 'Output deficit, GWh', 'Stored at end, GWh'])
    stored_at_end = batt_start_soc * batt_energy_capacity
    for ts, row in dfscaled.iterrows():
        ve_now = row['vetotal']/1000
        batt_out_needed = const_power_output - ve_now
        dfbattery.loc[ts, 'Stored at start, GWh'] = stored_at_end
        if batt_out_needed >= 0:
            batt_out_energy_avail = stored_at_end * batt_discharge_eff
            batt_out_effect_delivered = min(batt_discharge_power_capacity, batt_out_energy_avail, batt_out_needed)
            stored_at_end -= batt_out_effect_delivered / batt_discharge_eff
        elif batt_out_needed < 0:
            batt_out_energy_avail = (stored_at_end-batt_energy_capacity) / batt_charge_eff # Negative
            batt_out_effect_delivered = max(-batt_charge_power_capacity, 
            batt_out_energy_avail, batt_out_needed)
            stored_at_end -= batt_out_effect_delivered * batt_charge_eff 

        ve_and_batt_out = ve_now + batt_out_effect_delivered
        deficit = min(0, batt_out_effect_delivered - batt_out_needed)
        excess = max(0, ve_and_batt_out - const_power_output)

        dfbattery.loc[ts, 'VE, GW'] = ve_now
        dfbattery.loc[ts, 'Charged, GW'] = -batt_out_effect_delivered
        dfbattery.loc[ts, 'Output VE+batt, GW'] = ve_and_batt_out
        dfbattery.loc[ts, 'Output excess, GWh'] = excess
        dfbattery.loc[ts, 'Output deficit, GWh'] = deficit
        dfbattery.loc[ts, 'Stored at end, GWh'] = stored_at_end
    #print(dfbattery)
    #print()
    #print(dfbattery.sum())
    #print(dfbattery.mean())
    total_hours = len(dfbattery.index)
    desired_total_output_energy = total_hours * const_power_output
    min_accomplished_ve_and_batt_out = dfbattery['Output VE+batt, GW'].min()
    print()
    print(f"Ønsket konstant ydelse: {const_power_output:12.2f} GW")
    print(f"Analyseret antal timer: {total_hours:12}")
    print(f"Ønsket total ydelse:    {desired_total_output_energy:12.2f} GWh")
    cond_fulfilled = dfbattery['Output deficit, GWh'] == 0
    df_fulfilled_hours = dfbattery[cond_fulfilled]  
    df_nonfulfilled_hours = dfbattery[~cond_fulfilled]
    hours_fulfilled = len(df_fulfilled_hours.index)  
    hours_nonfulfilled = len(df_nonfulfilled_hours.index)  
    output_deficit = dfbattery['Output deficit, GWh'].sum()
    output_excess = dfbattery['Output excess, GWh'].sum()
    battery_stored_change = dfbattery['Stored at end, GWh'].iloc[-1] - dfbattery['Stored at start, GWh'].iloc[0]
    battery_deficit = min(0, battery_stored_change)
    battery_excess = max(0, battery_stored_change)
    total_deficit = output_deficit + battery_deficit
    total_excess = output_excess + battery_excess
    print(f"Ydelse opnået i         {hours_fulfilled:12} timer")
    print(f"Ydelse ikke opnået i    {hours_nonfulfilled:12} timer")
    print(f"Manglende ydelse total: {total_deficit:12.2f} GWh")
    print(f"Resulterende rådighed:  {100. + 100. * total_deficit / desired_total_output_energy:12.2f} %")
    print(f"Ekstra ydelse total:    {total_excess:12.2f} GWh")



