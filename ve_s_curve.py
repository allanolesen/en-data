from numpy import linspace, array, minimum
from pandas import DataFrame, to_datetime
from restclient import RestClient
from veplots import plotcanvas
from energinetdata import CapacitiesVE as CapVE
from energinetdata import ConsumptionProductionVE as CoprVE

import garminconnect


"""
capve = CapVE()
capve.add_missing()
dfcap = capve.getAsDataFrame()
print(dfcap.columns)
print(dfcap)

"""

print(1)
#coprve = CoprVE(start='2022-06-01T02:00', end='2022-06-12T01:00')
coprve = CoprVE(start='2022-01-01T01:00', end='2023-01-01T00:00')
#coprve = CoprVE(start='2022-01-01T01:00', end='2022-08-01T00:00')

#coprve = CoprVE(start='2022-08-01T02:00', end='2023-08-01T10:00')
#coprve = CoprVE(start='2022-06-01T00:00', end='2023-08-29T00:00')
print(2)
dfcons = coprve.getAsDataFrame() #.unstack()
print(3)
#print(dfcons.columns)
print(dfcons)
print(dfcons.sum())


#dfcap = coprve.getcap()
#print(dfcap)

dict_scale_args = dict(
    newcap_offshore= 12900,  # https://kefm.dk/Media/637917337785081736/Faktaark%20havvind.pdf
    newcap_onshore = 8200,   # https://kefm.dk/Media/637917337888630707/Faktaark%20land%20VE.pdf
    newcap_solar   = 20000,  # https://kefm.dk/Media/637917337888630707/Faktaark%20land%20VE.pdf
#    mult_offshore=3.5,
#    mult_onshore=3.5,
#    mult_solar=3.5,
    )



dfscaled = coprve. get_with_rescaled_cap(**dict_scale_args)
print(dfscaled)

pc = plotcanvas(outfilename='test_ve_s_curve.png')
pc.plot_all(dfscaled, titlesuffix='asdf')
pc.output_to_file()

pc = plotcanvas(outfilename='test_ve_s_curve3.png', counth=1)
pc.plot_sorted_prod_excess_to_ax(dfscaled, axnum=0, titlesuffix='asdf')
pc.output_to_file()


dfstreak = coprve. get_streaks(get_stacked=True, **dict_scale_args)

print(dfstreak)

pc = plotcanvas(outfilename='test_ve_gaphours.png', counth=2)
pc.plot_streak_hours_stacked(dfstreak, axnum=0, titlesuffix='asdf')
pc.plot_streak_energy_stacked(dfstreak, axnum=1, titlesuffix='asdf')
pc.output_to_file()


df4 = dfstreak.unstack(fill_value=0).drop(999999, axis=1, level='stacksubID').loc(axis=1)['count'].sum(axis=1)

"""
pc = plotcanvas(outfilename='test_ve_gaphours.png', counth=2)
pc.plot_streak_energy(dfstreak, axnum=0, titlesuffix='asdf')
pc.plot_streak_hours(dfstreak, axnum=1, titlesuffix='asdf')
pc.output_to_file()



# ================================================
# List of gaps
# ================================================

arr_surplus = array(dfscaled['vesurplus'])

list_gaps = []

gap_ongoing = False
acc_total_hours_this_gap = 0
acc_total_energy_this_gap = 0
acc_neg_hours_this_gap = 0
acc_neg_energy_this_gap = 0

for surplus in arr_surplus:
    if (gap_ongoing == False):
        if (surplus >= 0):
            # Nothing to see here. We are on a positive streak.
            continue
        else:
            # This is the first hour in a gap
            gap_ongoing = True

    # If we are here, we are in an ongoing gap
    acc_total_hours_this_gap += 1
    acc_total_energy_this_gap += surplus

    if (surplus < 0):
        acc_neg_hours_this_gap += 1
        acc_neg_energy_this_gap += surplus

    if acc_total_energy_this_gap > 0:
        # We are out of the gap and have covered all negative energy in the gap with subsequent positive energy
        # Now we need to wrap up and record some stats for this gap
        list_gaps.append({
#            'acc_total_hours_this_gap'       = dfgapsacc_total_hours_this_gap,
#            'acc_total_energy_this_gap'      = acc_total_energy_this_gap,
            'acc_neg_hours_this_gap':  acc_neg_hours_this_gap,
            'acc_neg_energy_this_gap': acc_neg_energy_this_gap,
            })

        # And we need to reset the stats, so we are ready for the next gap
        gap_ongoing = False
        acc_total_hours_this_gap = 0
        acc_total_energy_this_gap = 0
        acc_neg_hours_this_gap = 0
        acc_neg_energy_this_gap = 0


if gap_ongoing:
    # When we reached the end of the dataset, we were in an ongoing gap, which needs to be recorded
    list_gaps.append({
        'acc_neg_hours_this_gap':  acc_neg_hours_this_gap,
        'acc_neg_energy_this_gap': acc_neg_energy_this_gap,
        })

df_gaps = DataFrame(list_gaps)

df_gaps.sort_values('acc_neg_hours_this_gap', inplace=True)
print(df_gaps)
print(df_gaps.sum())

df_gaps.sort_values('acc_neg_energy_this_gap', inplace=True)
print(df_gaps)
print(df_gaps.sum())


pc = plotcanvas(outfilename='test_ve_gaphours.png', counth=1)
pc.plot_gap_hours(df_gaps, axnum=0, titlesuffix='asdf')
pc.output_to_file()

"""






