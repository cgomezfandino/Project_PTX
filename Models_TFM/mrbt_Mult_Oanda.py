__author__ = 'cgomezfandino@gmail.com'

import datetime as dt
import v20
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Create an object config
config = ConfigParser()
# Read the config
config.read("../API_Connection_Oanda/pyalgo.cfg")

class MRBT_Backtester(object):

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
    def __init__(self, symbol, start, end, amount = 10000, tc = 0.000, lvrage =1 , sufix = '.000000000Z', timeFrame = 'H4', price = 'A'):

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
        self.colors = sns.hls_palette(14)

        self.toplot_c = ['creturns_c']
        self.toplot_p = ['creturns_p']
        self.toplot_hist = ['returns']


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

    def run_strategy(self, SMA, threshold_std = 1):

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
        self.SMA = SMA


        # self.str_rtrn = ['returns']
        # self.drawdown = []
        #self.cumrent = []


        # Cumulative returns without laverage
        asset['creturns_c'] = self.amount * asset['returns'].cumsum().apply(np.exp)
        asset['creturns_p'] = asset['returns'].cumsum().apply(np.exp)

        # Cumulative returns with laverage
        asset['lcreturns_c'] = self.amount * asset['returns'].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
        asset['lcreturns_p'] = asset['returns'].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
        asset['lcmreturns_c'] = asset['lcreturns_c'].cummax()
        asset['lcmreturns_p'] = asset['lcreturns_p'].cummax()
        asset['ddreturns_c'] = asset['lcmreturns_c'] - asset['lcreturns_c']
        asset['ddreturns_p'] = asset['lcmreturns_p'] - asset['lcreturns_p']

        dicti = {'Mean Reverting Strategies': {}}
        x = []
        y = []
        z = []

        for i in SMA:

            asset['sma_%i' %i] = asset['CloseAsk'].rolling(i).mean()
            asset['distance_%i' %i] = asset['CloseAsk'] - asset['sma_%i' %i]

            self.threshold = threshold_std * np.std(asset['distance_%i' %i])

            ## Position
            asset['position_%i' %i] = np.where(asset['distance_%i' %i] > self.threshold, -1, np.nan)
            asset['position_%i' %i] = np.where(asset['distance_%i' %i] < -self.threshold, 1, asset['position_%i' %i])
            asset['position_%i' %i] = np.where(asset['distance_%i' %i] * asset['distance_%i' %i].shift(1) < 0, 0, asset['position_%i' %i])
            ## Fill al na for 0
            asset['position_%i' %i] = asset['position_%i' %i].ffill().fillna(0)

            asset['strategy_%i' %i] = asset['position_%i' %i].shift(1) * asset['returns']

            ##
            asset['lstrategy_%i' % i] = asset['strategy_%i' % i] * self.lvrage
            self.toplot_hist.append('lstrategy_%i' % i)

            ## determinate when a trade takes places (long or short)
            trades = asset['position_%i' %i].diff().fillna(0) != 0

            ## subtracting transaction cost from return when trade takes place
            asset['lstrategy_%i' %i][trades] -= self.tc

            ## Cumulative returns in Cash
            # asset['cstrategy_c_%i' %i] = self.amount * asset['strategy_%i' %i].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
            asset['cstrategy_c_%i' % i] = self.amount * asset['lstrategy_%i' % i].cumsum().apply(np.exp)

            ## Cumulative returns in percentage
            # asset['cstrategy_p_%i' %i] = asset['strategy_%i' %i].cumsum().apply(lambda x: x * self.lvrage).apply(np.exp)
            asset['cstrategy_p_%i' % i] = asset['lstrategy_%i' % i].cumsum().apply(np.exp)

            ## Max Cummulative returns in cash
            asset['cmstrategy_c_%i' % i] = asset['cstrategy_c_%i' % i].cummax()

            ## Max Cummulative returns in percentage
            asset['cmstrategy_p_%i' % i] = asset['cstrategy_p_%i' % i].cummax()

            ## Max Drawdown un Cash
            asset['ddstrategy_c_%i' % i] = asset['cmstrategy_c_%i' % i] - asset['cstrategy_c_%i' % i]

            ## Max Drawdown in Percentage
            asset['ddstrategy_p_%i' % i] = asset['cmstrategy_p_%i' % i] - asset['cstrategy_p_%i' % i]


            ## Adding values that we wanna plot
            self.toplot_c.append('cstrategy_c_%i' % i)
            self.toplot_p.append('cstrategy_p_%i' % i)

            ## save asset df into self.results
            self.results = asset

            ## Final calculations for return

            ## absolute Strategy performance in Cash:
            aperf_c = self.results['cstrategy_c_%i' %i].ix[-1]
            ## absolute Strategy performance in Percentage:
            aperf_p = self.results['cstrategy_p_%i' %i].ix[-1]
            ## Out-/underperformance Of strategy in Cash
            operf_c = aperf_c - self.results['creturns_c'].ix[-1]
            ## Out-/underperformance Of strategy in Percentage
            operf_p = aperf_p - self.results['creturns_p'].ix[-1]

            ## Maximum Drawdown in Cash
            mdd_c = self.results['ddstrategy_c_%i' %i].max()
            ## Maximum Drawdown in Percentage
            mdd_p = self.results['ddstrategy_p_%i' %i].max()


            keys = ['aperf_c_%i' %i, 'aperf_p_%i' %i, 'operf_c_%i' %i, 'operf_p_%i' %i, 'mdd_c_%i' %i, 'mdd_p_%i' %i]
            values = ['%.2f' % np.round(aperf_c, 2), '%.2f' % np.round(aperf_p, 2), '%.2f' % np.round(operf_c, 2),
                      '%.2f' % np.round(operf_p, 2), '%.2f' % np.round(mdd_c, 2), '%.2f' % np.round(mdd_p, 2)]

            res = dict(zip(keys, values))

            dicti['Mean Reverting Strategies']['strategy_%i' %i] = res

            x.append(i)
            y.append(aperf_p)
            z.append(mdd_p)


        self.x = x  # SMA
        self.y = y  # final returns
        self.z = z  # mdd

        # return np.round(aperf_c,2), round(aperf_p,2), round(operf_c,2), round(operf_p,3), mdd_c, mdd_p
        return dicti

    def plot_strategy(self):

        #self.results = self.run_strategy()



        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = 'Mean Reverting Backtesting - %s \n %s ' % (self.symbol, self.timeFrame)
        # self.results[self.toplot_c].plot(title=title, figsize=(10, 6)) #Cash
        self.results[self.toplot_p].plot(title=title, figsize=(10, 6), color= self.colors) #Percentage
        plt.show()

    def hist_returns(self):

        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        title = 'Histogram Returns - Mean Reverting Backtesting - %s \n %s ' % (self.symbol, self.timeFrame)
        self.results[self.toplot_hist].plot.hist(title=title, color=self.colors, figsize=(10, 6), alpha = 0.5, bins=30) #in Cash
        # self.results[self.toplot_p].plot.hist(title=title, figsize=(10, 6), alpha = 0.5, bins=30) #in Percentage
        # plt.hist(self.results['creturns_p'])
        plt.show()

    # def plot_mr(self):
    #
    #     if self.results is None:
    #         print('No results to plot yet. Run a strategy.')
    #
    #     title = 'Mean Reverting (%i) Backtesting - %s ' % (self.SMA, self.symbol)
    #     self.results[['distance']].plot(title=title, figsize=(10, 6))
    #     plt.axhline(self.threshold, color='r')
    #     plt.axhline(-self.threshold, color='r')
    #     plt.axhline(0, color='r')
    #     # self.results[['creturns_p', 'cstrategy_p']].plot(title=title, figsize=(10, 6))
    #     plt.show()


    def plot_bstmr(self):

        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        title = 'All Mean Reverting Strategies Final Returns - %s \n %s ' % (self.symbol, self.timeFrame)

        # fig, ax1 = plt.subplots()
        # ax1.plot(self.x,self.y, 'b-', alpha = 0.5)
        # ax1.set_ylabel('Final Returns', color='b')
        # ax1.tick_params('y', colors='b')
        # ax2 = ax1.twinx()
        # ax2.plot(self.x,self.z, 'r--')
        # ax2.set_ylabel('Max.Drawdown', color='r')
        # ax2.tick_params('y', colors='r')
        # fig.tight_layout()
        # plt.legend()

        plt.plot(self.x, self.y, 'b-o', alpha = 0.5)
        plt.plot(self.x, self.z, 'r--o', alpha = 0.5)
        plt.title(title)
        plt.legend(['Final Returns', 'Maximum Drawdown'])
        plt.xlabel('Mean Reverting/SMA')
        plt.ylabel('Returns/MDD')
        plt.show()


if __name__ == '__main__':
    mrbt = MRBT_Backtester('EUR_USD', '2015-01-01', '2017-01-01', lvrage=10)
    print(mrbt.run_strategy(SMA=[x for x in range(20,220,20)],threshold_std= 1.5))
    mrbt.plot_strategy()
    # mrbt.plot_mr()
    mrbt.plot_bstmr()
    mrbt.hist_returns()
