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

    """
    Explanation:
        A trailing stop is a stop order that can be set at a defined percentage
        away from a security's current market price
        https://www.investopedia.com/terms/t/trailingstop.asp
    """
    params = dict(
        shrt_target_profit=0.11,
        shrt_stop_loss=0.04,

        long_target_profit=0.1,
        long_stop_loss=0.05,

        trail=False,
    )

    def __init__(self, **kwargs):
        """
        Keyword Args:
            shrt_target_profit (float)
            shrt_stop_loss (float)

            long_target_profit (float)
            long_stop_loss (float)
        """
        super(StopLoss, self).__init__()

        self.p.update(**kwargs)
        self._check()

    def _check(self):
        """
        Sanity checks for the strategy
        """
        if self.p.long_target_profit <= 0 or self.p.shrt_target_profit <= 0:
            self.logger.error("Invalid target_profit percentage")
            raise RuntimeError

        if self.p.long_stop_loss <= 0 or self.p.shrt_stop_loss <= 0:
            self.logger.error("Invalid stop_loss percentage")
            raise RuntimeError

    def signal(self, market, context, data):
        price = data.current(market, 'price')

        # Get position
        pos = context.portfolio.positions[market]
        # print(pos)

        if pos.amount > 0:
            if price <= pos.cost_basis * (1 - self.p.long_stop_loss):
                arg = 'StopLoss at {}'.format(self.p.long_stop_loss)
                return SIGNAL_SHORT, arg

            elif price >= pos.cost_basis * (1 + self.p.long_target_profit):
                arg = 'Target profit at {}'.format(self.p.long_target_profit)
                return SIGNAL_SHORT, arg

        elif pos.amount == 0:
            last_sale_price = context.short_positions.get(
                market.symbol, float('nan'))

            if price <= last_sale_price * (1 - self.p.shrt_target_profit):
                arg = 'Target profit at {}'.format(self.p.shrt_target_profit)
                return SIGNAL_LONG, arg

            elif price >= last_sale_price * (1 + self.p.shrt_stop_loss):
                arg = 'StopLoss at {}'.format(self.p.shrt_stop_loss)
                return SIGNAL_LONG, arg

        return SIGNAL_NONE, ''

    # def plot(self, )
