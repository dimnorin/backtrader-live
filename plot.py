from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging, sys, multiprocessing
# Import the backtrader platform
import backtrader as bt

import itertools
from itertools import product, repeat, starmap
from collections import namedtuple
from utils.dump import Dump
from strategy.strat_super import LiveSuperStrategy
from utils.log import Logger
import utils.util as utils

hist_days = 7
results = {}

class Plot:
    def __init__(self, logger=None):
        self._logger = logger

    def run(self, strat_file_name, coin, tf):
        kwargs = {
            'strat_super': self.kwargs_super,
            'strat_bb': self.kwargs_bb,
            'strat_ma': self.kwargs_ma,
            'strat_klinger': self.strat_klinger,
        }

        Plot._run(strat_file_name, coin, tf, kwargs[strat_file_name]())

    def kwargs_super(self):
        return {"stperiod": 8, "mult": 1.4, 'vaperiod': 16}

    def kwargs_bb(self):
        return {'bbperiod': 77}

    def kwargs_ma(self):
        return {'maperiod': 9, 'smaperiod': 4, 'vaperiod': 26,}

    def strat_klinger(self):
        return {'kvoFast':34, 'kvoSlow':55, 'sigPeriod':13,}

    @staticmethod
    def _run(strat_file_name, coin, tf, kwargs):
    # def _run(*args):
        try:
            # strat_file_name, coin, tf, kwargs = args
            strat_class = utils.import_file('strategy', strat_file_name + '.py')
            cerebro = bt.Cerebro()

            logger = Logger(logging.INFO, sys.stdout)
            kwargs['is_live'] = False
            cerebro.addstrategy(strat_class, **kwargs)

            # Create a Data Feed
            dump = Dump('binance', coin)
            df = dump.get_data(tf, hist_days)
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)

            df = dump.get_data('1m', hist_days)
            data = bt.feeds.PandasData(dataname=df)
            # cerebro.adddata(data)

            # Set our desired cash start
            cerebro.broker.setcash(1000.0)

            # Add a FixedSize sizer according to the stake
            cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

            # Set the commission
            cerebro.broker.setcommission(commission=0.001)

            # Run over everything
            strat = cerebro.run(maxcpus=1)

            # Print out the final result
            print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

            # Plot the result
            cerebro.plot()
        except Exception as e:
            logger.error(e)
            print(e)


if __name__ == '__main__':
    p = Plot()
    p.run('strat_klinger', 'XRP/USDT', '15m')
