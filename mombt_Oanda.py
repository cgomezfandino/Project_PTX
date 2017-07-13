__author__ = 'cgomezfandino@gmail.com'

import datetime as dt
import v20
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create an object config
config = ConfigParser()
# Read the config
config.read("pyalgo.cfg")

class Momentum_Backtester(object):

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
    def __init__(self, symbol, start, end, amount = 10000, tc = 0.000, sufix = '.000000000Z', timeFrame = 'H4', price = 'A'):


        self.symbol = symbol # EUR_USD
        # self.start = start
        # self.end = end
        self.amount = amount
        self.tc = tc
        self.suffix = sufix
        self.timeFrame = timeFrame
        self.price = price
        self.start = dt.datetime.combine(pd.to_datetime(start), dt.time(9,00))
        self.end = dt.datetime.combine(pd.to_datetime(end), dt.time(16,00))
        # This string suffix is needed to conform to the Oanda API requirements regarding start and end times.
        self.fromTime = self.start.isoformat('T') + self.suffix
        self.toTime = self.end.isoformat('T') + self.suffix
        self.results = None


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
        asset['position'] = np.sign(asset['returns'].rolling(momentum).mean())
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





        # return asset['strategy'][trades]
        # return {'Momentum Strategy - %s'%self.symbol:{'Results':{'strategy':{'Returns':np.round(asset['cstrategy'].sum(),3),
        #                                                                      'Anual_Return':asset['cstrategy'].mean() * 252,
        #                                                                      'Anual_Desv': asset['cstrategy'].std() * 252 ** 0.5,
        #                                                                      'Drawdown':asset['ddstrategy'].max(),
        #                                                                      'Sharpe_Ratio':''},
        #                                                          'Buy and Hold':{'Returns':asset['creturns'].sum(),
        #                                                                      'Anual_Return':asset['creturns'].mean() * 252,
        #                                                                      'Anual_Desv': asset['creturns'].std() * 252 ** 0.5,
        #                                                                      'Drawdown':asset['ddreturns'].max(),
        #                                                                      'Sharpe_Ratio':''}}}}

        #return(asset)

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



    # def strat_drawdown(self):
    #
    #     self.results = self.run_strategy()
    #
    #     if self.results is None:
    #         print("Not results to plot yet. Run a strategy.!")
    #     #
    #     # else:
    #     return(self.results['ddstrategy_c'].max())


    def plot_strategy(self):

        #self.results = self.run_strategy()

        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = 'Momentum Backtesting - %s ' % (self.symbol)
        self.results[['creturns_c', 'cstrategy_c']].plot(title=title, figsize=(10, 6))
        # self.results[['creturns_p', 'cstrategy_p']].plot(title=title, figsize=(10, 6))
        plt.show()


if __name__ == '__main__':
    mombt = Momentum_Backtester('EUR_USD', start='2010-01-01', end='2015-01-01')
    print(mombt.run_strategy())
    # print(mombt.strat_drawdown())
    print(mombt.plot_strategy())

