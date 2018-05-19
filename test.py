from broker import Broker
from agent import Agent
from strategies.rsi_fawner import RSI_Bol_Fawner
from plotter import Plotter

from logbook import Logger
import time

import pandas as pd
from catalyst.utils.run_algo import run_algorithm

# Initialize broker
broker = Broker(freq=1)


def initialize(context):
    context.start_time = time.time()

    # Spice it up
    broker.add_agent(Agent('eth_usd', RSI_Bol_Fawner()))

    # Add commission and slippage
    context.set_commission(maker=0.001, taker=0.002)
    context.set_slippage(spread=0.001)


def handle_data(context, data):
    # Broker is the one who makes business
    broker.handle_data(context, data)


def analyze(context, perf):
    Logger(__name__).info('elapsed time: {}'.format(
        time.time() - context.start_time))

    context.base_currency = list(context.exchanges.values())[
        0].base_currency.upper()

    context.asset = list(broker.agents.keys())[0]

    plotter = Plotter(context, perf)
    plotter.plot('portfolio_value', 'asset_trades', 'portfolio_change', 'cash')


if __name__ == '__main__':
    run_algorithm(
        capital_base=100,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        analyze=analyze,
        exchange_name='bitfinex',
        base_currency='usd',
        start=pd.to_datetime('2018-04-25', utc=True),
        end=pd.to_datetime('2018-05-10', utc=True),
    )
