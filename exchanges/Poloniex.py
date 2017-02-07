from .Exchange import Exchange
from .api.poloniex_api import poloniex
from Order import Order
from utils import get_swapped_order

'''
ALL pairs are written in the order of (BIG coin)_(small coin)
'''


class Poloniex(Exchange):
    def __init__(self, keypath):
        keyfile = open(keypath, 'r')
        api_key = keyfile.readline()
        secret = keyfile.readline()
        self.api = poloniex(api_key, secret)
        super(Poloniex, self).__init__()
        self.name = 'Poloniex'
        self.trading_fee = 0.0025
        self.log = logging.getLogger(self.name)

    def get_major_currencies(self):
        majors = []
        for pair, rate in self.api.return24hVolume().items():
            if 'total' in pair:
                continue
            base, alt = pair.split('_')
            if base == 'BTC' and float(rate['BTC']) > 1.0:
                majors.append(alt)
        return majors

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in self.api.returnTicker():
            a, b = pair.split("_")
            tradeable_pairs.append((b.upper(), a.upper()))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))

        if pair is None:
            return
        pairstr = pair[1].upper() + '_' + pair[0].upper()
        depth = self.api.returnOrderBook(pairstr)

        asks, bids = depth['asks'], depth['bids']
        if not swapped:
            book['bids'] = [Order(float(b[0]), float(b[1])) for b in bids]
            book['asks'] = [Order(float(a[0]), float(a[1])) for a in asks]
        else:
            book['asks'] = [get_swapped_order(Order(float(b[0]), float(b[1]))) for b in bids]
            book['bids'] = [get_swapped_order(Order(float(a[0]), float(a[1]))) for a in asks]

        return book

    def get_balance(self, currency):
        balances = self.get_all_balances()
        return balances[currency]

    def get_all_balances(self):
        balances = self.api.returnBalances()
        return balances

    def submit_order(self, gc, gv, rc, rv):
        pass

    def confirm_order(self, order_id):
        pass
