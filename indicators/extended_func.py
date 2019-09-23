from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import functools
import math
import operator
import backtrader as bt

from backtrader.indicators import Indicator, MovingAverageBase, MovAv
from backtrader.indicators.basicops import BaseApplyN, PeriodN

class Exponent(BaseApplyN):
    alias = ('Exp','exp')
    lines = ('exp',)
    params = (
        ('func', lambda d: math.exp(x for x in d)),
    )

class Cos(BaseApplyN):
    alias = ('cos')
    lines = ('cos',)
    params = (
        ('func', lambda d: math.cos(x for x in d)),
    )

class NZ(BaseApplyN):
    alias = ('nz')
    lines = ('nz',)
    params = (
        # ('func', lambda d: [x if x else 0 for x in d]),
    )

class SuperSmoother(MovingAverageBase):
    '''
    SuperSmoother filter
    © 2013  John F. Ehlers
    '''
    alias = ('SSMA',)
    lines = ('ssma',)

    def __init__(self):
        self.len = self.p.period

        a0 = 1.414 * math.pi / self.len
        a1 = pow(math.e, -a0)
        b1 = 2 * a1 * math.cos(a0)
        c2 = b1
        c3 = (-a1) * a1
        self.c1 = 1 - c2 - c3
        self.c2 = c2
        self.c3 = c3

        super(SuperSmoother, self).__init__()

    def next(self):
        self.lines.ssma[0] = self.c1 * (self.data(0) + self.data(-1)) / 2

    def once(self, start, end):
        for i in range(start, end):
            self.lines.ssma[i] = self.c1 * (self.data[i] + self.data[i-1]) / 2
            if not math.isnan(self.lines.ssma[i-1]):
                self.lines.ssma[i] += self.c2 * self.lines.ssma[i-1]
            if not math.isnan(self.lines.ssma[i-2]):
                self.lines.ssma[i] += self.c3 * self.lines.ssma[i-2]


class Doubleema(MovingAverageBase):
    alias = ('DEMA',)
    lines = ('dema',)

    def __init__(self):
        src = self.data
        len = self.p.period
        ema1 = bt.indicators.EMA(src, period=len)
        ema2 = bt.indicators.EMA(ema1, period=len)
        self.lines.dema = 2 * (ema1 - ema2) + ema2

        super(Doubleema, self).__init__()


class Tripleema(MovingAverageBase):
    alias = ('TEMA',)
    lines = ('tema',)

    def __init__(self):
        src = self.data
        len = self.p.period
        ema1 = bt.indicators.EMA(src, period=len)
        ema2 = bt.indicators.EMA(ema1, period=len)
        ema3 = bt.indicators.EMA(ema2, period=len)
        self.lines.tema = 3 * (ema1 - ema2) + ema3

        super(Tripleema, self).__init__()


class Laguerre(MovingAverageBase):
    alias = ('LAGMA',)
    lines = ('lagma','L0', 'L1', 'L2', 'L3')
    plotlines = dict(
        lagma=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        L1=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        L2=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        L3=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        L0=dict(marker='v', markersize=4.0, color='red',
                         fillstyle='full', ls='-'),
    )
    params = (
        ('g', 0),
    )

    def prenext(self):
        self.lines.L0[0] = 0
        self.lines.L1[0] = 0
        self.lines.L2[0] = 0
        self.lines.L3[0] = 0

    def next(self):
        src = self.data
        g = self.p.g

        self.lines.L0 = (1 - g) * src + g * self.lines.L0(-1)
        self.lines.L1 = -g * self.lines.L0 + self.lines.L0(-1) + g * self.lines.L1(-1)
        self.lines.L2 = -g * self.lines.L1 + self.lines.L1(-1) + g * self.lines.L2(-1)
        self.lines.L3 = -g * self.lines.L2 + self.lines.L2(-1) + g * self.lines.L3(-1)
        # self.lines.lagma = (self.lines.L0 + 2 * self.lines.L1 + 2 * self.lines.L2 + self.lines.L3) / 6


class VolumeWeightedMovingAverage(MovingAverageBase):
    plotinfo = dict(subplot=False)

    alias = ('VWMA', )
    lines = ('VWMA', )
    plotlines = dict(VWMA=dict(alpha=0.50, linestyle='-.', linewidth=2.0))



    def __init__(self):
        # VWMA (VWMA – Volume-WEIGHTED MOVING AVERAGE) - ВЗВЕШЕННАЯ по объему СКОЛЬЗЯЩАЯ СРЕДНЯЯ
        cumvol = bt.ind.SumN(self.data.volume, period = self.p.period)
        typprice = ((self.data.close + self.data.high + self.data.low)/3) * self.data.volume
        cumtypprice = bt.ind.SumN(typprice, period=self.p.period)
        self.lines[0] = cumtypprice / cumvol

        super(VolumeWeightedMovingAverage, self).__init__()