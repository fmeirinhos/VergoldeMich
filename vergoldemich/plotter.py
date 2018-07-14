import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import datetime
import logbook
from catalyst.exchange.utils.stats_utils import extract_transactions


class Plotter(object):
    """
    Main crypto plotter
    """

    def __init__(self, context, performance, **kwargs):
        """
        Sets the seaborn options

        Args:
            perf (Pandas.DataFrame): The algo performance DataFrame.
            **kwargs: See seaborn options
        """
        self.perf = performance
        self.context = context

        self._logger = logbook.Logger(self.__class__.__name__)

        try:
            import seaborn as sns

            # Set the default seaborn options
            self.options = {'palette': 'Set2'}
            self.options.update(**kwargs)

            sns.set(**self.options)
            sns.set_color_codes()

        except ImportError:
            self._logger.warn(
                'Seaborn not installed. Skipping seaborn options')

    def plot(self, *args):
        """
        Draws several plots

        Args:
                *args (str) the functions to plot
        """
        self.plots = [*args]
        self.subplot = str(len(self.plots)) + '1'  # vertical plot

        self.subplot_kwargs = {'sharex': plt.subplot(int(self.subplot + '1'))}

        for plot in self.plots:
            ax = self._get_axis(plot)
            getattr(self, plot)(ax)

        plt.show()

    def _get_axis(self, plot):
        """
        Fetches the axis of the plot ``plot``

        Arguments:
            plot (str)
        """
        loc = int(self.subplot + str(self.plots.index(plot) + 1))

        return plt.subplot(loc, **self.subplot_kwargs)

    def asset_trades(self, ax):
        """
        Plots the asset price and trades

        Args:
                ax (matplotlib.pyplot.subplot) Subplot
        """
        self.perf.loc[:, ['price', 'short_mavg', 'long_mavg']].plot(
            ax=ax, label='Price')
        ax.legend_.remove()
        ax.set_ylabel('{asset}\n({base})'.format(
            asset=self.context.asset.symbol, base=self.context.quote_currency))

        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))
        self.mark_purchases(ax)

    def mark_purchases(self, ax):
        """
        Marks the purchases made

        Args:
                ax (matplotlib.pyplot.subplot) Subplot
        """

        transaction_df = extract_transactions(self.perf)
        if not transaction_df.empty:
            buy_df = transaction_df[transaction_df['amount'] > 0]
            sell_df = transaction_df[transaction_df['amount'] < 0]
            ax.scatter(buy_df.index.to_pydatetime(), self.perf.loc[
                       buy_df.index, 'price'], marker='^', s=20, c='green', label='')
            ax.scatter(sell_df.index.to_pydatetime(), self.perf.loc[
                       sell_df.index, 'price'], marker='v', s=20, c='red', label='')

    def portfolio_value(self, ax):
        """
        Plots the portfolio value using the base currency

        Args:
                ax (matplotlib.pyplot.subplot) Subplot
        """

        self.perf.loc[:, ['portfolio_value']].plot(ax=ax)
        ax.legend_.remove()
        ax.set_ylabel('Portfolio Value\n({})'.format(
            self.context.quote_currency))
        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    def portfolio_change(self, ax):
        """
        Plots the percentual change of the portfolio and the asset

        Args:
                ax (matplotlib.pyplot.subplot) Subplot
        """
        price = self.perf.loc[:, ['price']].values
        price0 = price[1]
        self.perf['price_change'] = (price - price0) / price0

        self.perf.loc[:, ['algorithm_period_return']].plot(ax=ax)
        self.perf.loc[:, ['price_change']].plot(ax=ax)

        # ax.legend_.remove()
        ax.set_ylabel('Percentage Change')
        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    def cash(self, ax):
        """
        Plots the cash

        Args:
                ax (matplotlib.pyplot.subplot) Subplot
        """
        self.perf.cash.plot(ax=ax)
        ax.set_ylabel('Cash\n({})'.format(self.context.quote_currency))
        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(0, end, end / 5))
