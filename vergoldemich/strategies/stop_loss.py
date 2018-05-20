from .signal import *
from .strategy import *

import logbook


class StopLoss(Strategy):
    """
    A stop-loss order is an order placed with a broker to sell a security
    when it reaches a certain price. Stop loss orders are designed to
    limit an investor’s loss on a position in a security. Although most
    investors associate a stop-loss order with a long position, it can also
    protect a short position, in which case the security gets bought if it
    trades above a defined price.

    Source:
    https://www.investopedia.com/terms/s/stop-lossorder.asp
    """

    params = dict(
        target_profit=0.09,
        stop_loss=0.3,
        trail=False
    )

    def __init__(self, **kwargs):
        """
        Keyword Args:
            sell (float) Price is x% less than the entry point
            trail (Bool) trailing stop is a stop order that can be set at a defined percentage away from a security's current market price
        """
        super(StopLoss, self).__init__()

        self.logger = logbook.Logger(self.__class__.__name__)

        self.p.update(**kwargs)
        self._check()

    def _check(self):
        if self.p.target_profit <= 0:
            self.logger.error("Invalid target_profit percentage")
            raise RuntimeError

    def signal(self, market, context, data):
        price = data.current(market, 'price')

        # Get position
        pos = context.portfolio.positions[market]

        # Simple stop loss
        if pos.amount > 0:

            if price <= pos.cost_basis * (1 - self.p.stop_loss):
                arg = 'StopLoss at {}'.format(self.p.target_profit)
                return SIGNAL_SHORT, arg

            elif price >= pos.cost_basis * (1 + self.p.target_profit):
                arg = 'Target profit at {}'.format(self.p.target_profit)
                return SIGNAL_SHORT, arg

        return SIGNAL_NONE, ''

    # def plot(self, )
