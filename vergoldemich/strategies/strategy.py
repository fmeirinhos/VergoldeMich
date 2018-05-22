from .signal import *
from ..base import MetaBase

from catalyst.api import (
    record
)


class Strategy(MetaBase):

    """Docstring for Strategy. """

    def __str__(self):
        return "{}".format(self.__class__.__name__)

    def __init__(self):
        super(Strategy, self).__init__()

    def signal(self, market, context, data):
        """
        Will return either a BUY, SELL or WAIT signal for the given market
        """
        raise NotImplementedError

    def plot(self, ax, chart):
        """
        Plots the relevant data of the strategy
        """
        raise NotImplementedError
