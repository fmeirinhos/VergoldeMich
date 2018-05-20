from .signal import *
from .strategy import *

import logbook

# from pandas_talib import RSI, SMA, STDDEV, SETTINGS
from talib import RSI, SMA, STDDEV
import talib


class RSI_Bol_Fawner(Strategy):
    """
    Basic strategy solely based on following RSI.

    The Relative Strength Index is a useful indicator for determining when
    prices over overbought or oversold.
    RSI measures the velocity and magnitude of directional price moves and
    represents the data graphically by oscillating between 0 and 100.
    [source: Investopedia]
    """

    params = dict(
        RSIlength=14,
        RSIoversold=35,
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
        super(RSI_Bol_Fawner, self).__init__()

        self.logger = logbook.Logger(self.__class__.__name__)

        self.p.update(**kwargs)
        self._check()

        # Change internal settings of pandas_talib
        # SETTINGS.join = False

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
                bar_count=50,
                frequency=self.p.RSICandle
            )

        except Exception as e:
            self.logger.warn('historical data not available: '.format(e))
            return

        rsi = talib.RSI(prices.values, timeperiod=self.p.RSIlength)

        pos_amount = context.portfolio.positions[market].amount

        # Record everything useful to analyze later
        record(
            rsi=rsi[-1],
        )

        if rsi[-1] <= self.p.RSIoversold and pos_amount == 0:
            arg = 'RSI at {}'.format(rsi[-1])
            return SIGNAL_LONG, arg

        elif rsi[-1] >= self.p.RSIoverbought and pos_amount > 0:
            arg = 'RSI at {}'.format(rsi[-1])
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
