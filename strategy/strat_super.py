#!/usr/bin/env python3

import backtrader as bt
from strategy.abs_strat import AbstractLiveStrategy

from indicators.ind_supertrend import SuperTrend


class LiveSuperStrategy(AbstractLiveStrategy):
    params = dict(
        stperiod=7,
        vaperiod=20,
        mult=1.5,
        af=0.2,
        afmax=0.2,
    )

    def _init_indicators(self):
        self.sig = SuperTrend(self.data, period = self.p.stperiod, mult=self.p.mult)
        # self.psar = bt.ind.ParabolicSAR(af=self.p.af, afmax=self.p.afmax)
        # Volume Average
        # self.va = bt.ind.SumN(self.data.volume, period=self.p.vaperiod) / self.p.vaperiod
        self.va = bt.ind.Average(self.data.volume, period=self.p.vaperiod)

    def _is_buy(self):
        is_buy = self.sig.l.signal[0] > 0 and self.sig.l.signal[-1] < 0 \
                    and self.data.volume[0] > self.va[0]
                    # and self.psar[0] < self.data.low[0]
        self.log('_is_buy >> ' + str({'close0':self.data.close[0],'signal0': self.sig.l.signal[0], 'signal-1': self.sig.l.signal[-1], 'vol0': self.data.volume[0], 'va0': self.va[0],
                      'low0': self.data.low[0], 'is_buy': is_buy}))
        return is_buy

    def _is_fire_stop_loss(self):
        is_fire = self.sig.l.signal[0] < 0 and self.sig.l.signal[-1] > 0
        self.log('_is_fire_stop_loss >> ' + str({'close0':self.data.close[0],'signal0': self.sig.l.signal[0], 'signal-1': self.sig.l.signal[-1],
                      'is_fire': is_fire}))
        return is_fire
