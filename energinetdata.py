

from numpy import linspace, array, minimum
from pandas import DataFrame, to_datetime, concat

# Own modules
from restclient import RestClient

# Get electric production capacities for DK1+DK2 from EnergiDataService
# Warning: Production capacities are not available after july 2022.
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
        self.dfve = self.dffull[['SolarPowerCapacity','OffshoreWindCapacity','OnshoreWindCapacity']]

    def getAsDataFrame(self):
        return self.dfve

class ConsumptionProductionVE():
    def __init__(self, start: str, end: str):
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
        self.dffull = self.rc.getAsDataFrame().reset_index().set_index(['HourUTC','PriceArea']).groupby(level=0).sum()

        self.offshorelist = ['OffshoreWindLt100MW_MWh', 'OffshoreWindGe100MW_MWh',]
        self.onshorelist =  ['OnshoreWindLt50kW_MWh', 'OnshoreWindGe50kW_MWh', ]
        self.solarlist =    ['SolarPowerLt10kW_MWh', 'SolarPowerGe10Lt40kW_MWh', 'SolarPowerGe40kW_MWh', 'SolarPowerSelfConMWh',]
        self.dfve = DataFrame()
        self.dfve['consumptotal']  = self.dffull['GrossConsumptionMWh'].copy()
        self.dfve['offshoretotal'] = self.dffull[self.offshorelist].sum(axis=1)
        self.dfve['onshoretotal']  = self.dffull[self.onshorelist].sum(axis=1)
        self.dfve['solartotal']    = self.dffull[self.solarlist].sum(axis=1)

    def getAsDataFrame(self):
        return self.dfve

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



if __name__ == '__main__':
    cons = Consumption(start='2023-05-31T02:00', end='2023-07-01T01:00')
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


