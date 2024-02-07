from numpy import linspace, array, minimum, nan, where, trapz, timedelta64
import numpy as np
from pandas import Series
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
    srcUrl = 'https://api.energidataservice.dk/dataset/',
    srcTable = 'PowerSystemRightNow',
    params = {
        'start':  '2023-10-09T20:00',
        'end':    '2023-10-09T21:00',
        'sort':   'Minutes1DK',
        #'timezone': 'dk',
    },
    tablekey = 'records',
    indexkey = 'Minutes1DK',
)
rc.runRequest()
dffull = rc.getAsDataFrame()

