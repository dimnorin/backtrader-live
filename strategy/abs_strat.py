#!/usr/bin/env python3

import backtrader as bt
import datetime as dt

from abc import ABC, abstractmethod
import utils.util as utils

class AbstractLiveStrategy(bt.Strategy):
    params = dict(
        is_live=False,
        logger=None,
        pair='LTC/USDT',
        stop_loss=0.03,
        take_profit=0.02,
        is_trail_sl=True,
        tp_deviation=0.07,
    )

    def __init__(self):
        # logger = Logger(sys.stdout)
        # sys.stdout = logger
        self.logger = self.p.logger
        # self.logger.getLogger().setLevel(logging.DEBUG if self.p.printlog else logging.INFO)

        self._order = None
        self.status = "DISCONNECTED"
        self._force_close = False
        self.trades = []

        self._is_exit_fired = False

        self._init_indicators()
        self._init()
        self.log(vars(self.params))

    @abstractmethod
    def _init_indicators(self):
        pass

    @abstractmethod
    def _is_buy(self):
        pass

    @abstractmethod
    def _is_fire_stop_loss(self):
        pass

    def _init(self):
        self._stop_price = None
        self._sl_price = None
        self._tp_price = None
        self.is_trail_sl = self.p.is_trail_sl
        self.sl_dev = self.p.stop_loss
        self.is_trail_dev_set = False # If trail deviation is set to move stop loss to take profit level

    def next(self):
        if self.p.is_live and (self.status != "LIVE" or utils.dt_diff_seconds(bt.num2date(self.data0.datetime[0])) > 60):
            # self.log("%s - $%.2f" % (self.status, self.data0.close[0]))
            self.log('Skip this data')
            return

        if self._order:
            return

        # We are working only with BUY orders
        if not self.position:
            if self._is_buy():
                self.log('=' * 5 + 'Got buy signal', True)
                self._make_buy()
        else:
            self._check_trail()
        self.log('*' * 5 + 'NEXT: %s' % self.data0.close[0], self.data0._compression > 1)

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade", True)
        else:
            self.log("NOT LIVE - %s" % self.status)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                        order.executed.value,
                        order.executed.comm), True)

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self._is_exit_fired = False
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm), True)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected %s' % order.status)

        # Write down: no pending order
        self._order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm), True)
        self.trades.append(trade)

    def log(self, txt, notify=False):
        try:
            data = bt.num2date(self.data0.datetime[0])
            txt = '%s %s' % (data, txt)
        except: pass
        # if self.params.printlog or doprint:
        if self.logger:
            if isinstance(txt, Exception):
                self.logger.error(txt)
            else:
                self.logger.info(txt, not notify)

    def _make_buy(self):
        # if self.p.is_live: return # TODO remove for strategy trade
        try:
            self._order = self.buy(exectype=bt.Order.Market)
            # self._stop_price = self.data.close[0] * (1 - self.params.stop_loss)
            self.log("BUY ORDER created: %s" % self._order.ref)
        except Exception as e:
            self.log('Failed to make buy order: %s. Continue working...' % e, True)
            self.log(e)

    def _check_trail(self):
        """ Recalculate trail price """
        if self.is_trail_sl and self._sl_price:
            new_sl = self.data.close[0] * (1 - self.sl_dev)
            if new_sl > self._sl_price:
                self.log('Move SL, close: %s, old: %s, new: %s' % (self.data.close[0], self._sl_price, new_sl))
                self._sl_price = new_sl

        self._take_profit()

        # Fire stop loss order
        if self.position:
            if self._sl_price and self._sl_price >= self.data.close[0] or \
                    self._is_fire_stop_loss() or self._force_close or \
                    self._stop_price and self._stop_price >= self.data.close[0]:
                self.log('Fire stop loss, sl_price: %s, close: %s' % (self._sl_price, self.data.close[0]), True)
                self._exit_position()


    def _take_profit(self):
        if self.p.take_profit > 0: # Check if take profit is enabled
            if not self.is_trail_dev_set and self._tp_price:
                new_tp = self._tp_price * (1 + self.p.tp_deviation / 10)
                if new_tp < self.data.close[0]:
                    self.log('Swipe take profit. Old tp: %s, new tp: %s(%s), stop loss: %s, deviation: %s' %
                             (self._tp_price, new_tp, self.p.tp_deviation, self._tp_price, self.data.close[0] * (1 - self.p.tp_deviation)))
                    self.is_trail_sl = True
                    self._sl_price = self._tp_price
                    self.sl_dev = self.p.tp_deviation
                    self.is_trail_dev_set = True

    def _exit_position(self):
        if self.position and not self._is_exit_fired:
            self._is_exit_fired = True
            self.sell(exectype=bt.Order.Market)
            self._init()

    def panic_sell(self):
        if self.position:
            self.log('Panic sell, sl_price: %s, close: %s' % (self._sl_price, self.data.close[0]), True)
            self._exit_position()
        else:
            self.log('Panic sell, no open position, close: %s' % self.data.close[0], True)
