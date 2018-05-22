from .signal import *
from .strategy import *

import talib
import numpy as np
import time


class ADX_DI(Strategy):
    """
    Trading in the direction of a strong trend reduces risk and increases profit
    potential. The average directional index (ADX) is used to determine when
    price is trending strongly. In many cases, it is the ultimate trend
    indicator. After all, the trend may be your friend, but it sure helps to
    know who your friends are. In this article, we'll examine the value of ADX
    as a trend strength indicator.

    Source:
    https://www.investopedia.com/articles/trading/07/adx-trend-indicator.asp
    """
    params = dict(
        ADX_timeperiod=5,
        ADX_cross_timeperiod=1,
        candle_size='5T',
        threshold=60,
        trading_window=4
    )

    def __init__(self, **kwargs):
        """
        Args:
            ADX_length (int) The MA length of ADX
        """
        super(ADX_DI, self).__init__()

    def signal(self, market, context, data):

        # Fetch market history
        try:
            prices = data.history(
                market,
                fields=['low', 'high', 'close', 'price'],
                bar_count=20,
                frequency=self.p.candle_size
            )

        except Exception as e:
            self.logger.warn('historical data not available: {}'.format(e))
            return

        di_plus = talib.PLUS_DI(prices['high'].values, prices['low'].values, prices[
                                'close'].values, timeperiod=self.p.ADX_timeperiod)
        di_minus = talib.MINUS_DI(prices['high'].values, prices['low'].values, prices[
                                  'close'].values, timeperiod=self.p.ADX_timeperiod)

        crosscall = di_plus[-self.p.trading_window::] > di_minus[
            -self.p.trading_window::]

        if np.all(crosscall[-self.p.trading_window::]):
            arg = 'DIPcross'
            return SIGNAL_LONG, arg
        elif not np.all(crosscall[-self.p.trading_window::]):
            arg = 'DPIput'
            return SIGNAL_SHORT, arg
        else:
            return SIGNAL_NONE, ''
