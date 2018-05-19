import logbook
from datetime import timedelta

from catalyst.api import (
    schedule_function,
)


class Broker(object):
    """
    Defines the trading strategies and exchange pairs

    Attributes
        agents (dict) The crypto currency agents
        freq (int): The minutes between making decisions
    """

    def __init__(self, freq=1):
        self.agents = {}

        self.freq = freq

        self.logger = logbook.Logger(self.__class__.__name__)
        self.logger.info("Broker initialized")
        self.logger.info("\n\n++++ Get rich or die tryin ++++\n")
        self.logger.info("Trading every {} minute(s)".format(self.freq))

    def add_agent(self, agent):
        """
        Adds a currency agent

        Arguments:
            agent (Agent) The crypto currency agent
        """
        self.agents[agent.market] = agent
        self.logger.info(
            "Added {} as trading market".format(agent.market.symbol))

    def initialize(self, context):
        """
        Initialize is a required setup method for initializing state or 
        other bookkeeping. This method is called only once at the beginning of 
        your algorithm.

        Arguments:
            context (dict) Used for maintaining state during your backtest or live trading session
        """

        # schedule_function here
        pass

    def handle_data(self, context, data):
        """
        You should only use handle_data for things you really need to happen every minute

        Arguments:
            context (dict) Used for maintaining state during your backtest or live trading session
        """
        # self.logger.info("Trading at {}".format(data.current_dt))
        # try:
        self._handle_data(context, data)
        # except Exception as e:
        #     self.logger.warn('ABORTING the frame on error {}'.format(e))
        #     context.errors.append(e)
        # if len(context.errors) > 0:
        #     self.logger.info('The errors:\n{}'.format(context.errors))

    def _handle_data(self, context, data):
        """

        Arguments:
            context ()
            data ()
        """
        for market, agent in self.agents.items():
            agent.trade(context, data)
