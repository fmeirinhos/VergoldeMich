import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from catalyst.utils.run_algo import run_algorithm

from vergoldemich import (
    Broker,
    Agent,
    RSI_BB_Fawner,
    Plotter
)

from logbook import Logger
import time
import pandas as pd

# Initialize broker
broker = Broker()


def initialize(context):
    context.start_time = time.time()

    broker.add_agent(Agent('eth_btc', RSI_BB_Fawner()))

    # Find alternative!
    context.short_positions = {}

    # Add commission and slippage
    context.set_commission(maker=0.000, taker=0.001)
    context.set_slippage(spread=0.000)


def analyze(context, perf):
    Logger(__name__).info('elapsed time: {}'.format(
        time.time() - context.start_time))

    context.quote_currency = list(context.exchanges.values())[
        0].quote_currency.upper()

    context.asset = list(broker.agents.keys())[0]

    plotter = Plotter(context, perf)
    plotter.plot('portfolio_value', 'asset_trades', 'portfolio_change', 'cash')


if __name__ == '__main__':
    run_algorithm(
        capital_base=1,
        data_frequency='minute',
        initialize=initialize,
        handle_data=broker.handle_data,
        analyze=analyze,
        exchange_name='binance',
        quote_currency='eth',
        start=pd.to_datetime('2018-05-10', utc=True),
        end=pd.to_datetime('2018-05-25', utc=True),
    )
