

from numpy import linspace, array, minimum
from pandas import DataFrame, to_datetime, concat, Timestamp
from typing import Optional

# Own modules
from restclient import RestClient

# Get electric production capacities for DK1+DK2 from EnergiDataService
# Warning:  Production capacities are not available after july 2022.
#           Best guess of missing capacities can be added with method .add_missing()
class CapacitiesVE():
    def __init__(self):
        self.rc = RestClient(
            srcUrl = 'https://api.energidataservice.dk/dataset/',
            srcTable = 'CapacityPerMunicipality',
            params = {
                'offset': '0',
                'start':  '2016-11-01T00:00',
                'end':    '2023-01-01T00:00',
                'sort':   'Month ASC',
                #'timezone': 'dk',
            },
            tablekey = 'records',
            indexkey = 'Month',
        )
        self.rc.runRequest()
        self.dffull = self.rc.getAsDataFrame().groupby('Month').sum()

        #self.dfve = self.dffull[['SolarPowerCapacity','OffshoreWindCapacity','OnshoreWindCapacity']]

        self.dfve = DataFrame(index=self.dffull.index)
        self.dfve.loc(axis=1)['offshorecap'] = self.dffull[['OffshoreWindCapacity']]
        self.dfve.loc(axis=1)['onshorecap']  = self.dffull[['OnshoreWindCapacity']]
        self.dfve.loc(axis=1)['solarcap']    = self.dffull[['SolarPowerCapacity']]

    def getAsDataFrame(self):
        return self.dfve

    def add_missing(self):
        missingsolar = {
                    '2023-01-01':  3015, # https://ens.dk/sites/ens.dk/files/Sol/solcelleopgoerelse_q1_2023.pdf
                    '2023-03-31':  3251, # https://ens.dk/sites/ens.dk/files/Sol/solcelleopgoerelse_q1_2023.pdf
                    '2023-06-30':  3372, # https://ens.dk/sites/ens.dk/files/Sol/solcelleopgoerelse_q2_2023_0.pdf
                    '2024-01-01':  3500, # Guess
                }

        for missingdatestr, missingvalue in missingsolar.items():
            missingdate = Timestamp(missingdatestr)

            if missingdate not in self.dfve.index:
                self.dfve.loc[missingdate, 'solarcap'] = missingvalue

    def get_reindexed(self, idx):
        return self.dfve.resample('H').interpolate().reindex(idx)


