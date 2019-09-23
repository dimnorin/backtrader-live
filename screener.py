from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging, sys, multiprocessing
import backtrader as bt

from itertools import product, repeat
from utils.dump import Dump
from utils.log import Logger
import utils.util as utils


#  Binance assets
assets = {
    # 'USDT': ["ETH","BNB","LTC","EOS","XRP"],
    'USDT': ["ETH","BNB","LTC","EOS","XRP","USDC","ETC","WIN","TRX","PAX","LINK","BTT","ADA","TUSD","ALGO","FTM","ONT","PERL","MATIC","QTUM","DUSK","NEO","ATOM","HOT","FET","ICX","XLM","ONE","COS","BAT","WAN","COCOS","ERD","XMR","CELR","VET","IOST","IOTA","ZEC","ZIL","OMG","TOMO","WAVES","THETA","ENJ","DOGE","TFUEL","NULS","ANKR","DENT","NANO","MITH","ZRX","NPXS","MTL","FUN","DOCK","ONG","USDS","GTO","CVC","MFT","KEY","STORM"],
    # 'BTC': ["ETH","BNB","FTM","XRP","INS","LTC","EOS","BCHABC","WAN","LINK","REN","ADA","PERL","DUSK","MATIC","ALGO","XMR","ETC","TRX","ONE","COS","ATOM","ICX","RVN","BAT","QTUM","STRAT","WAVES","MTH","WTC","GNT","OAX","NEO","HOT","ENJ","XLM","ERD","DOCK","MTL","ONT","AGI","TOMO","AE","DASH","HC","CELR","NAS","FET","VET","COCOS","THETA","ZIL","ZEC","BTT","NANO","ANKR","MCO","FUN","IOTA","CDT","EVX","QKC","TFUEL","LSK","AION","PHB","REP","NULS","XEM","WABI","ARN","DENT","BTG","OMG","SNT","LOOM","MANA","POE","ONG","IOST","APPC","GXS","CVC","MITH","DOGE","ZRX","VIB","KMD","ELF","CMT","NEBL","ZEN","VIBE","DLT","GO","XVG","RCN","MDA","BCPT","OST","BTS","TNT","SNM","FUEL","GVT","SKY","BQX","BCD","EDO","DCR","REQ","WIN","DATA","STEEM","BRD","AST","NXS","PPT","GRS","MFT","GTO","LRC","ARK","QSP","XZC","AMB","KNC","LEND","ENG","RLC","NPXS","DNT","POWR","ADX","STORJ","WPR","BLZ","QLC","POLY","SYS","ARDR","IOTX","TNB","CND","DGD","VIA","LUN","NAV","PIVX","GAS","SC","RDN","YOYO","BNT","POA","SNGLS","KEY","NCASH","STORM","BTCB"],
    # 'BNB': ["LTC","XRP","PERL","EOS","TRX","ADA","FTM","WAN","RVN","REN","ETC","ALGO","NEO","ATOM","MATIC","XMR","COS","BTT","ONE","WAVES","DUSK","HOT","ICX","COCOS","BAT","ENJ","ERD","THETA","CELR","VET","XLM","QTUM","WTC","NANO","ZIL","ONT","FET","IOTA","DOGE","TOMO","DASH","ZEC","GNT","ANKR","AGI","","MITH","BRD","TFUEL","ZRX","MFT","SKY","GO","REP","LSK","QSP","PHB","DCR","MCO","OMG","ZEN","XEM","NULS","SC","","WABI","RCN","OST","BTS","CMT","STORM","DLT","QLC","LOOM","BCPT","NAS","","APPC","AION","POWR","SYS","POLY","XZC","ONG","","NCASH","","RDN","NXS","STEEM","NEBL","AMB","POA","GTO","CND","PIVX","ARDR","NAV","VIA","ADX","YOYO","YOYO"]
}

tfs_data = ['1m']
tfs_ind = ['5m', '15m', '30m', '1h']
hist_days = 3

