__author__ = 'cgomezfandino@gmail.com'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as web


class Momentum_Strat(object):

    def __init__(self, activo=None, start=None, end=None, data_src='google'):

        self.symbol = activo
        self.start = start
        self.end = end
        # price = OHLC
        self.data_source = data_src
        self.get_data()
        self.results = None

    def get_data(self):

        data  = web.DataReader(name=self.symbol, data_source=self.data_source, start=self.start, end=self.end)#[price]
        self.asset = data

    def run_strategy(self, momentum = 1):

        # self.str_rtrn = ['returns']
        # self.drawdown = []

        self.momentum = momentum
        self.cumrent = []
        asset = self.asset.copy()


        # Asset Returns
        asset['returns'] = np.log(asset['Close']/asset['Close'].shift(1))

        # Position
        asset['position'] = np.sign(asset['returns'].rolling(momentum).mean())
        asset['strategy'] = asset['position'].shift(1) * asset['returns']

        # Cumulative returns
        asset['creturns'] = asset['returns'].cumsum().apply(np.exp)
        asset['cstrategy'] = asset['strategy'].cumsum().apply(np.exp)

        # Max Cummulative returns
        asset['cmreturns'] = asset['creturns'].cummax()
        asset['cmstrategy'] = asset['cstrategy'].cummax()

        asset['ddreturns'] = asset['cmreturns'] - asset['creturns']
        asset['ddstrategy'] = asset['cmstrategy'] - asset['cstrategy']

        self.results = asset

        return asset

        # for m in momentum:
        #     asset['position_%d' % m] = np.sign(asset['returns'].rolling(m).mean())
        #     asset['strategy_%d' % m] = asset['position_%d' % m].shift(1) * asset['returns']
        #     self.str_rtrn.append('strategy_%d' % m) #mirar si se lleva al self o no?

        # cumulative returns and max(cumulative return)
        # for dd in str_rtrn:
        #     # print dd
        #     asset['cumret_%s' % dd] = asset[dd].cumsum().apply(np.exp)
        #     asset['cummax_%s' % dd] = asset['cumret_%s' % dd].cummax()
        #     asset['drawdown_%s' % dd] = asset['cummax_%s' % dd] - activo['cumret_%s' % dd]
        #     self.drawdown.append('drawdown_%s' % dd)
        #     self.cumrent.append('cumret_%s' % dd)

        # return {'Strategy Yield:':self.results['strategy'].sum(),
        #         'Buy and Hold Yield:':self.results['returns'].sum(),
        #         'Strategy Drawdown':np.round(self.results['ddstrategy'].max(),3),
        #         'Hold Drawdown':np.round(self.results['ddreturns'].max(),3)}



    def strat_drawdown(self):

        self.results = self.run_strategy()

        if self.results is None:
            print("Not results to plot yet. Run a strategy.!")
        #
        # else:
        return self.results['ddstrategy'].max()


    def plot_strategy(self):

        self.results = self.run_strategy()

        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = '%s ' % (self.symbol)
        self.results[['creturns', 'cstrategy']].plot(title=title, figsize=(10, 6))
        plt.show()

if __name__ == '__main__':
    mm = Momentum_Strat('AAPL', '2010-1-1', '2016-10-31')
    # print mm.run_strategy()
    print mm.strat_drawdown()
    # print mm.plot_strategy()