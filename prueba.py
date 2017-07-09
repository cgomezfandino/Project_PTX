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

import mmtm_strt_GoogFinance.Momentu

a = Momentum_Strat('AAPL', '2010-1-1', '2016-10-31')

print a.momentum_strategy()