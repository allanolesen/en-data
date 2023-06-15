from numpy import linspace, array, minimum
from pandas import DataFrame, to_datetime
from restclient import RestClient

def printstats(df, columnlist, description='', sercap=None):

    print('--------')
    print('Statistics for :    ', description)
    print('Period:             ', df.index.min(), ' - ', df.index.max())
    print('Columns:            ', columnlist)

    serProd = df[columnlist].sum(axis=1) #df2.loc(axis=1)['SolarPowerGe40kW_MWh']

    #if sercap is not None:
    #    serProdRatio = serProd / sercap
    #else:
    #    serProdRatio = serProd

    #serProdSorted = serProdRatio.sort_values()
    #serProdSorted = serProd.sort_values()
    #maxProd = serProdSorted[-1]
    #estCap = 1.25 * maxProd

    if sercap is not None:
        estCap = sercap.mean()
        serProdRatio = serProd / sercap
        serProdRatioSorted = serProdRatio.sort_values()
        serProdSorted = serProd.sort_values()
        maxProd = serProdSorted[-1]
    else:
        serProdSorted = serProd.sort_values()
        maxProd = serProdSorted[-1]
        estCap = 1.25 * maxProd
        serProdRatioSorted = serProdSorted / estCap

    #print(serSolarSorted)
    print('Max. production, MW:', maxProd)
    print('Est. capacity, MW:  ', estCap)
    print('Avg. prod., MW:     ', serProdSorted.mean())

    print('Total prod., MWh:   ', serProdSorted.sum())
    print('Total prod., TJ:    ', serProdSorted.sum() * 3600 / 1e6)

    print((serProdRatioSorted).quantile(linspace(0,1,21)).map('{:.2%}'.format))
    print((serProdRatioSorted/serProdRatioSorted.mean()).quantile(linspace(0,1,21)).map('{:.2%}'.format))



rc = RestClient(
    srcUrl = 'https://api.energidataservice.dk/dataset/',
    params = {
        'offset': '0',

#        'start':  '2021-01-01T00:00',
#        'end':    '2022-01-01T00:00',
#        'end':    '2022-01-01T02:00',

#        'start':  '2022-01-01T00:00',
#        'end':    '2023-01-01T00:00',

#        'start':  '2022-06-01T22:00',
#        'end':    '2023-06-01T22:00',

#        'start':  '2023-04-30T22:00',
#        'end':    '2023-05-31T22:00',

#        'start':  '2023-04-12T02:00',
#        'end':    '2023-04-13T02:00',

#        'start':  '2022-03-01T00:00',
#        'end':    '2022-03-12T00:00',

        'start':  '2022-08-07T16:00',
        'end':    '2022-08-24T00:00',


#            'start':  '2017-01-01T00:00',
#            'start':  '2018-01-01T00:00',
#            'start':  '2019-01-01T00:00',
#            'start':  '2020-01-01T00:00',


#            'start':  '2023-01-01T00:00',
#            'end':    '2018-01-01T00:00',
#            'end':    '2019-01-01T00:00',
#            'end':    '2020-01-01T00:00',
#            'end':    '2021-01-01T00:00',


#        'end':    '2023-04-01T00:00',
#        'filter': '{"PriceArea": ["DK1"]}',
        'sort':   'HourUTC ASC',
        #'timezone': 'dk',
    },
    tablekey = 'records',
    indexkey = 'HourUTC',
)

#outfilename = 'graph_2021.png'

#outfilename = 'graph_2022.png'
#outfilename2 = 'scatter_2022.png'

#outfilename = 'graph_2022-23.png'

#outfilename = 'graph_2023_1M.png'
#outfilename2 = 'scatter_2023_1M.png'

#outfilename = 'graph_2023_1D.png'


outfilename = 'graph_2021-2022.png'
outfilename2 = 'scatter_2021-2022.png'

#outfilename = 'graph_2022_dunkelflaute2.png'
#outfilename2 = 'scatter_2022_dunkelflaute2.png'


