__author__ = 'cgomezfandino@gmail.com'

import datetime as dt
import v20
from pandas_datareader import data as web
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn


# class mr_ImpliedVolatility(object):
#
#     def __init__(self):
#
#
#
#
# if __name__ == '__main__':
#     mombt = Momentum_Backtester('AAPL', '2010-1-1', '2016-10-31')
#     print(mombt.run_strategy())
#     # print(mombt.strat_drawdown())
#     print(mombt.plot_strategy())

roll = 30
df = web.DataReader('YHOO','google', start='01/01/2010', end='01/01/2015')
# df.rename(columns={'':'Close'},inplace=True)

df['return'] = np.log(df['Close']/df['Close'].shift(1))
df['sigma_rol'] = df['return'].rolling(roll).std()

mu = df['return'].mean()
mu_vol = df['sigma_rol'].mean()
sigma = df['return'].std()

df[['sigma_rol']].plot(title='sigma_rolling', figsize=(10, 6))
plt.axhline(mu_vol,color='r')
plt.show()

# print df



