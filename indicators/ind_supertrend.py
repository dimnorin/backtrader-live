import backtrader as bt


class SuperTrend(bt.Indicator):
    lines = ('signal',)

    params = (('period', 11),
              ('mult', 2),
              )

    def __init__(self):
        atr = bt.indicators.ATR(self.data, period=self.p.period)
        atr = self.p.mult * atr
        self.basicUB = (self.data.high + self.data.low) / 2.0 + atr
        self.basicLB = (self.data.high + self.data.low) / 2.0 - atr

        self.finalUB = atr * 1
        self.finalLB = atr * 1
        self.dir = atr * 1

    def prenext(self):
        self.dir[0] = 1
        self.l.signal[0] = 0
        self.finalUB[0] = 0
        self.finalLB[0] = 0

    def next(self):
        # self.l.finalUB[0] = max(self.basicUB[0], self.l.finalUB[-1]) if self.data.close[-1] > self.l.finalUB[-1] else self.basicUB[0]
        self.finalUB[0] = self.basicUB[0] if self.basicUB[0] < self.finalUB[-1] < self.data.close[-1] else self.basicUB[-1]
        self.finalLB[0] = self.basicLB[0] if self.basicLB[0] > self.finalLB[-1] > self.data.close[-1] else self.basicLB[-1]

        # self.supertrend = self.l.finalUB[0] if self.data.close(0) <= self.l.finalUB[0] else self.l.finalLB[0]
        self.dir[0] = 1 if self.dir[-1] == -1 and self.data.close[0] > self.finalUB[-1] else -1 if self.dir[-1] == 1 and self.data.close[0] < self.finalLB[-1] else self.dir[-1]
        # self.l.signal[0] = 1 if self.dir[0] == 1 and self.dir[-1] == -1 else -1 if self.dir[0] == -1 and self.dir[-1] == 1 else 0
        self.l.signal[0] = self.dir[0]

        # print('close=%s, finalLB=%s, finalUB=%s, dir=%s, signal=%s' % (self.data.close[0], self.finalLB[-1], self.finalUB[-1], self.dir[0], self.l.signal[0]))