def getCapacities(idx=None):
    capdict = {
            'windtotal': { # https://ens.dk/sites/ens.dk/files/Statistik/energistatistik2021.pdf
                    '2015-12-31T23:00:00':  5077,
                    '2019-12-31T23:00:00':  6111,
                    '2020-12-31T23:00:00':  6267,
                    '2021-09-06T22:00:00':  6367, # 754 MW added in 2021, of which 603 MW from Kriegers Flak officially opened on 6th Sep.
                    '2021-09-06T23:00:00':  6970, # Remaining 151 MW distributed with 100 MW before this date and 51 after
                    '2021-12-31T23:00:00':  7021,
                    '2022-12-31T23:00:00':  7121, # Guess
                    '2023-12-31T23:00:00':  7221, # Guess
                },
            'solartotal': { # https://ens.dk/sites/ens.dk/files/Statistik/energistatistik2021.pdf
                    '2015-12-31T23:00:00':   782,
                    '2019-12-31T23:00:00':  1080,
                    '2020-12-31T23:00:00':  1304,
                    '2021-12-31T23:00:00':  1704,

                    '2022-03-31T22:00:00':  1954, # https://www.ft.dk/samling/20211/almdel/KEF/bilag/493/2623797/index.htm
                    '2022-06-30T22:00:00':  2339, # https://www.ft.dk/samling/20211/almdel/KEF/bilag/493/2623797/index.htm

                    '2022-12-31T23:00:00':  3015, # https://ens.dk/sites/ens.dk/files/Sol/solcelleopgoerelse_q1_2023.pdf
                    '2023-03-31T22:00:00':  3251, # https://ens.dk/sites/ens.dk/files/Sol/solcelleopgoerelse_q1_2023.pdf
                    '2023-12-31T23:00:00':  4000, # Guess
                },
        }

    capdf = DataFrame(capdict)
    idxdf = DataFrame(index=idx)


    #try:
    if True:
        capdf.index = to_datetime(capdf.index)
    #except:
    #    pass



    capdf.sort_index(inplace=True)
    capdf = capdf.resample('1H').interpolate()

#    idxdf[capdf.columns] = capdf[capdf.columns]

    if idx is not None:
        idxdf = capdf.loc(axis=0)[idx]
    else:
        idxdf = capdf

    return idxdf #capdf

"""
rcPrices = RestClient(
    srcTable = 'ElSpotPrices',
    parent = rc,
)
rcPrices.runRequest()
dfPrices = rcPrices.getAsDataFrame()

rcProduction = RestClient(
    srcTable = 'ElectricityBalanceNonv',
    parent = rc,
)
rcProduction.runRequest()
dfProduction = rcProduction.getAsDataFrame()
"""


rcProdSettled = RestClient(
    srcTable = 'ProductionConsumptionSettlement',
    parent = rc,

)
rcProdSettled.runRequest()
dfProdSettled = rcProdSettled.getAsDataFrame()

#print(dfProdSettled)

df2 = dfProdSettled.reset_index().set_index(['HourUTC','PriceArea']).groupby(level=0).sum()
#print(df2)

dfcap = getCapacities(df2.index)



windlist = []
solarlist = []
for colname in df2.columns:
    if 'shoreWind' in colname:
        windlist.append(colname)
    if 'SolarPower' in colname:
        solarlist.append(colname)




print('--------------- Diagram start ------------------------')

act_inst_factor = 1

consumplist = ['GrossConsumptionMWh']

dfGraphAbs = df2[consumplist]
dfGraphAbs.loc[df2.index,'windtotal'] = df2[windlist].sum(axis=1) * act_inst_factor
dfGraphAbs.loc[df2.index,'solartotal'] = df2[solarlist].sum(axis=1) * act_inst_factor
dfGraphAbs.loc[df2.index,'wstotal'] = dfGraphAbs['windtotal'] + dfGraphAbs['solartotal']
dfGraphAbs.loc[df2.index,'wssurplus'] = dfGraphAbs['windtotal'] + dfGraphAbs['solartotal'] - dfGraphAbs['GrossConsumptionMWh']

dfGraphAbs.loc[df2.index,'windcf'] = dfGraphAbs['windtotal'] / dfcap['windtotal']
dfGraphAbs.loc[df2.index,'solarcf'] = dfGraphAbs['solartotal'] / dfcap['solartotal']


dfGraphSorted = dfGraphAbs.sort_values(by='wssurplus', axis=0).reset_index()


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

mydpi = 100
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=False, figsize=(1920/mydpi,1080/mydpi), dpi=mydpi)

x = array(dfGraphAbs.index)
y1 = array(dfGraphAbs['wstotal'])
y2 = array(dfGraphAbs['GrossConsumptionMWh'])

if act_inst_factor == 1:
    ax1.set_title('Elforbrug og VE-produktion')
else:
    ax1.set_title('Elforbrug og VE-produktion ved {:.00f}x faktisk kapacitet'.format(act_inst_factor))

#ax2.plot(x, y1, '-')
ax1.plot(x, y2, '-', label='Elforbrug DK1+DK2')
ax1.plot(x, y1, '-', color='C2', label='Elproduktion fra sol og vind DK1+DK2')
ax1.fill_between(x, y1, y2, where=(y1 > y2), color='C2', alpha=0.3,
                 interpolate=True)
ax1.fill_between(x, y1, y2, where=(y1 <= y2), color='C3', alpha=0.3,
                 interpolate=True)
ax1.fill_between(x, 0, minimum(y1,y2), color='C2', alpha=0.6,
                 interpolate=True)
ax1.legend()
ax1.set_xlabel('Dato og tid, UTC')
ax1.set_ylabel('MW')


