import numpy as np
import pandas as pd

import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
from pandas.core import datetools

from pandas_datareader import data as web


symb = ['YHOO','GOOG']

# df = web.DataReader('YHOO','google','2010-01-01','2015-01-01')
# df2 = web.DataReader('GOOG','google','2010-01-01','2015-01-01')

df = web.get_data_google(symb)['Close']

coint, pvalue, _ = coint(df.YHOO,df.GOOG)

print((coint, pvalue))

fig, ax1 = plt.subplots()
ax1.plot(df.YHOO, 'r')
# ax2 = ax1.twinx()
# ax2.plot(df.GOOG, 'b')
# fig.tight_layout()
plt.show()
print df