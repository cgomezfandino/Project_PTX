import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as web


class momentum_strat(object):

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

#Creating list for save the columns for analysis
str_rtrn = ['returns']
drawdown = []


for m in [1,10,30]:
    activo['position_%d' % m] = np.sign(activo['returns'].rolling(m).mean())
    activo['strategy_%d' % m] = activo['position_%d' % m].shift(1) * activo['returns']
    str_rtrn.append('strategy_%d' % m)


# cumulative returns and max(cumulative return)
for dd in str_rtrn:
    # print dd
    activo['cumret_%s' %dd] = activo[dd].cumsum().apply(np.exp)
    activo['cummax_%s' %dd] = activo['cumret_%s' %dd].cummax()
    activo['drawdown_%s' %dd]= activo['cummax_%s' %dd] - activo['cumret_%s' %dd]
    drawdown.append('drawdown_%s' %dd)

# Drawdown Calculus:
# for r in drawdown:
#     print 'el drawdown para la estrategia', r, 'es :', np.round(activo[r].max(),5)

# Plotting: Drawdown calculus for each strategy
activo[['cummax_strategy_1','cumret_strategy_1']].plot(figsize=(10, 6))
plt.show()


# Plotting: All strategies
activo[str_rtrn].dropna().cumsum().apply(np.exp).plot(title='SPY - 1D -  2010-2015',
                                                      figsize=(10, 6), style=['-', '--', '--','--'])
plt.show()
str_rtrn.dropna()
print activo.head()
print str_rtrn
