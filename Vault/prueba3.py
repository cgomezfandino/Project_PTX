import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as web

symb = ['GOOG','YHOO']
df1 = web.DataReader(name = 'YHOO',data_source='google',start= '2015-01-01', end='2016-01-01')
df2 = web.DataReader(name = 'GOOG',data_source='google',start= '2015-01-01', end='2016-01-01')
df3 = pd.concat(df1['Close'],df2['Close'])
print(df3.head())