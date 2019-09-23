import backtrader as bt


class MaExtension(bt.Indicator):

    lines = ('ma', 'sma1', 'sma2', 'signal')

    params = (('maperiod',7),
              ('smaperiod', 30),
              )

    def __init__(self):
        periodMA = bt.indicators.SMA(self.data.close, period=100)
        self.lines.ma = bt.indicators.SMA(self.data.close - periodMA, period=self.p.maperiod)
        # self.lines.ma = self.data.close - periodMA

        self.lines.sma1 = bt.indicators.SMA(self.lines.ma, period=self.p.smaperiod)

        self.lines.signal = bt.indicators.CrossOver(self.lines.ma, self.lines.sma1)