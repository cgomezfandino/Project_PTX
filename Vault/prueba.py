import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
import datetime as dt
import v20
from configparser import ConfigParser

# a = np.random.rand(100)
# print plt.hist(a)

__author__ = 'cgomezfandino@gmail.com'

import datetime as dt
import v20
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn

# Create an object config
config = ConfigParser()
# Read the config
config.read("pyalgo.cfg")

class Momentum_Backtester(object):

    ''' Momentum backtesting strategy:
    Attributes
    ==========
    symbol: str
        Oanda symbol with which to work with
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    amount: int, float
        amount to be invested at the beginning
    tc: float
        proportional transaction costs (e.g. 0.3% = 0.003) per trade
    sufix: str

    timeFrame:
        Candle TimeFrame

    Methods
    =========
    get_data:
        retrieves and prepares the base data set
    run_strategy:
        runs the backtest for the momentum-based strategy
    plot_strategy:
        plots the performance of the strategy compared to the symbol
    '''
    def __init__(self, symbol, start, end, amount = 10000, tc = 0.000, lvrage=1, sufix = '.000000000Z', timeFrame = 'H4', price = 'A'):

        '''

        symbol:
                SYmbol
        :param start:
        :param end:
        :param amount:
        :param tc:
        :param sufix:
        :param timeFrame:
        :param price:
        '''


        self.symbol = symbol # EUR_USD
        # self.start = start
        # self.end = end
        self.amount = amount
        self.tc = tc
        self.lvrage = lvrage
        self.suffix = sufix
        self.timeFrame = timeFrame
        self.price = price
        self.start = dt.datetime.combine(pd.to_datetime(start), dt.time(9,00))
        self.end = dt.datetime.combine(pd.to_datetime(end), dt.time(16,00))
        # This string suffix is needed to conform to the Oanda API requirements regarding start and end times.
        self.fromTime = self.start.isoformat('T') + self.suffix
        self.toTime = self.end.isoformat('T') + self.suffix
        self.results = None

        self.toplot_c = ['creturns_c']
        self.toplot_p = ['creturns_p']


        self.ctx = v20.Context(
            'api-fxpractice.oanda.com',
            443,
            True,
            application='sample_code',
            token=config['oanda_v20']['access_token'],
            datetime_format='RFC3339')
        self.get_data()

    def get_data(self):

        res = self.ctx.instrument.candles(
            instrument= self.symbol,
            fromTime= self.fromTime,
            toTime= self.toTime,
            granularity= self.timeFrame,
            price= self.price)

        # data.keys()

        raw = res.get('candles')

        raw = [cs.dict() for cs in raw]

        for cs in raw:
            cs.update(cs['ask'])
            del cs['ask']

        data = pd.DataFrame(raw)

        data['time'] = pd.to_datetime(data['time'], unit='ns')

        data = data.set_index('time')

        data.index = pd.DatetimeIndex(data.index)

        # print data.info()

        cols = ['c', 'l', 'h', 'o']

        data[cols] = data[cols].astype('float64')

        data.rename(columns={'c': 'CloseAsk', 'l': 'LowAsk',
                             'h': 'HighAsk', 'o': 'OpenAsk'}, inplace=True)

        data['returns'] = np.log(data['CloseAsk'] / data['CloseAsk'].shift(1))

        self.asset = data

    def run_strategy(self, momentum = 1):

        '''
        This function run a momentum backtest.

        :param momentum:
        ================
        Number of lags you want to to test for momuntum strategy

        :return:
        ================
        The backtest returns the following values:
        aperf_c: Absolute Strategy performance in Cash
        aperf_p: Absolute Strategy performance in Percentage
        operf_c: Out-/underperformance Of strategy in Cash
        operf_p: Out-/underperformance Of strategy in Percentage
        mdd_c: Maximum Drawdown in Cash
        mdd_p:Maximum Drawdown in Percentage
       '''

        asset = self.asset.copy()
        self.momentum = momentum
        # self.str_rtrn = ['returns']
        # self.drawdown = []
        #self.cumrent = []

        ## Position

        asset['creturns_c'] = self.amount * asset['returns'].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
        asset['creturns_p'] = asset['returns'].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
        asset['cmreturns_c'] = asset['creturns_c'].cummax()
        asset['cmreturns_p'] = asset['creturns_p'].cummax()
        asset['ddreturns_c'] = asset['cmreturns_c'] - asset['creturns_c']
        asset['ddreturns_p'] = asset['cmreturns_p'] - asset['creturns_p']

        for i in momentum:
            
            asset['position_%i' %i] = np.sign(asset['returns'].rolling(i).mean())
            asset['strategy_%i' %i] = asset['position_%i' %i].shift(1) * asset['returns']

            ## determinate when a trade takes places (long or short)
            trades = asset['position_%i' %i].diff().fillna(0) != 0

            ## subtracting transaction cost from return when trade takes place
            asset['strategy_%i' %i][trades] -= self.tc

            ## Cumulative returns in Cash
            asset['cstrategy_c_%i' %i] = self.amount * asset['strategy_%i' %i].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)

            ## Cumulative returns in percentage
            asset['cstrategy_p_%i' %i] = asset['strategy_%i' %i].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)

            ## Max Cummulative returns in cash
            asset['cmstrategy_c_%i' %i] = asset['cstrategy_c_%i' %i].cummax()

            ## Max Cummulative returns in percentage
            asset['cmstrategy_p_%i' %i] = asset['cstrategy_p_%i' %i].cummax()


            ## Max Drawdown un Cash
            asset['ddstrategy_c_%i' %i] = asset['cmstrategy_c_%i' %i] - asset['cstrategy_c_%i' %i]

            ## Max Drawdown in Percentage
            asset['ddstrategy_p_%i' %i] = asset['cmstrategy_p_%i' %i] - asset['cstrategy_p_%i' %i]

            self.toplot_c.append('cstrategy_c_%i' %i)

            ## save asset df into self.results
            self.results = asset

        ## Final calculations for return

        ## absolute Strategy performance in Cash:



        # aperf_c = self.results['cstrategy_c_%i' %i].ix[-1]
        # ## absolute Strategy performance in Percentage:
        # aperf_p = self.results['cstrategy_p_%i' %i].ix[-1]
        # ## Out-/underperformance Of strategy in Cash
        # operf_c = aperf_c - self.results['creturns_c_%i' %i].ix[-1]
        # ## Out-/underperformance Of strategy in Percentage
        # operf_p = aperf_p - self.results['creturns_p_i%' %i].ix[-1]
        # ## Maximum Drawdown in Cash
        # mdd_c = self.results['ddstrategy_c_%i' %i].max()
        # ## Maximum Drawdown in Percentage
        # mdd_p = self.results['ddstrategy_p_%i' %i].max()
        #
        # return np.round(aperf_c,2), round(aperf_p,2), round(operf_c,2), round(operf_p,3), mdd_c, mdd_p

    def plot_strategy(self):

        #self.results = self.run_strategy()

        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = 'Momentum Backtesting - %s ' % (self.symbol)
        # self.results[['creturns_c', 'cstrategy_c']].plot(title=title, figsize=(10, 6))
        self.results[self.toplot_c].plot(title=title, figsize=(10, 6))
        plt.show()

    def hist_returns(self):

        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        title = 'Histogram Returns - Momentum Backtesting - %s ' % (self.symbol)
        self.results[['creturns_p','cstrategy_p']].plot.hist(title=title, figsize=(10, 6), alpha = 0.5, bins=30)
        # plt.hist(self.results['creturns_p'])
        plt.show()



if __name__ == '__main__':
    mombt = Momentum_Backtester('EUR_USD', start='2015-12-08', end='2016-12-10',lvrage=10)
    print(mombt.run_strategy(momentum=[1,15,20]))
    # print(mombt.strat_drawdown())
    print(mombt.plot_strategy())
    # print(mombt.hist_returns())


# for i in range(1,10,1):
#     print('hola_%d' %i)
