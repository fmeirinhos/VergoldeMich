from .signal import *
from .strategy import *

import talib
import numpy as np
import time


class RSI_BB_Fawner(Strategy):
    """
    Basic strategy solely based on following RSI.

    The Relative Strength Index is a useful indicator for determining when
    prices over overbought or oversold.
    RSI measures the velocity and magnitude of directional price moves and
    represents the data graphically by oscillating between 0 and 100.
    [source: Investopedia]
    """

    params = dict(
        RSIlength=16,
        RSIoversold=30,
        RSIoverbought=70,
        RSICandle='5T',

        BBlength=20,
        BBsa=2
    )

    def __init__(self, **kwargs):
        """
        Keyword Args:
            RSIlength (int) RSI period Length
            RSIoversold (int) RSI oversold threshold
            RSIoverbought (int) RSI overbought threshold
            RSICandle (str) RSI candle size

            BBlength (int) BB SMA period Length
            BBsa (int) BB standard deviation
        """
        super(RSI_BB_Fawner, self).__init__()

        self.p.update(**kwargs)
        self._check()

    def _check(self):
        """
        Sanity checks for the strategy
        """
        if self.p.RSIoverbought is None:
            self.p.RSIoverbought = 100 - self.p.RSIoversold

        if self.p.BBsa < 0.001 or self.p.BBsa > 50:
            self.logger.error("Bollinger Bands Standard Deviation not OK")

    def signal(self, market, context, data):

        # Fetch market history
        try:
            prices = data.history(
                market,
                fields='price',
                bar_count=200,
                frequency=self.p.RSICandle
            )

        except Exception as e:
            self.logger.warn('historical data not available: '.format(e))
            return

        rsi = talib.RSI(prices.values, timeperiod=self.p.RSIlength)

        bb_upper, middleband, bb_lower = talib.BBANDS(
            prices.values, timeperiod=self.p.BBlength, nbdevup=self.p.BBsa, nbdevdn=self.p.BBsa, matype=0)

        # Record everything useful to analyze later
        record(
            rsi=rsi[-1],
            bb_upper=bb_upper[-1],
            bb_lower=bb_lower[-1]
        )

        close = data.current(market, 'close')

        if rsi[-1] <= self.p.RSIoversold and close <= bb_lower[-1]:
            arg = 'RSI at {:.3f}'.format(rsi[-1])
            return SIGNAL_LONG, arg

        elif rsi[-1] >= self.p.RSIoverbought and close >= bb_upper[-1]:
            arg = 'RSI at {:.3f}'.format(rsi[-1])
            return SIGNAL_SHORT, arg

        return SIGNAL_NONE, ''

    def plot(self, ax, chart):
        """
        Plots the data calculated for the strategy
        """

        self.get_data(chart)

        t = chart['Time'].values
        bbupper = self.sma.add(self.bbdev).values
        bblower = self.sma.subtract(self.bbdev).values

        ax.plot(t, self.sma.values, c='grey', label='BB SMA', lw=0.75)
        ax.plot(t, bbupper, c='grey', label='BB Upper', lw=0.5)
        ax.plot(t, bblower, c='grey', label='BB Lower', lw=0.5)

        # ax.fill_between(t, bblower, bblower, where=bbupper >
        # bbupper, facecolor='black', alpha=0.3, interpolate=True)
