from numpy import linspace, array, minimum
#from pandas import DataFrame, to_datetime, concat, Timestamp
#from typing import Optional

from matplotlib import pyplot as plt
import matplotlib.dates as mdates

# Necessary when running on pythonanywhere.com
import matplotlib
matplotlib.use("Agg")

# Own modules
from restclient import RestClient
#from veplots import plotcanvas

rc = RestClient(
    # https://api.energidataservice.dk/dataset/PowerSystemRightNow?offset=0&sort=Minutes1UTC%20DESC
    # https://api.energidataservice.dk/dataset/PowerSystemRightNow?offset=0&start=2023-12-28T00:00&sort=Minutes1DK%20ASC
    srcUrl = 'https://api.energidataservice.dk/dataset/',
    srcTable = 'PowerSystemRightNow',
    params = {
        'offset': '0',
        'start':  '2023-12-29T00:00',
        'end':    '2023-12-31T00:00',
        'sort':   'Minutes1DK',
        #'timezone': 'dk',
    },
    tablekey = 'records',
    indexkey = 'Minutes1DK',
)
rc.runRequest()
dffull = rc.getAsDataFrame()

dfuk_exchange = dffull[['Exchange_DK1_GB']]

print(dffull)
print(dfuk_exchange)

df = dfuk_exchange

countw: int = 1
counth: int = 1
pixelw: int = 1920
pixelh: int = 1080
dpi: int = 200

fn = 'uk_exhange.png'

fig, ax = plt.subplots(counth, countw, figsize=(pixelw/dpi, pixelh/dpi), dpi=dpi)

ax.set_title('Viking Link')

ax.set_xlabel('Dato og tid')
ax.set_ylabel('MW')

x = array(df.index)
y1 = array(df['Exchange_DK1_GB'] * -1)

#myFmt = mdates.DateFormatter('%d-%m %H:%M')
#ax.xaxis.set_major_formatter(myFmt)



ax.plot(x, y1, '-', linewidth=3, color='C2', label='DK1 -> UK')

ax.legend()
ax.set_ylim((0,1400))


ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))

ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[3,6,9,12,15,18,21]))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

#plt.xticks(rotation=270)
ax.tick_params(axis='both', which='major', labelsize=12)
ax.tick_params(axis='both', which='minor', labelsize=6)


ax.grid(which='major', linewidth=1, color='grey', alpha=0.3)
ax.grid(which='minor', linewidth=0.5, color='grey', alpha=0.1)


fig.tight_layout()
fig.savefig(fn)


