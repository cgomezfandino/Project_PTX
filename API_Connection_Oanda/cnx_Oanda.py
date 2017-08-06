import datetime as dt
import v20
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create an object config
config = ConfigParser()
# Read the config
config.read("../API_Connection_Oanda/pyalgo.cfg")

ctx = v20.Context(
    'api-fxpractice.oanda.com',
    443,
    True,
    application='sample_code',
    token=config['oanda_v20']['access_token'],
    datetime_format='RFC3339')

# This string suffix is needed to conform to the Oanda API requirements regarding start and end times.
suffix = '.000000000Z'
fromTime = dt.datetime(2016, 12, 8, 8, 0, 0)
fromTime = fromTime.isoformat('T') + suffix


toTime = dt.datetime(2016, 12, 10, 8, 0, 0)
toTime = toTime.isoformat('T') + suffix


res = ctx.instrument.candles(
    instrument='EUR_USD',
    fromTime=fromTime,
    toTime=toTime,
    granularity='M1',
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
# data['returns2'] = data['CloseAsk'].pct_change(1)

cols = []

for momentum in [15, 30 ,60, 120]:
    col = 'position %s' % momentum
    data[col] = np.sign(data['returns'].rolling(momentum).mean())
    cols.append(col)

strats = ['returns']

for col in cols:
    strat = 'strategy %s' % col.split(' ')[1]
    data[strat] = data[col].shift(1) * data['returns']
    strats.append(strat)

# Final Bakctest with not laverage
data[strats].dropna().cumsum().apply(np.exp).plot()
plt.title('Momentum Strategies with not Laverage - m1')
# Final Backtest with laverage
data[strats].dropna().cumsum().apply(lambda x: x * 20).apply(np.exp).plot()
plt.title('Momentum Strategies with Laverage - m1')
plt.show()