import PTX_oandaInfo
import numpy as np
import pandas as pd
from pandas_datareader import data as web
import matplotlib.pyplot as plt
# import fix_yahoo_finance as yf
# yf.pdr_override() # <== that's all it takes :-)
# PTX_oandaInfo.account_ID()

# PTX_oandaInfo.get_instruments()


# -------------------------------------------------------------------------------
# class person():
#
#     def __init__(self, id):
#         self.id = id
#         print("class created")
#
#
#     def name_(self,first_name,last_name):
#         self.first_name = first_name
#         self.last_name = last_name
#
#     def print_name(self):
#         print(self.first_name, " ", self.last_name, self.id)

# nombres = person(10)
# nombres.name_('Carlos','Gomez')
# nombres.print_name()

# ---------------------------------------------------------------------------------

# x = range(1,10)
# x = pd.DataFrame(x)
# # print x
# print x.apply(lambda x: x*2)

# print np.exp(2)

#  a = 10
# print a

# ----------------------------------------------------------------------------------

# data = web.DataReader('GLD', data_source='yahoo',start='2010-01-01', end='2016-12-31')
# print data.head()


data = web.DataReader('SPY',data_source='google',start='2010-01-01', end='2016-12-31')#['Close']
data['retuns_1'] =  np.log(data['Close']/data['Close'].shift(1))
data['retuns_2'] =  data['Close']-data['Close'].shift(1)

# print data.head()
# cols = ['retuns_1','retuns_2']
# data['retuns_1'].plot()
# plt.title('porcentaje')
# data.retuns_2.hist(bins=30) # mostramos el histograma de los retornos en %
plt.show()
# data['retuns_2'].plot()
# plt.title('en cash')
# plt.show()
# print data.head()