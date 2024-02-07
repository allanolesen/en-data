from typing import Optional
import requests
import json
import pandas as pd

class RestClient:
    def __init__(self,
            srcUrl: Optional[str] = None,
            srcTable: Optional[str] = None,
            columns: Optional[list] = None,
            params: Optional[dict] = None,
            tablekey: Optional[str] = None,
            indexkey: Optional[str] = None,
            #outputkeys: Optional[dict] = None,
            parent: Optional['RestClient'] = None
        ):

        self.srcUrl = srcUrl
        self.srcTable = srcTable
        self.columns = columns
        self.params = params
        #self.outputkeys = outputkeys
        self.tablekey = tablekey
        self.indexkey = indexkey
        self.parent = parent

        # Create a valid fallback for args
        if (parent is None) and (params is None):
            self.params = {}

        self.request = None
        self.reqText = None
        self.reqJson = None
        self.reqCode = None

    def runRequest(self):
        self.request = requests.request(
            'GET',
            self.getUrl(),
            params=self._resolve_var('params'),
        )
        self.reqCode = self.request.status_code
        self.reqText = self.request.text
        try:
            self.reqJson = json.loads(self.reqText)
        except:
            print('Extracting JSON from response failed.')
            print('Status code:   ', self.reqCode)
            print('Response text: ', self.reqText)

    def getAsDataFrame(self):
        if (self.reqCode != 200):
            raise Exception('Cannot convert to pandas DataFrame when request status code is', str(self.reqCode))

        #dictout = {}
        #for okkey, okval in self._resolve_var('outputkeys').items():
        #    dictout[okkey] = pd.DataFrame(self.reqJson[okval])

        #return dictout
        df = pd.DataFrame(self.reqJson[self._resolve_var('tablekey')])
        indexkey = self._resolve_var('indexkey')
        if indexkey is not None:
            df.set_index(indexkey, inplace=True)

        try:
            df.index = pd.to_datetime(df.index)
        except:
            pass

        return df

    def getUrl(self) -> str:
        return self._resolve_var('srcUrl') + str(self._resolve_var('srcTable'))

    def _resolve_var(self, varname: str):
        if getattr(self, varname) is not None:
            return getattr(self, varname)
        if isinstance(self.parent, RestClient):
            return self.parent._resolve_var(varname)
        raise Exception('No XXX given in this object or any of its parents')


if (__name__ == '__main__'):

    rc = RestClient(
        srcUrl = 'https://api.energidataservice.dk/dataset/',
        params = {
            'offset': '0',
#            'start':  '2017-01-01T00:00',
#            'start':  '2018-01-01T00:00',
#            'start':  '2019-01-01T00:00',
#            'start':  '2020-01-01T00:00',
#            'start':  '2021-01-01T00:00',
            'start':  '2022-01-01T00:00',
#            'start':  '2023-01-01T00:00',
#            'start':  '2023-04-01T00:00',
#            'end':    '2018-01-01T00:00',
#            'end':    '2019-01-01T00:00',
#            'end':    '2020-01-01T00:00',
#            'end':    '2021-01-01T00:00',
#            'end':    '2022-01-01T00:00',
            'end':    '2023-01-01T00:00',
#            'end':    '2023-04-01T00:00',
            'end':    '2023-04-17T00:00',
            'filter': '{"PriceArea": ["DK1"]}',
            'sort':   'HourUTC ASC',
            #'timezone': 'dk',
        },
        tablekey = 'records',
        indexkey = 'HourUTC',
    )

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

    rcProdSettled = RestClient(
        srcTable = 'ProductionConsumptionSettlement',
        parent = rc,
    )
    rcProdSettled.runRequest()
    dfProdSettled = rcProdSettled.getAsDataFrame()

    print(dfProdSettled)

    #https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?offset=0&sort=HourUTC%20DESC&timezone=dk

    #print('URL: ', rc.getUrl())
    #print('Params: ', rc.params)
    #rc.runRequest()

    #print('Status code: ', rc.reqCode)
    #print('Retrieved data as JSON: ', rc.reqJson)

    #df = rc.getAsDataFrame()
    #df = dfs['ElectricityBalanceNonv']

    #print(dfPrices)
    #print(dfProduction)

    serResults = pd.Series(dtype=float)
    serPrices = dfPrices['SpotPriceDKK']

    dfOut = pd.DataFrame(dtype=float)

    for colkey in ['ExchangeContinent', 'ExchangeGreatBelt', 'ExchangeNordicCountries']:
        cond = (dfProduction[colkey] > 0.0)
        dfProduction.loc[cond, colkey + '_pos'] = dfProduction.loc[cond, colkey]
        dfProduction.loc[~cond, colkey + '_neg'] = dfProduction.loc[~cond, colkey]

    for colkey in dfProduction.columns:
        if colkey not in ['HourDK', 'PriceArea']:
            serProd = dfProduction[colkey]
            serProd_x_Price = serProd * serPrices
            PriceAvg = serProd_x_Price.sum() / serProd.sum()
            serResults[colkey] = PriceAvg

            dfOut.loc[colkey, 'Total GWh'] = serProd.sum()/1000
            dfOut.loc[colkey, 'kDKK/GWh'] = PriceAvg
            dfOut.loc[colkey, 'Total kDKK'] = serProd_x_Price.sum()/1000


    print(serResults)

    #print(dfProduction[['ExchangeContinent', 'ExchangeContinent_pos']])

    #print(dfProduction.iloc[1,:])

    pd.set_option('display.float_format', lambda x: '%.0f' % x)

    print(dfOut)

    print(serPrices.iloc[-24:])

    serPricesNight = serPrices[serPrices.index.str.contains('T22|T23|T00|T01|T02|T03')]
    print(serPricesNight)
    print(serPricesNight.mean()/8)


