import logbook
import numpy as np

from base import MetaBase

from strategies.signal import *

from catalyst.api import (
    get_open_orders,
    symbol,
    record,
    order,
    order_percent,
    order_target,
    order_target_percent,
    order_target_value,
    order_value
)


class Agent(MetaBase):
    """
    Agent for a crypto asset. The agent manages everything associated with
    the market, such as activating stop losses, trading and changing
    strategies.

    Attributes
            market (str) The currency market
            strategy (Strategy) The to-be-used strategy
    """

    params = dict(
        target_profit=0.1,
        target_percentage=1,
        stop_loss=0.05,
        trail=False
    )
    """
    Explanation:
        A trailing stop is a stop order that can be set at a defined percentage
        away from a security's current market price
        https://www.investopedia.com/terms/t/trailingstop.asp
    """

    def __init__(self, market, strategy):
        super(Agent, self).__init__()

        self.logger = logbook.Logger(self.__class__.__name__)
        self.logger.info("Initialized agent for {} with {}".format(
            market, strategy.__class__.__name__))

        self.market = symbol(market)
        self.strategy = strategy

    def trade(self, context, data):
        """
        This is the brain of the agent and it is what carries out trades
        """

        # Get current price
        price = data.current(self.market, 'price')

        # Check if price is ok
        if price is np.nan:
            self.logger.warn('No pricing data')
            return

        # Activate possible stop losses
        if self.stop_loss(price, context.portfolio.positions[self.market]) is not None:
            return

        record(
            price=price,
            cash=context.portfolio.cash
        )

        # Check current orders for this market
        if len(get_open_orders(self.market)) > 0:
            self.logger.info(
                'Skipping frame until all open orders for {} execute'.format(self.market.symbol))
            return

        if not data.can_trade(self.market):
            self.logger.info("Can't trade {}".format(self.market.symbol))
            return

        # Call strategy
        signal = self.strategy.signal(self.market, context, data)

        # Act on signal
        if signal != SIGNAL_NONE:
            if signal == SIGNAL_LONG:
                self.logger.info(
                    '{}: LONGING {} - price: {}'.format(data.current_dt, self.market.symbol, price))
                order_target_percent(self.market, target=1,
                                     limit_price=price * 1.005)
            if signal == SIGNAL_SHORT:
                self.logger.info(
                    '{}: SHRTING {} - price: {}'.format(data.current_dt, self.market.symbol, price))
                order_target_percent(self.market, target=0,
                                     limit_price=price * 0.995)

    def stop_loss(self, price, amount):

        # if not self.p.trail:
        #     stop_price = price * (1 - self.p.stop_loss)
        #     order(self.market, )

        # else:
        #     self.sell

        return None
