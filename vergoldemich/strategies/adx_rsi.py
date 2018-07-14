from .signal import *
from .strategy import *

import talib
import numpy as np


class ADX_RSI(Strategy):
    """
    Basic strategy based on RSI, BBs and ADX.

    If RSI is satisfied, a timewindow of of trade is opened.
    If the cross is satisfied within the timeframe, the trading is 
    """

    params = dict(
        RSI_timeperiod=14,
        RSI_oversold=33,
        RSI_overbought=70,

        ADX_timeperiod=3,
        ADX_cross_timeperiod=1,
        threshold=60,

        candlesize='5T',
        trading_window=7,
        long_trigger=3,
        short_trigger=2,
    )

    def __init__(self, **kwargs):
        super(ADX_RSI, self).__init__()

        self.p.update(**kwargs)

    def signal(self, market, context, data):

        try:
            prices = data.history(
                market,
                fields=['low', 'high', 'close', 'price'],
                bar_count=50,
                frequency=self.p.candlesize
            )

        except Exception as e:
            self.logger.warn("Historical data not available {}".format(e))
            return

        rsi = talib.RSI(prices['price'].values,
                        timeperiod=self.p.RSI_timeperiod)

        d_p = talib.PLUS_DI(prices['high'].values, prices['low'].values, prices[
            'close'].values, timeperiod=self.p.ADX_timeperiod)
        d_m = talib.MINUS_DI(prices['high'].values, prices['low'].values, prices[
            'close'].values, timeperiod=self.p.ADX_timeperiod)

        crosscall = d_p[-self.p.ADX_timeperiod::] > d_m[-self.p.ADX_timeperiod::]

        # if rsi[-1] <= self.p.RSI_oversold:
        #     if crosscall[-1]:
        #         return SIGNAL_LONG, 'Crosscall and RSI'.format(rsi[-1])
        # elif rsi[-1] >= self.p.RSI_overbought:
        #     if not crosscall[-1]:
        #         return SIGNAL_SHORT, 'Crossput and RSI'.format(rsi[-1])

        # if crosscall[-1]:
        #     if np.any(rsi[-self.p.trading_window::] <= self.p.RSI_oversold):
        #         return SIGNAL_LONG, 'Crosscall and RSI'.format(rsi[-1])

        # else:
        #     if np.any(rsi[-self.p.trading_window::] >= self.p.RSI_overbought):
        #         return SIGNAL_SHORT, 'Crossput and RSI'.format(rsi[-1])

        if np.sum(crosscall) >= self.p.long_trigger:
            if np.any(rsi[-self.p.trading_window::] <= self.p.RSI_oversold):
                return SIGNAL_LONG, 'Crosscall and RSI {}'.format(rsi[-1])

        # elif not crosscall[-1]:
        if self.p.trading_window - np.sum(crosscall) >= self.p.short_trigger:
            if np.any(rsi[-self.p.trading_window::] >= self.p.RSI_overbought):
                return SIGNAL_SHORT, 'Crossput and RSI {}'.format(rsi[-1])
        return SIGNAL_NONE, ''
