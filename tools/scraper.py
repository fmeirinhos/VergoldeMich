from coinmarketcap import Market
import time


class CoinMarketcap:

    def __init__(self):
        self.cmc = Market()
        self.investments = {}

    def get_percentage(self, start=0, limit=100):

        ticker = self.cmc.ticker(start=start, limit=limit, convert='Eur')

        for key, val in ticker['data'].items():
            name = val['name']
            pc1h = val['quotes']['USD']['percent_change_1h']

            if name in self.investments:
                self.investments[name].append(pc1h)

            else:
                self.investments[name] = [pc1h]


cmc = CoinMarketcap()

while True:

    cmc.get_percentage(start=000, limit=100)
    cmc.get_percentage(start=101, limit=200)

    for key, val in cmc.investments.items():
        if val[-1] > 2:
            print("Invest in: {}\t1h % change: {}".format(key, val[-1]))

        # TODO: What if val[-2] == 0?
        if len(val) > 1 and (val[-1] - val[-2]) / abs(val[-2]) > 2:
            print(
                "\nPOSSIBLE PUMP\nInvest in: {}\n1h % change in the last 2 minutes{} -> {}\n\n".format(key, val[-2], val[-1]))

    print("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
    time.sleep(120)
