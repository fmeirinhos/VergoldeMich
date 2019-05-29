from .signal import *
from .strategy import *

import talib
import numpy as np


class ADX_DI(Strategy):
    """
    Trading in the direction of a strong trend reduces risk and increases profit
    potential. The average directional index (ADX) is used to determine when
    price is trending strongly.

    Source:
    https://www.investopedia.com/articles/trading/07/adx-trend-indicator.asp
    """
    params = dict(
        ADX_timeperiod=5,
        candle_size='5T',
        trading_window=3
    )

    def __init__(self, **kwargs):
        """
        Args:
            ADX_length (int) The MA length of ADX
        """
        super(ADX_DI, self).__init__(**kwargs)

    def check(self):
        pass

    def eval(self, market, context, data):
        # Fetch market history
        try:
            prices = data.history(
                market,
                fields=['low', 'high', 'close'],
                bar_count=20,
                frequency=self.p.candle_size
            )

        except Exception as e:
            self.logger.warn('historical data not available: {}'.format(e))
            return

        return self.signal(prices)

    def signal(self, prices):

        di_plus = talib.PLUS_DI(prices['high'].values, prices['low'].values, prices[
                                'close'].values, timeperiod=self.p.ADX_timeperiod)
        di_minus = talib.MINUS_DI(prices['high'].values, prices['low'].values, prices[
                                  'close'].values, timeperiod=self.p.ADX_timeperiod)

        crosscall = di_plus[-self.p.trading_window:] > di_minus[
            -self.p.trading_window:]

        if np.all(crosscall[-self.p.trading_window:]):
            arg = 'DIPcross'
            return SIGNAL_LONG, arg
        elif not np.any(crosscall[-self.p.trading_window:]):
            arg = 'DIPput'
            return SIGNAL_SHORT, arg
        else:
            return SIGNAL_NONE, ''
