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

class Optimizer:
    def __init__(self, logger=None):
        self._logger = logger
        self.results = {}
        self._pool = multiprocessing.Pool(multiprocessing.cpu_count())

    def run(self, strat_file_name, coin, tf):
        kwargs = {
            'strat_super': self.kwargs_super,
            'strat_bb': self.kwargs_bb,
            'strat_ma': self.kwargs_ma,
        }

        try:
            options = kwargs[strat_file_name]()
            keys,values = options.keys(), options.values()
            opts = [dict(zip(keys, items)) for items in itertools.product(*values)]
            # print(opts)

            kwargs_iter = opts
            args_for_starmap = zip(repeat(strat_file_name), repeat(coin), repeat(tf), kwargs_iter)
            results = self._pool.starmap(Optimizer._iterate, args_for_starmap)
            dic = dict((x, y) for x, y in results)
            self.results = {**self.results, **dic}
        except Exception as e:
            self._logger.error(e)

        ret = coin + '\n'
        ret += str(utils.sort(self.results)) + '\n\n'
        self.results = {}
        utils.beep()
        return ret


    def kwargs_super(self):
        # stperiod = [x * 0.2 + 6 for x in range(1, 10)]
        stperiod = [8]
        # mult = [x * 0.1 + 1 for x in range(1, 10)]
        mult = [1.4]
        vaperiod = [x for x in range(1,100,5)]

        return {"stperiod": stperiod, "mult": mult, 'vaperiod': vaperiod}

    def kwargs_bb(self):
        bbperiod = [x for x in range(1,100,5)]
        return {'bbperiod': bbperiod}

    def kwargs_ma(self):
        maperiod = range(1, 20, 2)
        # maperiod = [9]
        smaperiod = range(1, 20, 2)
        # smaperiod = [4]
        vaperiod = [x for x in range(1, 100, 5)]

        return {'maperiod': maperiod, 'smaperiod': smaperiod, 'vaperiod': vaperiod}

    @staticmethod
    # def _iterate(strat_file_name, coin, tf, **kwargs):
    def _iterate(*args):
        try:
            strat_file_name, coin, tf, kwargs = args
            # coin = args[1]
            # tf = args[2]
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
            cerebro.adddata(data)

            # Set our desired cash start
            cerebro.broker.setcash(1000.0)

            # Add a FixedSize sizer according to the stake
            cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

            # Set the commission
            cerebro.broker.setcommission(commission=0.001)

            # Run over everything
            strat = cerebro.run(maxcpus=1)

            res = int(strat[0].broker.getvalue())
            # ret = (res, '%s, coin=%s, tf=%s, stperiod=%s, mult=%s' % (res, coin, tf, kwargs['stperiod'], kwargs['mult']))
            ret = (res, '%s, %s, %s' % (res, ', '.join(args[:-1]), str(kwargs)))
            print(ret)
            return ret
        except Exception as e:
            logger.error(e)
            print(e)
            return (0, str(e))


if __name__ == '__main__':
    o = Optimizer()
    ret = o.run('strat_ma', 'XRP/USDT', '15m')
    print(ret)
