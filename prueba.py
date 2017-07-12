import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
import datetime as dt

# fromTime_2 = dt.datetime(2016, 12, 8, 8, 0, 0)
fromTime = '2016-12-08'

fromTime = dt.datetime.combine(pd.to_datetime(fromTime), dt.time(10,23))
print fromTime
#
# suffix = '.000000000Z'
#
# fromTime = fromTime.isoformat('T') + suffix
# fromTime_2 = fromTime_2.isoformat('T') + suffix
# print fromTime
# print fromTime_2

# print(dt.datetime.combine(dt.date(2011, 01, 01), dt.time(10, 23)))

