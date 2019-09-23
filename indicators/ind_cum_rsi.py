import backtrader as bt

class CumulativeRSI(bt.Indicator):
    lines = ('cumrsi',)
    params = (('period', 14), ('count', 2),)
    alias = ('CumRSI',)

    def __init__(self):
        rsi = bt.ind.RSI(self.data, period=self.p.period)
        self.lines.cumrsi = bt.indicators.SumN(rsi, period=self.p.count)