class Screener:
    def __init__(self, logger):
        self._logger = logger
        self.results = {}
        self._pool = multiprocessing.Pool(multiprocessing.cpu_count())

    def runAll(self, strat_file_name):
        for base in assets.keys():
            coins = []
            for asset in assets.get(base):
                coin = '%s/%s' % (asset, base)
                coins.append(coin)
                # for i, tf_data in enumerate(tfs_min):
                #     for tf_ind in tfs_min[i:]:
            try:
                # result = self._iterate(coin, tf_data, tf_ind)
                results = self._pool.starmap(Screener._iterate, product([strat_file_name], coins, tfs_ind))
                dic = dict((x, y) for x, y in results)
                self.results = {**self.results, **dic}
                # self.results.setdefault(result, []).append('%s, tf_data=%s, tf_ind=%s' % (coin, tf_data,tf_ind))
            except Exception as e:
                self._logger.error(e)

            ret = ''
            ret += base + '\n'
            ret += str(self._sort(self.results, None)) + '\n\n'
        return ret

    def runQuickOnCoins(self, strat_file_name, tf_data:str='15m', tf_ind:str='15m'):
        for base in assets.keys():
            coins = []
            for asset in assets.get(base):
                coin = '%s/%s' % (asset, base)
                coins.append(coin)

            try:
                # result = self._iterate(coin, tf_data, tf_ind)
                results = self._pool.starmap(Screener._iterate, product([strat_file_name], coins, [tf_ind]))
                # self.results.setdefault(result, []).append('%s, tf_data=%s, tf_ind=%s' % (coin, tf_data,tf_ind))
                dic = dict((x, y) for x, y in results)
                self.results = {**self.results, **dic}
            except Exception as e:
                self._logger.error(e)

            ret = ''
            ret += base + '\n'
            ret += str(self._sort(self.results, None)) + '\n\n'
            self.results = {}

        return ret

    def runQuickOnTimeframes(self, strat_file_name, coin):
        # for i, tf_data in enumerate(tfs_min):
        #     for tf_ind in tfs_min[i:]:
        try:
            # result = self._iterate(coin, tf_data, tf_ind)
            # self.results.setdefault(result, []).append('%s, tf_data=%s, tf_ind=%s' % (coin, tf_data, tf_ind))

            results = self._pool.starmap(Screener._iterate, product([strat_file_name],[coin], tfs_ind))
            dic = dict((x, y) for x, y in results)
            self.results = {**self.results, **dic}
        except Exception as e:
            self._logger.error(e)

        ret = coin + '\n'
        ret += str(self._sort(self.results, None)) + '\n\n'
        self.results = {}
        return ret

    @staticmethod
    def _iterate(strat_file_name, coin, tf_ind:str='15m'):
        try:
            strat_class = utils.import_file('strategy', strat_file_name + '.py')
            # Create a cerebro entity
            # cerebro = bt.Cerebro(cheat_on_open=True)
            cerebro = bt.Cerebro()

            logger = Logger(logging.INFO, sys.stdout)
            # Add a strategy
            # cerebro.addstrategy(LiveBBStrategy, is_live=False)
            cerebro.addstrategy(strat_class, is_live=False)

            # Create a Data Feed
            dump = Dump('binance', coin)
            df = dump.get_data(tf_ind, hist_days)
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)

            df = dump.get_data('1m', hist_days)
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)
            # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=tf_ind)

            # Set our desired cash start
            cerebro.broker.setcash(1000.0)

            # Add a FixedSize sizer according to the stake
            cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

            # Set the commission
            cerebro.broker.setcommission(commission=0.001)

            # cerebro.addobserver(bt.observers.DrawDown)
            # Print out the starting conditions
            # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

            # Run over everything
            strat = cerebro.run(maxcpus=1)

            res = int(strat[0].broker.getvalue())
            ret = (res, '%s, tf_ind=%s' % (coin, tf_ind))
            print(ret)
            return ret
        except Exception as e:
            logger.error(e)
            print(e)
            return (0, str(e))

        # Print out the final result
        # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    def _sort(self, dic, from_top=5):
        sorted_results = sorted(dic.keys(), reverse=True)
        if from_top:
            sorted_results = sorted_results[:from_top]
        return dict((r, self.results[r]) for r in sorted_results)

if __name__ == '__main__':
    screener = Screener(Logger(logging.INFO, sys.stdout))
    # ret = screener.runQuickOnTimeframes('strat_super', 'ATOM/USDT')
    ret = screener.runQuickOnCoins('strat_super', tf_ind='15m')
    # ret = screener.runAll()
    print(ret)