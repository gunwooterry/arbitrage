from Order import Order
from utils import get_swapped_order, total_base_volume
from decimal import Decimal

from .Exchange import Exchange
from .api import bitfinex_api


class Bitfinex(Exchange):
    def __init__(self, keyfile, logger_name):
        key, secret = open(keyfile, 'r').read().split()
        self.api = bitfinex_api
        self.client = self.api.Client
        self.trader = self.api.TradeClient(key, secret)
        self.min_volumes = \
            {info['pair']: Decimal(info['minimum_order_size']) for info in self.client.symbols_details()}
        Exchange.__init__(self, 'Bitfinex', Decimal('0.002'), logger_name)

    def get_major_currencies(self):
        return ['USD', 'BTC', 'ETH', 'ETC', 'BFX', 'ZEC', 'XMR', 'RRT', 'LTC']

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for symbol in self.client.symbols():
            base, alt = symbol[:3].upper(), symbol[3:].upper()
            tradeable_pairs.append((base, alt))
        return tradeable_pairs

    def get_min_vol(self, pair, depth):
        test = self.get_validated_pair(pair)
        if test is not None:
            true_pair, swapped = test
            base, alt = true_pair
            slug = base.lower() + alt.lower()
            alt_vol = self.min_volumes[slug]
            if swapped:
                return alt_vol
            else:
                return total_base_volume(self.get_clipped_alt_volume(depth, alt_vol))

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
