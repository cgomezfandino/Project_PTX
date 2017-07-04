import pandas as pd
import quandl as q
import matplotlib.pyplot as plt

a = 2 * 2

d = q.get('BCHAIN/MKPRU')
d['SMA'] = d['Value'].rolling(100).mean()
d[d.index > '2013-1-1'].plot(title='BTC/USD exchange rate',figsize=(10, 6))
plt.show() # To show the graph