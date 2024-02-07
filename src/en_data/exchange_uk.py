from numpy import linspace, array, minimum, nan, where, trapz, timedelta64
import numpy as np
from pandas import Series
import pandas as pd

#from pandas import DataFrame, to_datetime, concat, Timestamp
#from typing import Optional

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from datetime import date

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
        'start':  '2023-12-29T12:00',
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

# insert extra values where data cross 0
sery = df['Exchange_DK1_GB']

signs = np.sign(sery)
mask_bef = signs.diff(periods=-1).abs().eq(2)
mask_aft = signs.diff().abs().eq(2)

sery_bef = sery[mask_bef]
sery_aft = sery[mask_aft]

times_bef = sery_bef.index.values
values_bef = sery_bef.values
times_aft = sery_aft.index.values
values_aft = sery_aft.values

times_int = times_bef + (times_aft-times_bef) * values_bef / (values_bef-values_aft)
ser_int = Series(0, index=times_int, dtype=float)
sery_int = pd.concat([sery,ser_int]).sort_index()

countw: int = 1
counth: int = 1
pixelw: int = 1920
pixelh: int = 1080
dpi: int = 200

fn = 'uk_exhange.png'

print(counth, countw, pixelw/dpi, pixelh/dpi, dpi)

fig, ax = plt.subplots(counth, countw, figsize=(pixelw/dpi, pixelh/dpi), dpi=dpi)

ax.set_title('Viking Link')

#ax.set_xlabel('Dato og tid')
ax.set_ylabel('MW')


x = array(sery_int.index)
y = array(sery_int)
ypos = where(y>=0, y, nan)
yneg = where(y<=0, y, nan)
ypos2 = where(y>=0, y, 0)
yneg2 = where(y<=0, y, 0)
sumpos = trapz(ypos2, x) / timedelta64(1000, 'h')
sumneg = trapz(yneg2, x) / timedelta64(1000, 'h')

#colors = where(y>=0, 'C2', 'C3')


#myFmt = mdates.DateFormatter('%d-%m %H:%M')
#ax.xaxis.set_major_formatter(myFmt)


poslabel = 'UK -> DK1 ({:.3f} GWh)'.format(sumpos)
neglabel = 'UK <- DK1 ({:.3f} GWh)'.format(sumneg)


ax.plot(x, ypos, '-', linewidth=1, color='C2', label=poslabel, solid_capstyle='butt')
ax.plot(x, yneg, '-', linewidth=1, color='C3', label=neglabel, solid_capstyle='butt')

ax.fill_between(x, 0, y, where=(y > 0), color='C2', alpha=0.3, interpolate=True)
ax.fill_between(x, 0, y, where=(y <= 0), color='C3', alpha=0.3, interpolate=True) #, edgecolor='blue', linewidth=3)


#ax.plot(x, y, '-', linewidth=3, color=colors, label='DK1 -> UK')


#ax.plot(x, y1, where=(y1>=0), '-', linewidth=3, color='C2', label='UK -> DK1')
#ax.plot(x, y1, where=(y1<0), '-', linewidth=3, color='C3', label='DK1 -> UK')

ax.legend()
ax.set_ylim((-1500,1500))
firstx = x[0]
print(firstx)
print(type(firstx))
ax.set_xlim((firstx,None))


# S axis
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b-%Y"))

ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
#ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d-%m"))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
#ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21]))
#ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
#plt.setp(ax.get_xticklabels(which='minor'), visible=False)
#plt.setp(ax.get_xticklabels(which='minor')[::2], visible=True)
#plt.setp(ax.get_xticklabels(which='minor')[1::2], visible=False)


ax.tick_params(axis='x', which='major', labelsize=10, pad=10)
ax.tick_params(axis='x', which='minor', labelsize=6)
#ax.tick_params(axis='x', which='major', pad=10)
#plt.xticks(rotation=270)

# Y axis
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1400))
ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(200))


# Both axes
ax.grid(which='major', linewidth=1, color='grey', alpha=0.3)
ax.grid(which='minor', linewidth=0.5, color='grey', alpha=0.1)


mestr = 'Allan Olesen ' + date.today().strftime('%d-%b-%Y')

xlim = ax.get_xlim()
xpos = xlim[0] + 0.01 * (xlim[1] - xlim[0])
ylim = ax.get_ylim()
ypos = ylim[0] + 0.012 * (ylim[1] - ylim[0])

ax.text(s=mestr, x=xpos, y=ypos, ha='left', va='center', color='lightgrey', alpha = 0.8, fontsize='small', fontstyle='italic', fontweight='black') #, backgroundcolor='white')



fig.tight_layout()
fig.savefig(fn)


