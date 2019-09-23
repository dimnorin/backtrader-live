from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import math

from indicators.extended_func import VWMA, DEMA, TEMA, LAGMA, SSMA

class DualMARibbons(bt.Indicator):
    lines = ('variant',)

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
    )

    params = (
         # Fast Ribbon MAs
         # Lower MA - type, length
        ('typeF1', "HullMA"), # "SMA", "EMA", "WMA", "VWMA", "SMMA", "DEMA", "TEMA", "LAGMA", "HullMA", "ZEMA", "TMA", "SSMA"
        ('lenF1', 5), # FAST Ribbon Lower MA Length
        # Upper MA - type, length
        ('lenF11', 5),  # FAST Ribbon Upper Length
        # Slow Ribbon MAs
        # Lower MA - type, length
        ('typeS1', bt.indicators.EMA),  # "SMA", "EMA", "WMA", "VWMA", "SMMA", "DEMA", "TEMA", "LAGMA", "HullMA", "ZEMA", "TMA", "SSMA"
        ('lenS1', 28),  # SLOW Ribbon Lower MA Length
        # Upper MA - type, length
        ('lenS16', 72),  # SLOW Ribbon Upper Length
    )

    def __init__(self):
        super(DualMARibbons, self).__init__()

        typeF1 = self.p.typeF1
        gammaF1 = 0.33 # Fast MA - Gamma for LAGMA
        typeF11 = typeF1
        gammaF11 = 0.77 # Slow MA - Gamma for LAGMA
        typeS1 = self.p.typeS1
        gammaS1 = gammaF1
        typeS16 = typeS1
        gammaS16 = gammaF11

        src = self.data.close

        # Fast MA Ribbon
        emaF1 = self.variant(typeF1, src, self.p.lenF1, gammaF1)
        emaF11 = self.variant(typeF11, src, self.p.lenF11, gammaF11)
        emafast = (emaF1 + emaF11) / 2 # Average of Upper and Lower MAs

        # Slow MA Ribbon
        emaS1 = self.variant(typeS1, src, self.lenS1, gammaS1)
        emaS16 = self.variant(typeS16, src, self.lenS16, gammaS16)
        emaslow = (emaS1 + emaS16) / 2 # Average of Upper and Lower MAs

    def variant(self, type):
        switcher = {
            "EMA": lambda src, len: bt.indicators.EMA(src, period=len),
            "WMA": lambda src, len: bt.indicators.WMA(src, period=len),
            "VWMA": lambda src, len: VWMA(src, period=len),
            "SMMA": lambda src, len: bt.indicators.SMMA(src, period=len),
            "DEMA": lambda src, len: DEMA(src, period=len),
            "TEMA": lambda src, len: TEMA(src, period=len),
            "LAGMA": lambda src, g: LAGMA(src, g=g),
            "HullMA": lambda src, len: bt.indicators.HullMA(src, period=len),
            "SSMA": lambda src, len: SSMA(src, period=len),
            "ZEMA": lambda src, len: bt.indicators.ZLEMA(src, period=len),
            "TMA":  lambda src, len: bt.indicators.SMA(bt.indicators.SMA(src, period=len), period=len)
        }
        return switcher.get(type, lambda src, len: bt.indicators.SMA(src, period=len))

