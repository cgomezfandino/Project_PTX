import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
import datetime as dt
import v20
from configparser import ConfigParser

# Create an object config
config = ConfigParser()
# Read the config
config.read("pyalgo.cfg")

ctx = v20.Context(
    'api-fxpractice.oanda.com',
    443,
    True,
    application='sample_code',
    token=config['oanda_v20']['access_token'],
    datetime_format='RFC3339')

start = '2010-01-01'

end = '2015-01-01'

# This string suffix is needed to conform to the Oanda API requirements regarding start and end times.
suffix = '.000000000Z'
fromTime = dt.datetime.combine(pd.to_datetime(start), dt.time(9, 00))

fromTime = fromTime.isoformat('T') + suffix


toTime = dt.datetime.combine(pd.to_datetime(end), dt.time(16, 00))
toTime = toTime.isoformat('T') + suffix


res = ctx.instrument.candles(
    instrument='EUR_USD',
    fromTime=fromTime,
    toTime=toTime,
    granularity='H4',
    price='A')

# data.keys()

raw = res.get('candles')

raw = [cs.dict() for cs in raw]

for cs in raw:
    cs.update(cs['ask'])
    del cs['ask']

data = pd.DataFrame(raw)

data['time'] = pd.to_datetime(data['time'], unit='ns')

data = data.set_index('time')

data.index = pd.DatetimeIndex(data.index)

# print data.info()

cols = ['c','l','h','o']

data[cols] = data[cols].astype('float64')

data.rename(columns = {'c':'CloseAsk', 'l':'LowAsk',
                              'h':'HighAsk', 'o':'OpenAsk'},inplace=True)

data['returns'] = np.log(data['CloseAsk']/data['CloseAsk'].shift(1))

print data