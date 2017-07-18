__author__ = 'cgomezfandino@gmail.com'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as web
import seaborn

class MRBT_Backtester(object):

    ''' Momentum backtesting strategy:
    Attributes
    ==========
    symbol: str
        Google Finance symbol with which to work with
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    amount: int, float
        amount to be invested at the beginning
    tc: float
        proportional transaction costs (e.g. 0.3% = 0.003) per trade

    Methods
    =========
    get_data:
        retrieves and prepares the base data set
    run_strategy:
        runs the backtest for the momentum-based strategy
    plot_strategy:
        plots the performance of the strategy compared to the symbol
    '''
    def __init__(self, symbol, start, end, amount=10000, tc=0.001, data_src='google'):

        self.symbol = symbol
        self.start = start
        self.end = end
        self.amount = amount
        self.tc = tc
        # price = OHLC
        self.data_source = data_src
        self.get_data()
        self.results = None

    def get_data(self):

        data = web.DataReader(name=self.symbol, data_source=self.data_source, start=self.start, end=self.end)
        ## Asset Returns
        data['returns'] = np.log(data['Close']/data['Close'].shift(1))
        self.asset = data

    def run_strategy(self, SMA, threshold):
        '''

        :param SMA:
        :param threshold:
        :return:
        '''

        asset = self.asset.copy()
        self.SMA = SMA
        self.threshold = threshold
        # self.str_rtrn = ['returns']
        # self.drawdown = []
        #self.cumrent = []


        asset['sma'] = asset['Close'].rolling(self.SMA).mean()
        asset['distance'] = asset['Close'] - asset['sma']

        ## Position
        asset['position'] = np.where(asset['distance'] > self.threshold, -1, np.nan)
        asset['position'] = np.where(asset['distance'] < self.threshold, 1, asset['position'])
        asset['position'] = np.where(asset['distance'] * asset['distance'].shift(1) < 0, 0, asset['position'])
        ## Fill al na for 0
        asset['position'] = asset['position'].ffill().fillna(0)

        asset['strategy'] = asset['position'].shift(1) * asset['returns']

        ## determinate when a trade takes places (long or short)
        trades = asset['position'].diff().fillna(0) != 0

        ## subtracting transaction cost from return when trade takes place
        asset['strategy'][trades] -= self.tc

        ## Cumulative returns in Cash
        asset['creturns_c'] = self.amount * asset['returns'].cumsum().apply(np.exp)
        asset['cstrategy_c'] = self.amount * asset['strategy'].cumsum().apply(np.exp)

        ## Cumulative returns in percentage
        asset['creturns_p'] = asset['returns'].cumsum().apply(np.exp)
        asset['cstrategy_p'] = asset['strategy'].cumsum().apply(np.exp)

        ## Max Cummulative returns in cash
        asset['cmreturns_c'] = asset['creturns_c'].cummax()
        asset['cmstrategy_c'] = asset['cstrategy_c'].cummax()

        ## Max Cummulative returns in percentage
        asset['cmreturns_p'] = asset['creturns_p'].cummax()
        asset['cmstrategy_p'] = asset['cstrategy_p'].cummax()


        ## Max Drawdown un Cash
        asset['ddreturns_c'] = asset['cmreturns_c'] - asset['creturns_c']
        asset['ddstrategy_c'] = asset['cmstrategy_c'] - asset['cstrategy_c']

        ## Max Drawdown in Percentage
        asset['ddreturns_p'] = asset['cmreturns_p'] - asset['creturns_p']
        asset['ddstrategy_p'] = asset['cmstrategy_p'] - asset['cstrategy_p']

        ## save asset df into self.results
        self.results = asset

        ## Final calculations for return

        ## absolute Strategy performance in Cash:
        aperf_c = self.results['cstrategy_c'].ix[-1]
        ## absolute Strategy performance in Percentage:
        aperf_p = self.results['cstrategy_p'].ix[-1]
        ## Out-/underperformance Of strategy in Cash
        operf_c = aperf_c - self.results['creturns_c'].ix[-1]
        ## Out-/underperformance Of strategy in Percentage
        operf_p = aperf_p - self.results['creturns_p'].ix[-1]
        ## Maximum Drawdown in Cash
        mdd_c = self.results['ddstrategy_c'].max()
        ## Maximum Drawdown in Percentage
        mdd_p = self.results['ddstrategy_p'].max()

        return np.round(aperf_c,2), round(aperf_p,2), round(operf_c,2), round(operf_p,3), mdd_c, mdd_p

    def plot_strategy(self):

        #self.results = self.run_strategy()

        if self.results is None:

            print('No results to plot yet. Run a strategy.')

        title = 'Mean Reverting Backtesting - %s ' % (self.symbol)
        self.results[['creturns_c', 'cstrategy_c']].plot(title=title, figsize=(10, 6))
        # self.results[['creturns_p', 'cstrategy_p']].plot(title=title, figsize=(10, 6))
        plt.show()

    def hist_returns(self):

        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        title = 'Histogram Returns - Mean Reverting Backtesting - %s ' % (self.symbol)
        self.results[['creturns_p','cstrategy_p']].plot.hist(title=title, figsize=(10, 6), alpha = 0.5, bins=30)
        # plt.hist(self.results['creturns_p'])
        plt.show()

    def plot_mr(self):

        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = 'Mean Reverting Backtesting - %s ' % (self.symbol)
        self.results[['distance']].plot(title=title, figsize=(10, 6))
        plt.axhline(self.threshold, color='r')
        plt.axhline(-self.threshold, color='r')
        plt.axhline(0, color='r')
        # self.results[['creturns_p', 'cstrategy_p']].plot(title=title, figsize=(10, 6))
        plt.show()



if __name__ == '__main__':
    mrbt = MRBT_Backtester('AAPL', '2010-1-1', '2016-10-31')
    print(mrbt.run_strategy(SMA=10,threshold=7))
    # print(mombt.strat_drawdown())
    print(mrbt.plot_strategy())
    print(mrbt.plot_mr())

