#from numpy import linspace, array, minimum
#from pandas import DataFrame, to_datetime
#from restclient import RestClient
#from veplots import plotcanvas
#from energinetdata import CapacitiesVE as CapVE
from energinetdata import Consumption

cons = Consumption(start='2013-01-01T00:00', end='2024-01-01T00:00')

dfcons = cons.getAsDataFrame()
dfcons2=dfcons.unstack()
dfcons2[('GrossConsumptionMWh','Total')]=dfcons2[('GrossConsumptionMWh','DK1')]+dfcons2[('GrossConsumptionMWh','DK2')]
print(dfcons)
