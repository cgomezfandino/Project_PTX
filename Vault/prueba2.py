import numpy as np
import pandas as pd

import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
from pandas.core import datetools

from pandas_datareader import data as web


# symb = ['YHOO','GOOG']
symb = ['YHOO']
# df = web.DataReader('YHOO','google','2010-01-01','2015-01-01')
# df2 = web.DataReader('GOOG','google','2010-01-01','2015-01-01')

df = web.get_data_google(symb, '2010-01-01','2011-01-01')['Close']

# coint, pvalue, _ = coint(df.YHOO,df.GOOG)

# print((coint, pvalue))
#
# fig, ax1 = plt.subplots()
# ax1.plot(df.YHOO, 'r')
# ax2 = ax1.twinx()
# ax2.plot(df.GOOG, 'b')
# fig.tight_layout()
# plt.show()
# # if __name__ == '__main__':
df['return'] = np.log(df['YHOO']/df['YHOO'].shift(1))
# df.dropna(inplace=True) #elimina toda fila con NA
df.fillna(0,inplace=True) #rellena los NA por 0
mu = df['return'].mean() * 252
sigma = df['return'].std()*252**0.5
# print(df['return'])
kc = mu / sigma**2 #Kelly criterio
# print(mu,sigma, kc)

print(df.ix[1])



