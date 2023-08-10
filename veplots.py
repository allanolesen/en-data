# Plot miscellaneous diagrams for VE production versus consumption
# Allan H. Olesen 18-Jun-2023


from typing import Optional
from matplotlib import pyplot as plt
from pandas import DataFrame

# Necessary when running on pythonanywhere.com
import matplotlib
matplotlib.use("Agg")


class plotcanvas():

    def __init__(self, outfilename: str, countw: int, counth: int, pixelw: int, pixelh: int, dpi: int, subplotkwargs: Optional[dict] = None):
        self.outfilename = outfilename
        self.countw = countw
        self.counth = counth
        self.pixelw = pixelw
        self.pixelh = pixelh
        self.dpi = dpi

        self.fig, self.axes = plt.subplots(self.counth, self.countw, figsize=(self.pixelw/self.dpi, self.pixelh/self.dpi), dpi=self.dpi)

        if self.countw*self.counth==1:
            self.axes=[self.axes]


    def plot_total_prod_and_consumpt_to_ax(self, df:DataFrame, axnum:int, title:Optional[str]=None):
        ax=self.axes[axnum]
#        df.plot(ax=ax, kind='area', y=['solartotal','windtotal'],)
        df.plot(ax=ax, kind='line', y='GrossConsumptionMWh',)
        df.plot(ax=ax, kind='area', y=['solartotal','windtotal'],)

    def output_to_file(self):
        self.fig.tight_layout()
        self.fig.savefig(self.outfilename)

"""
[1]
print('--------------- Diagram start ------------------------')

act_inst_factor = 1

consumplist = ['GrossConsumptionMWh']

dfGraphAbs = df2[consumplist].copy()

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
"""
