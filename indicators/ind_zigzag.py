import backtrader as bt
import math

class ZigZag(bt.ind.PeriodN):
    '''
      Identifies Peaks/Troughs of a timeseries
    '''
    lines = (
        'trend', 'last_pivot_t', 'last_pivot_x', 'last_pivot_ago',
        'zigzag_peak', 'zigzag_valley', 'zigzag', 'last_zigzag',
    )

    # Fancy plotting name
    # plotlines = dict(logreturn=dict(_name='log_ret'))
    plotinfo = dict(
        subplot=False,
        plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
    )

    plotlines = dict(
        trend=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        last_pivot_t=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        last_pivot_x=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        last_pivot_ago=dict(marker='', markersize=0.0, ls='', _plotskip=True),
        zigzag_peak=dict(marker='v', markersize=4.0, color='red',
                         fillstyle='full', ls=''),
        zigzag_valley=dict(marker='^', markersize=4.0, color='red',
                           fillstyle='full', ls=''),
        zigzag=dict(_name='zigzag', color='blue', ls='-', _skipnan=True),
        last_zigzag=dict(_name='last_zigzag', color='blue', ls='--', _skipnan=True),
    )

    # update value to standard for Moving Averages
    params = (
        ('period', 2),
        ('up_retrace', 0.5),
        ('dn_retrace', 0.5),
        ('bardist', 0.015),  # distance to max/min in absolute perc
    )

    def __init__(self):
        super(ZigZag, self).__init__()

        if not self.p.up_retrace:
            raise ValueError('Upward retracement should not be zero.')

        if not self.p.dn_retrace:
            raise ValueError('Downward retracement should not be zero.')

        if self.p.up_retrace < 0:
            self.p.up_retrace = -self.p.up_retrace

        if self.p.dn_retrace > 0:
            self.p.dn_retrace = -self.p.dn_retrace

        self.p.up_retrace = self.p.up_retrace / 100
        self.p.dn_retrace = self.p.dn_retrace / 100

        self.missing_val = float('nan')

    def prenext(self):
        self.lines.trend[0] = 0
        self.lines.last_pivot_t[0] = 0
        self.lines.last_pivot_x[0] = self.data[0]
        self.lines.last_pivot_ago[0] = 0
        self.lines.zigzag_peak[0] = self.missing_val
        self.lines.zigzag_valley[0] = self.missing_val
        self.lines.zigzag[0] = self.missing_val
        self.lines.last_zigzag[0] = self.missing_val

    def next(self):
        data = self.data
        trend = self.lines.trend
        last_pivot_t = self.lines.last_pivot_t
        last_pivot_x = self.lines.last_pivot_x
        last_pivot_ago = self.lines.last_pivot_ago
        zigzag_peak = self.lines.zigzag_peak
        zigzag_valley = self.lines.zigzag_valley
        zigzag = self.lines.zigzag
        last_zigzag = self.lines.last_zigzag

        x = data[0]
        r = x / last_pivot_x[-1] - 1
        curr_idx = len(data) - 1

        trend[0] = trend[-1]
        last_pivot_x[0] = last_pivot_x[-1]
        last_pivot_t[0] = last_pivot_t[-1]
        last_pivot_ago[0] = curr_idx - last_pivot_t[0]
        zigzag_peak[0] = self.missing_val
        zigzag_valley[0] = self.missing_val
        zigzag[0] = self.missing_val
        last_zigzag[0] = x

        if trend[-1] == 0:
            if r >= self.p.up_retrace:
                piv = last_pivot_x[0] * (1 - self.p.bardist)
                zigzag_valley[-int(last_pivot_ago[0])] = piv
                zigzag[-int(last_pivot_ago[0])] = last_pivot_x[0]
                trend[0] = 1
                last_pivot_x[0] = x
                last_pivot_t[0] = curr_idx
            elif r <= self.p.dn_retrace:
                piv = last_pivot_x[0] * (1 + self.p.bardist)
                zigzag_peak[-int(last_pivot_ago[0])] = piv
                zigzag[-int(last_pivot_ago[0])] = last_pivot_x[0]
                trend[0] = -1
                last_pivot_x[0] = x
                last_pivot_t[0] = curr_idx
        elif trend[-1] == -1:
            if r >= self.p.up_retrace:
                piv = last_pivot_x[0] * (1 - self.p.bardist)
                zigzag_valley[-int(last_pivot_ago[0])] = piv
                zigzag[-int(last_pivot_ago[0])] = last_pivot_x[0]
                trend[0] = 1
                last_pivot_x[0] = x
                last_pivot_t[0] = curr_idx
            elif x < last_pivot_x[-1]:
                last_pivot_x[0] = x
                last_pivot_t[0] = curr_idx
        elif trend[-1] == 1:
            if r <= self.p.dn_retrace:
                piv = last_pivot_x[0] * (1 + self.p.bardist)
                zigzag_peak[-int(last_pivot_ago[0])] = piv
                zigzag[-int(last_pivot_ago[0])] = last_pivot_x[0]
                trend[0] = -1
                last_pivot_x[0] = x
                last_pivot_t[0] = curr_idx
            elif x > last_pivot_x[-1]:
                last_pivot_t[0] = curr_idx
                last_pivot_x[0] = x

        idx = 1
        while idx < len(self.zigzag) and math.isnan(zigzag[-idx]):
            last_zigzag[-idx] = self.missing_val
            idx += 1

        if idx < len(self.data):
            last_zigzag[-idx] = zigzag[-idx]