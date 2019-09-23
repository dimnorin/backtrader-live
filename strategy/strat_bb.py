#!/usr/bin/env python3

import backtrader as bt
from strategy.abs_strat import AbstractLiveStrategy


class LiveBBStrategy(AbstractLiveStrategy):
    params = dict(
        bbperiod=1,
    )

    def _init_indicators(self):
        self.bband = bt.indicators.BollingerBands(self.data, period=self.p.bbperiod)
        self.redline = None
        self.blueline = None

    def next(self):
        if self.data0.close[0] < self.bband.lines.bot[-1] and not self.position:
            self.redline = True

        if self.data.close[0] > self.bband.lines.top[-1] and self.position:
            self.blueline = True

        self.log('next >> ' + str({'close': self.data0.close[0], 'bot': self.bband.lines.bot[-1], 'top': self.bband.lines.top[-1],
             'redline': self.redline, 'blueline': self.blueline}))

        super().next()

    def _is_buy(self):
        is_buy = self.data0.close[0] > self.bband.lines.mid[-1] and self.redline \
                    or self.data0.close[0] > self.bband.lines.top[-1]
        self.log('_is_buy >> ' + str({'close': self.data0.close[0], 'mid': self.bband.lines.mid[-1], 'top': self.bband.lines.top[-1],
                      'redline': self.redline, 'is_buy': is_buy}))
        return is_buy

    def _is_fire_stop_loss(self):
        is_fire = self.data.close[0] < self.bband.lines.mid[-1] and self.blueline
        self.log('_is_fire_stop_loss >> ' + str({'close': self.data0.close[0], 'mid': self.bband.lines.mid[-1],
                      'blueline': self.blueline, 'is_fire': is_fire}))
        return is_fire