class ConsumptionProductionVE():
    def __init__(self, start: str, end: str, doCalcDkSum: Optional[bool]=True ):
        self.rc = RestClient(
            srcUrl = 'https://api.energidataservice.dk/dataset/',
            srcTable = 'ProductionConsumptionSettlement',
            params = {
                'offset': '0',
                'start':  start,
                'end':    end,
                'sort':   'HourUTC ASC',
                'columns': 'HourUTC,PriceArea,GrossConsumptionMWh,OffshoreWindLt100MW_MWh,OffshoreWindGe100MW_MWh,OnshoreWindLt50kW_MWh,OnshoreWindGe50kW_MWh,SolarPowerLt10kW_MWh,SolarPowerGe10Lt40kW_MWh,SolarPowerGe40kW_MWh,SolarPowerSelfConMWh',

            },
            tablekey = 'records',
            indexkey = 'HourUTC',
        )
        self.rc.runRequest()
        self.dffullng = self.rc.getAsDataFrame().reset_index().set_index(['HourUTC','PriceArea'])
        if doCalcDkSum:
            self.dffull = self.dffullng.groupby(level=0).sum()
        else:
            self.dffull = self.dffullng

        self.offshorelist = ['OffshoreWindLt100MW_MWh', 'OffshoreWindGe100MW_MWh',]
        self.onshorelist =  ['OnshoreWindLt50kW_MWh', 'OnshoreWindGe50kW_MWh', ]
        self.solarlist =    ['SolarPowerLt10kW_MWh', 'SolarPowerGe10Lt40kW_MWh', 'SolarPowerGe40kW_MWh', 'SolarPowerSelfConMWh',]
        self.dfve = DataFrame()
        self.dfve['consumptotal']  = self.dffull['GrossConsumptionMWh'].copy()
        self.dfve['offshoretotal'] = self.dffull[self.offshorelist].sum(axis=1)
        self.dfve['onshoretotal']  = self.dffull[self.onshorelist].sum(axis=1)
        self.dfve['solartotal']    = self.dffull[self.solarlist].sum(axis=1)
        self.dfve['vetotal']       = self.dfve[['offshoretotal','onshoretotal','solartotal']].sum(axis=1)
        self.dfve['vesurplus']     = self.dfve['vetotal'] - self.dfve['consumptotal']

    def getAsDataFrame(self):
        return self.dfve

    def getcap(self):

        capve = CapacitiesVE()
        capve.add_missing()
        dfcap = capve.get_reindexed(self.dfve.index)
        return dfcap

    def get_with_rescaled_cap(self, newcap_offshore=None, newcap_onshore=None, newcap_solar=None, mult_offshore=None, mult_onshore=None, mult_solar=None):
        dfcap = self.getcap()
        dfout = DataFrame(index=self.dfve.index)
        dfout['consumptotal'] = self.dfve['consumptotal']

        if newcap_offshore is not None:
            offshore_mult = newcap_offshore / dfcap['offshorecap']
        elif mult_offshore is not None:
            offshore_mult = mult_offshore
        else:
            offshore_mult = 1
        dfout['offshoretotal'] = self.dfve['offshoretotal'] * offshore_mult


        if newcap_onshore is not None:
            onshore_mult = newcap_onshore / dfcap['onshorecap']
        elif mult_onshore is not None:
            onshore_mult = mult_onshore
        else:
            onshore_mult = 1
        dfout['onshoretotal'] = self.dfve['onshoretotal'] * onshore_mult


        if newcap_solar is not None:
            solar_mult = newcap_solar / dfcap['solarcap']
        elif mult_solar is not None:
            solar_mult = mult_solar
        else:
            solar_mult = 1
        dfout['solartotal'] = self.dfve['solartotal'] * solar_mult

        dfout['vetotal']       = dfout[['offshoretotal','onshoretotal','solartotal']].sum(axis=1)
        dfout['vesurplus']     = dfout['vetotal'] - dfout['consumptotal']

        return dfout

    def get_streaks(self, get_stacked=False, newcap_offshore=None, newcap_onshore=None, newcap_solar=None, mult_offshore=None, mult_onshore=None, mult_solar=None):

        df = self.get_with_rescaled_cap(newcap_offshore=newcap_offshore, newcap_onshore=newcap_onshore, newcap_solar=newcap_solar,
            mult_offshore=mult_offshore, mult_onshore=mult_onshore, mult_solar=mult_solar)

        # Create a unique serial number for each streak and write this into a new column
        consecutives = df['vesurplus'].lt(0).diff().ne(0).cumsum()
        df['streak_ID'] = consecutives

        #return df

        dfagg = df['vesurplus'].groupby(df['streak_ID']).agg(['count', 'sum'])

        if not get_stacked:
            return dfagg

        # Group negative streaks together if they are not followed by a positive streak of the same size.

        streak_sum = 0
        stackID = 1
        stacksubID = 1 * (dfagg['sum'].iloc[0] >= 0)

        for idxval in dfagg.index:
            curval = dfagg.loc[idxval, 'sum']
            streak_sum += curval

            if (streak_sum >= 0):
                # This is the last row in this combined streak
                # We will not want this included in the negative streak, so we
                #   give it an impossibly high subID, which can later be filtered.
                dfagg.loc[idxval, 'stackID'] = stackID
                dfagg.loc[idxval, 'stacksubID'] = 999999

                # Reset counters
                streak_sum = 0
                stackID += 1
                stacksubID = 0

            else:
                dfagg.loc[idxval, 'stackID'] = stackID
                dfagg.loc[idxval, 'stacksubID'] = stacksubID
                stacksubID += 1


        dfagg['stackID'] = dfagg['stackID'].astype('int')
        dfagg['stacksubID'] = dfagg['stacksubID'].astype('int')

        dfagg.set_index(['stackID', 'stacksubID'], inplace=True)

        return dfagg






class Consumption():
    def __init__(self, start: str, end: str):
        self.rc = RestClient(
            srcUrl = 'https://api.energidataservice.dk/dataset/',
            srcTable = 'ProductionConsumptionSettlement',
            params = {
                'offset': '0',
                'start':  start,
                'end':    end,
                'sort':   'HourUTC ASC',
                'columns': 'HourUTC,PriceArea,GrossConsumptionMWh',

            },
            tablekey = 'records',
            indexkey = 'HourUTC',
        )
        self.rc.runRequest()
        self.dffull = self.rc.getAsDataFrame().reset_index().set_index(['HourUTC','PriceArea'])
        self.dfdk = self.dffull.groupby(level=0).sum()


    def getAsDataFrame(self):
        return self.dffull

class ElSpotPrices():
    def __init__(self, start: str, end: str):
        self.rc = RestClient(
            srcUrl = 'https://api.energidataservice.dk/dataset/',
            srcTable = 'ElSpotPrices',
            params = {
                'offset': '0',
                'start':  start,
                'end':    end,
                'sort':   'HourUTC ASC',
                'columns': 'HourUTC,HourDK,PriceArea,SpotPriceDKK',
            },
            tablekey = 'records',
            indexkey = 'HourUTC',
        )
        self.rc.runRequest()
        self.dffull = self.rc.getAsDataFrame().reset_index().set_index(['HourUTC','PriceArea'])
        self.dfdk = self.dffull.groupby(level=0).sum()


    def getAsDataFrame(self):
        return self.dffull



