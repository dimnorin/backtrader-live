#!/usr/bin/env python3

import backtrader as bt
from strategy.abs_strat import AbstractLiveStrategy

from indicators.ind_klinger_osc import KlingerOsc


class LiveSuperStrategy(AbstractLiveStrategy):
    params = dict(
        kvoFast=34,
        kvoSlow=55,
        sigPeriod=13,
        vaperiod=20,
    )

    def _init_indicators(self):
        klinger = KlingerOsc(self.data, kvoFast=self.p.kvoFast, kvoSlow=self.p.kvoSlow, sigPeriod=self.p.sigPeriod)
        self.kvo = klinger.l.kvo
        self.sig = klinger.l.sig
        # Volume Average
        self.va = bt.ind.SumN(self.data.volume, period=self.p.vaperiod) / self.p.vaperiod

    def _is_buy(self):
        is_buy = self.kvo[-1] < self.sig[-1] and self.kvo[0] > self.sig[0] \
                    and self.data.volume[0] > self.va[0]
        self.log('_is_buy >> ' + str({'close0':self.data.close[0], 'vol0': self.data.volume[0], 'va0': self.va[0],
                      'low0': self.data.low[0], 'is_buy': is_buy}))
        return is_buy

    def _is_fire_stop_loss(self):
        is_fire = self.kvo[-1] > self.sig[-1] and self.kvo[0] < self.sig[0]
        self.log('_is_fire_stop_loss >> ' + str({'close0':self.data.close[0],
                      'is_fire': is_fire}))
        return is_fire
