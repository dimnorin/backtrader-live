#!/usr/bin/env python3
import backtrader as bt

from indicators.ind_ma import MaExtension
from strategy.abs_strat import AbstractLiveStrategy


class LiveMaStrategy(AbstractLiveStrategy):
    params = dict(
        maperiod=7,
        smaperiod=24,
        vaperiod=20,
    )

    def _init_indicators(self):
        self.sig = MaExtension(self.data, maperiod=self.p.maperiod, smaperiod=self.p.smaperiod)
        # Volume Average
        self.va = bt.ind.Average(self.data.volume, period=self.p.vaperiod)

    def _is_buy(self):
        return self.sig.l.signal > 0 \
               and self.data.volume[0] > self.va[0]

    def _is_fire_stop_loss(self):
        return False
