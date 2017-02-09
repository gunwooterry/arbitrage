from Order import Order
from utils import get_swapped_order, total_base_volume
from itertools import product

from .Exchange import Exchange
from .api import bitfinex_api


class Bitfinex(Exchange):
    def __init__(self, keyfile, logger_name):
        key, secret = open(keyfile, 'r').read().split()
        self.api = bitfinex_api
        self.client = self.api.Client
        self.trader = self.api.TradeClient(key, secret)
        Exchange.__init__(self, 'Bitfinex', 0.002, logger_name)

    def get_major_currencies(self):
        return ['USD', 'BTC', 'ETH', 'ETC', 'BFX', 'ZEC', 'XMR', 'RRT', 'LTC']

    def get_tradeable_pairs(self):
        bases = ['ETH', 'ETC', 'BFX', 'ZEC', 'XMR', 'RRT', 'LTC']
        alts = ['USD', 'BTC']
        tradeable_pairs = list(product(bases, alts))
        tradeable_pairs.append(('BTC', 'USD'))
        return tradeable_pairs

    def get_min_vol(self, pair, depth):
        pass

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))

        if pair is not None:
            true_base, true_alt = pair
            depth = self.client.order_book(true_base.lower() + true_alt.lower())
            asks, bids = depth['asks'], depth['bids']

            if not swapped:
                book['bids'] = [Order(b['price'], b['amount']) for b in bids]
                book['asks'] = [Order(a['price'], a['amount']) for a in asks]
            else:
                book['asks'] = [get_swapped_order(Order(b['price'], b['amount'])) for b in bids]
                book['bids'] = [get_swapped_order(Order(a['price'], a['amount'])) for a in asks]

        return book

    def get_balance(self, currency):
        balances = self.get_all_balances()
        if currency in balances:
            return balances[currency]
        else:
            return 0.0

    def get_all_balances(self):
        # TODO: Check the exact form of balances
        pass

    def submit_order(self, order_type, pair, price, volume):
        pass

    def confirm_order(self, order_id):
        pass
