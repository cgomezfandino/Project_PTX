import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as web


def momentum(activo=None ,start=None, end=None, data_src='google'):

    name = activo
    start = start
    end = end
    # price = OHLC
    data_source = data_src

    df  = web.DataReader(name=name, data_source=data_source, start=start, end=end)#[price]
    return df

activo = momentum(activo='SPY',start='2010-01-01',end='2015-12-31')

activo['returns'] = np.log(activo['Close']/activo['Close'].shift(1))

str_rtrn = ['returns']

for m in [1,10,30]:
    activo['position_%d' % m] = np.sign(activo['returns'].rolling(m).mean())
    activo['strategy_%d' % m] = activo['position_%d' % m].shift(1) * activo['returns']
    # activo['str_rtrn'].append(activo['strategy_%d' % m])
    str_rtrn.append('strategy_%d' % m)

activo[str_rtrn].dropna().cumsum().apply(np.exp).plot(title='SPY - 1D -  2010-2015',
                                                      figsize=(10, 6), style=['-', '--', '--','--'])
plt.show()
# str_rtrn.dropna()
# print activo.head()
# print str_rtrn