if __name__ == '__main__':
    cons = Consumption(start='2022-05-31T02:00', end='2023-07-01T01:00')
    dfcons = cons.getAsDataFrame().unstack()
    dfmonthmean = dfcons.resample('M').mean()
    dfmonthmax = dfcons.resample('M').max()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mydpi = 200
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False, figsize=(1920/mydpi,1080/mydpi), dpi=mydpi)
    ax1.set_title('Elforbrug pr. måned, DK1')
    ax2.set_title('Elforbrug pr. måned, DK2')

    x = array(dfmonthmax.index)
    y1 = array(dfmonthmax[('GrossConsumptionMWh','DK1')])
    y2 = array(dfmonthmax[('GrossConsumptionMWh','DK2')])
    ax1.plot(x, y1, '-', label='Maksimalt elforbrug i DK1')
    ax2.plot(x, y2, '-', label='Maksimalt elforbrug i DK2')
    #ax1.bar(x, y, '-', label='Makximalt elforbrug i DK1')

    x = array(dfmonthmean.index)
    y1 = array(dfmonthmean[('GrossConsumptionMWh','DK1')])
    y2 = array(dfmonthmean[('GrossConsumptionMWh','DK2')])
    ax1.plot(x, y1, '-', label='Middel elforbrug i DK1')
    ax2.plot(x, y2, '-', label='Middel elforbrug i DK2')
    #ax1.bar(x, y, '-', label='Middel elforbrug i DK1')

    ax1.legend(loc='upper center')
    ax1.set_xlabel('År')
    ax1.set_ylabel('MW')

    ax2.legend(loc='upper center')
    ax2.set_xlabel('År')
    ax2.set_ylabel('MW')

    # Currently, there are no minor ticks,
    #   so trying to make them visible would have no effect
    ax1.xaxis.get_ticklocs(minor=True)     # []
    ax2.xaxis.get_ticklocs(minor=True)     # []



    # Initialize minor ticks
    ax1.minorticks_on()
    ax2.minorticks_on()

    ax1.set_xticks(ax1.get_xticks(minor=True)[::2], minor=True)
    ax2.set_xticks(ax2.get_xticks(minor=True)[::2], minor=True)


    # Now minor ticks exist and are turned on for both axes

    # Turn off y-axis minor ticks
    ax1.yaxis.set_tick_params(which='minor', bottom=False)
    ax2.yaxis.set_tick_params(which='minor', bottom=False)

    #ax1.tick_params(axis='x', which='minor') #, bottom=False)
    ax1.grid(color='gray', which='major', alpha=0.5, linestyle='-', linewidth=1)
    ax1.grid(color='gray',axis='x', which='minor', alpha=0.2, linestyle='-', linewidth=1)

    ax2.grid(color='gray', which='major', alpha=0.5, linestyle='-', linewidth=1)
    ax2.grid(color='gray',axis='x', which='minor', alpha=0.2, linestyle='-', linewidth=1)


    fig.tight_layout()

    fig.savefig('dkconsump4.png')



    cap = CapacitiesVE().getAsDataFrame()
    print(cap)

    spot = ElSpotPrices(start='2022-12-12T02:00', end='2023-12-12T02:00')
    dfspot = spot.getAsDataFrame() #.unstack()
    print(dfspot)

    import pandas as pd

#    dfspotnight = dfspot[dfspot['HourDK']<7]
    dfspotnight = dfspot.loc(axis=0)[:,'DK1']
    dfspotnight.loc(axis=1)['HourNumDK'] = pd.DatetimeIndex(dfspotnight.loc(axis=1)['HourDK']).hour
    dfspotnight = dfspotnight[dfspotnight.loc(axis=1)['HourNumDK'] < 7]
    print(dfspotnight)
    print(dfspotnight.loc[:,'SpotPriceDKK'].mean() / 800)



    prod = ConsumptionProductionVE(start='2023-05-01T02:00', end='2023-11-01T01:00', doCalcDkSum=False)
    dfprod = prod.getAsDataFrame() #.unstack()

    dfprod['SpotPriceDKK'] = dfspot['SpotPriceDKK']
    dfprod['SolarValueDKK'] = dfspot['SpotPriceDKK'] * dfprod['solartotal']
    dfprod['OffshoreValueDKK'] = dfspot['SpotPriceDKK'] * dfprod['offshoretotal']
    dfprod['OnshoreValueDKK'] = dfspot['SpotPriceDKK'] * dfprod['onshoretotal']

    dfprodsum = dfprod.unstack().sum()


    import pandas as pd
    pd.options.display.float_format = '{:,.2f} DKK/MWh'.format

    #dfprodfull = prod.dffullng
    print(dfprod)
    print(dfprodsum)
    print()
    print('Spotpris DKK uvægtet:')
    print(dfprod['SpotPriceDKK'].unstack().mean())
    print('Spotpris DKK vægtet efter produktion fra sol:')
    print(dfprodsum['SolarValueDKK']/dfprodsum['solartotal'])
    print('Spotpris DKK vægtet efter produktion fra vind offshore:')
    print(dfprodsum['OffshoreValueDKK']/dfprodsum['offshoretotal'])
    print('Spotpris DKK vægtet efter produktion fra vind onshore:')
    print(dfprodsum['OnshoreValueDKK']/dfprodsum['onshoretotal'])

