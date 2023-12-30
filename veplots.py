# Plot miscellaneous diagrams for VE production versus consumption
# Allan H. Olesen 18-Jun-2023


from typing import Optional
from matplotlib import pyplot as plt
from pandas import DataFrame
from numpy import array, zeros_like, minimum

# Necessary when running on pythonanywhere.com
import matplotlib
matplotlib.use("Agg")


class plotcanvas():

    def __init__(self, outfilename: str, countw: int = 1, counth: int = 3, pixelw: int = 1920, pixelh: int = 1080, dpi: int = 200, subplotkwargs: Optional[dict] = None):
        self.outfilename = outfilename
        self.countw = countw
        self.counth = counth
        self.pixelw = pixelw
        self.pixelh = pixelh
        self.dpi = dpi

        self.fig, self.axes = plt.subplots(self.counth, self.countw, figsize=(self.pixelw/self.dpi, self.pixelh/self.dpi), dpi=self.dpi)

        if self.countw*self.counth==1:
            self.axes=[self.axes]

    def plot_all(self, df:DataFrame, titlesuffix:Optional[str]=None):
        self.plot_total_prod_and_consumpt_to_ax(df, 0, titlesuffix)
        self.plot_prod_excess_to_ax(df, 1)
        self.plot_sorted_prod_excess_to_ax(df, 2)


    def plot_total_prod_and_consumpt_to_ax(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Elforbrug og VE-produktion')
        else:
            ax.set_title('Elforbrug og VE-produktion - ' + titlesuffix)

        ax.set_xlabel('Dato og tid, UTC')
        ax.set_ylabel('MW')

        #df.plot(ax=ax, kind='area', y=['solartotal','windtotal'],)
        #df.plot(ax=ax, kind='line', y='GrossConsumptionMWh',)
        #df.plot(ax=ax, kind='area', y=['solartotal','windtotal'],)

        x = array(df.index)
        y1 = array(df['vetotal'])
        y2 = array(df['consumptotal'])
        #y1 = array(df['wstotal'])
        #y2 = array(df['GrossConsumptionMWh'])

        ax.plot(x, y2, '-', linewidth=0.6, label='Elforbrug DK1+DK2')
        ax.plot(x, y1, '-', linewidth=0.6, color='C2', label='Elproduktion fra sol og vind DK1+DK2')

        ax.fill_between(x, y1, y2, where=(y1 > y2), color='C2', alpha=0.3,
                         interpolate=True, edgecolor='white', linewidth=0)
        ax.fill_between(x, y1, y2, where=(y1 <= y2), color='C3', alpha=0.3,
                         interpolate=True, edgecolor='white', linewidth=0)
        ax.fill_between(x, 0, minimum(y1,y2), color='C2', alpha=0.6,
                         interpolate=True, edgecolor='white', linewidth=0)
        ax.legend()

    def plot_prod_excess_to_ax(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Overskud af VE-produktion i forhold til forbrug')
        else:
            ax.set_title('Overskud af VE-produktion i forhold til forbrug - ' + titlesuffix)

        ax.set_xlabel('Dato og tid, UTC')
        ax.set_ylabel('MW')

        x = array(df.index)
        #y1 = array(df['vetotal'] - df['consumptotal'])
        y1 = array(df['vesurplus'])

        ax.fill_between(x, 0, y1, where=(y1 > 0), color='C2', alpha=0.3, interpolate=True)
        ax.fill_between(x, 0, y1, where=(y1 <= 0), color='C3', alpha=0.3, interpolate=True)
        #ax.legend()


    def plot_sorted_prod_excess_to_ax(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Overskud af VE-produktion i forhold til forbrug, sorteret')
        else:
            ax.set_title('Overskud af VE-produktion i forhold til forbrug, sorteret - ' + titlesuffix)

        ax.set_xlabel('Timer')
        ax.set_ylabel('MW')

        dfGraphSorted = df.sort_values(by='vesurplus', axis=0).reset_index()
        x = array(dfGraphSorted.index)
        y1 = array(dfGraphSorted['vesurplus'])
        negsum = ((y1<0) * y1).sum()
        possum = ((y1>=0) * y1).sum()
        negtimer = (y1<0).sum()
        postimer = (y1>=0).sum()

        ax.fill_between(x, 0, y1, where=(y1 > 0), color='C2', alpha=0.3, interpolate=True)
        ax.fill_between(x, 0, y1, where=(y1 <= 0), color='C3', alpha=0.3, interpolate=True)

        # Print summary of hours and GWh after finding best position in plot
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        yspan = ylim[1]-ylim[0]
        yfracpos = ylim[1]/yspan

        if yfracpos < 0.3:
            ypos1 = - 0.12 * yspan
            ypos2 = - 0.12 * yspan
        elif yfracpos > 0.7:
            ypos1 = 0.1 * yspan
            ypos2 = 0.1 * yspan
        else:
            ypos1 = 0.1 * yspan
            ypos2 = -0.12 * yspan

        xpos1 = (negtimer+postimer) * 0.005
        xpos2 = (negtimer+postimer) * 0.995

        negtext = '{:.0f} timer; {:.0f} GWh'.format(negtimer, negsum/1000)
        postext = '{:.0f} timer; {:.0f} GWh'.format(postimer, possum/1000)

        ax.text(x=xpos1, y=ypos1, ha='left', va='center', s=negtext, color='C3')
        ax.text(x=xpos2, y=ypos2, ha='right', va='center', s=postext, color='C2')
        #ax.legend()


    def plot_streak_hours(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Fortløbende timer med over-/underskud af VE')
        else:
            ax.set_title('Fortløbende timer med over-/underskud af VE - ' + titlesuffix)

        ax.set_ylabel('Timer')

        x = array(df.index).astype('str')
        y1 = array(df['count']) #.sort_values())
        mask = array(df['sum'] >= 0) #.sort_values())
        ax.bar(x[mask], y1[mask], color='C2', alpha=0.3)
        ax.bar(x[~mask], -y1[~mask], color='C3', alpha=0.3)

    def plot_streak_energy(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Fortløbende over-/underskud af energi fra VE')
        else:
            ax.set_title('Fortløbende over-/underskud af energi fra VE - ' + titlesuffix)

        ax.set_ylabel('GWh')

        x = array(df.index).astype('str')
        y1 = array(0.001 * df['sum'])
        mask = array(df['sum'] >= 0)
        ax.bar(x[mask], y1[mask], color='C2', alpha=0.3)
        ax.bar(x[~mask], y1[~mask], color='C3', alpha=0.3)


    def plot_streak_hours_stacked(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        if titlesuffix is None:
            ax.set_title('Fortløbende timer med over-/underskud af VE')
        else:
            ax.set_title('Fortløbende timer med over-/underskud af VE - ' + titlesuffix)

        ax.set_ylabel('Timer')
        ax.margins(y=0.2)
        ax.grid(color='lightgrey', axis='y')

        df2 = df.unstack(fill_value=0.0)
        x = array(df2.index).astype('int')
        y0 = zeros_like(x, dtype=float)
        color1, color2 = 'C3', 'C2'

        #ax.set_ylim(0,100)

        for colkey in df2.columns:
            if (colkey[0] == 'count') and (colkey[1] < 999998):
                y1 = array(df2[colkey])

                """
                print(colkey)
                print(x)
                print(y0)
                print(y1)
                """

                #ax.bar(x, y1, color='C3',   alpha=0.3, bottom=y0)
                ax.bar(x, y1, color=color1, alpha=0.3, bottom=y0, edgecolor=color1)
                color1, color2 = color2, color1
                y0 += y1



    def plot_streak_energy_stacked(self, df:DataFrame, axnum:int, titlesuffix:Optional[str]=None):
        ax=self.axes[axnum]

        #if titlesuffix is None:
        #    ax.set_title('Fortløbende timer med over-/underskud af VE')
        #else:
        #    ax.set_title('Fortløbende timer med over-/underskud af VE - ' + titlesuffix)

        ax.set_ylabel('GWh')

        df2 = df.unstack(fill_value=0.0)
        x = array(df2.index).astype('int')
        y0neg = zeros_like(x, dtype=float)
        y0pos = zeros_like(x, dtype=float)
        color1, color2 = 'C3', 'C2'

        for colkey in df2.columns:
            if (colkey[0] == 'sum') and (colkey[1] < 999998):
                y1 = array(0.001 * df2[colkey])

                """
                print('--------')
                print('color1: ', color1)
                print('colkey: ', colkey)
                print('x:      ', x)
                print('y0neg:  ', y0neg)
                print('y0pos:  ', y0pos)
                print('y1:     ', y1)
                """
                if color1 == 'C2':
                    ax.bar(x, y1, color=color1, alpha=0.3, bottom=y0neg, edgecolor=color1)
                    y0neg += y1
                else:
                    ax.bar(x, y1, color=color1, alpha=0.3, bottom=y0pos, edgecolor=color1)
                    y0pos += y1


                color1, color2 = color2, color1



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