x = array(dfGraphAbs.index)
y1 = array(dfGraphAbs['wssurplus'])

ax2.set_title('Overskud af VE-produktion i forhold til forbrug')
ax2.fill_between(x, 0, y1, where=(y1 > 0), color='C2', alpha=0.3,
                 interpolate=True)
ax2.fill_between(x, 0, y1, where=(y1 <= 0), color='C3', alpha=0.3,
                 interpolate=True)
ax2.set_xlabel('Dato og tid, UTC')
ax2.set_ylabel('MW')


x = array(dfGraphSorted.index)
y1 = array(dfGraphSorted['wssurplus'])
negsum = ((y1<0) * y1).sum()
possum = ((y1>=0) * y1).sum()
negtimer = (y1<0).sum()
postimer = (y1>=0).sum()


negtext = '{:.0f} timer - {:.3f} GWh'.format(negtimer, negsum/1000)
postext = '{:.0f} timer - {:.3f} GWh'.format(postimer, possum/1000)



ax3.set_title('Overskud af VE-produktion i forhold til forbrug, sorteret')
#ax2.plot(x, y1, '-')
#ax2.plot(x, y2, '-')
ax3.fill_between(x, 0, y1, where=(y1 > 0), color='C2', alpha=0.3,
                 interpolate=True)
ax3.fill_between(x, 0, y1, where=(y1 <= 0), color='C3', alpha=0.3,
                 interpolate=True)
#ax2.fill_between(x, 0, minimum(y1,y2), color='C2', alpha=0.6,
#                 interpolate=True)
ax3.set_xlabel('Timer')
ax3.set_ylabel('MW')
ax3.text(x=negtimer/3, y=-500, ha='center', va='center', s=negtext, color='C3')
ax3.text(x=negtimer+postimer*2/3, y=500,  ha='center', va='center', s=postext, color='C2')


fig.tight_layout()

fig.savefig(outfilename)

print('--------------- Diagram end ------------------------')



mydpi = 200
fig, ax1 = plt.subplots(1, 1, sharex=False, figsize=(1920/mydpi,1080/mydpi), dpi=mydpi)

dfday = dfGraphAbs.resample('D').mean()

x = array(dfday['windcf'])
y = array(dfday['solarcf'])

ax1.set_title('Kapacitetsudnyttelse sol og vind i DK1+DK2, 24h-perioder i 2021-2022')
#ax2.plot(x, y1, '-')
ax1.scatter(x, y)
#ax1.legend()
ax1.set_xlabel('Kapacitetsudnyttelse vind')
ax1.set_ylabel('Kapacitetsudnyttelse sol')

fig.tight_layout()

fig.savefig(outfilename2)


print('--------------- Diagram end2 ------------------------')


#print(dfcap)


printstats(df2, windlist, description='Wind', sercap=dfcap['windtotal'])
printstats(df2, solarlist, description='Solar', sercap=dfcap['solartotal'])


"""
print(solarlist)
print()
print(windlist)
print()

#dfCompr2 = dfProdSettled[['SolarPowerGe40kW_MWh']]
#dfCompr = dfProdSettled[['PriceArea']]

serSolar = df2[solarlist].sum(axis=1) #df2.loc(axis=1)['SolarPowerGe40kW_MWh']
serSolarSorted = serSolar.sort_values()
maxProdSolar = serSolarSorted[-1]
estCapSolar = 1.25 * maxProdSolar

print(serSolarSorted)
print(maxProdSolar, estCapSolar, serSolarSorted.sum())
print((serSolar/estCapSolar).quantile(linspace(0,1,21)).map('{:.2%}'.format))

serWind = df2[windlist].sum(axis=1) #df2.loc(axis=1)['SolarPowerGe40kW_MWh']
serWindSorted = serWind.sort_values()
maxProdWind = serWindSorted[-1]
estCapWind = 1.25 * maxProdWind

print(serWindSorted)
print(maxProdWind, estCapWind, serWindSorted.sum())
print((serWind/estCapWind).quantile(linspace(0,1,21)).map('{:.2%}'.format))


#print(dfProdSettled.columns)
#print(serSolar)
#print(dfCompr)
#print(dfCompr2)
"""

"""
Planning:

Desired graphs:
 - Individual plots for wind and solar:
    - Time plot of production vs. installed capacity
        - Installed capacity as line
        - Production as green fill
    - Time plot of production as percent of capacity
        - 100 % as line
        - Actual percentage as green fill
    - S-curve plot of production as percent of capacity
        - 100% as line
        - Actual percentage as green fill
    - Time plot of production vs. consumption
    - Time plot of production as percent of consumption
    - Time plot of production surplus/deficit in MW
    - S-curve plot of production as percent of consumption
    - S-curve plot of production surplus/deficit in MW

    - More?




"""