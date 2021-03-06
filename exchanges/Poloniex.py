"""
ALL pairs are written in the order of (BIG coin)_(small coin)
"""

from Order import Order
from utils import get_swapped_order, total_base_volume
from decimal import Decimal

from .Exchange import Exchange
from .api.poloniex_api import poloniex


class Poloniex(Exchange):
    def __init__(self, keyfile, logger_name):
        key, secret = open(keyfile, 'r').read().split()
        self.api = poloniex(key, secret)
        Exchange.__init__(self, 'Poloniex', Decimal('0.0025'), logger_name)

    def get_major_currencies(self):
        majors = []
        for pair, rate in self.api.return24hVolume().items():
            if 'total' in pair:
                continue
            base, alt = pair.split('_')
            if base == 'BTC' and Decimal(rate['BTC']) > 1.0:
                majors.append(alt)
        majors.append('BTC')
        return majors

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in self.api.returnTicker():
            alt, base = pair.split('_')
            tradeable_pairs.append((base.upper(), alt.upper()))
        return tradeable_pairs

    # not all exchanges have the same min volumes!
    def get_min_vol(self, pair, depth):
        test = self.get_validated_pair(pair)
        if test is not None:
            true_pair, swapped = test
            if swapped:
                return Decimal('0.0001')  # 0.011 reduces likelihood we run into rounding errors. but we miss a lot of opportunity
            else:
                # we need to use the depth information to calculate
                # how much alt we need to trade to fulfill min base vol
                return total_base_volume(self.get_clipped_alt_volume(depth, Decimal('0.0001')))

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))

        if pair is not None:
            true_base, true_alt = pair
            depth = self.api.returnOrderBook(true_alt.upper() + '_' + true_base.upper())
            asks, bids = depth['asks'], depth['bids']

            if not swapped:
                book['bids'] = [Order(Decimal(b[0]), Decimal(b[1])) for b in bids]
                book['asks'] = [Order(Decimal(a[0]), Decimal(a[1])) for a in asks]
            else:
                book['asks'] = [get_swapped_order(Order(Decimal(b[0]), Decimal(b[1]))) for b in bids]
                book['bids'] = [get_swapped_order(Order(Decimal(a[0]), Decimal(a[1]))) for a in asks]

        return book

    # Poloniex supports getting multiple orderbooks
    def get_multiple_depths(self, pairs):
        depth = {}
        all_depths = self.api.returnOrderBook('all')

        for pair in pairs:
            book = {'bids': [], 'asks': []}
            true_pair, swapped = self.get_validated_pair(pair)
            if true_pair is not None:
                true_base, true_alt = true_pair
                slug = true_alt.upper() + '_' + true_base.upper()
                if slug in all_depths:
                    single_depth = all_depths[slug]
                    asks, bids = single_depth['asks'], single_depth['bids']

                    if not swapped:
                        book['bids'] = [Order(Decimal(b[0]), Decimal(b[1])) for b in bids]
                        book['asks'] = [Order(Decimal(a[0]), Decimal(a[1])) for a in asks]
                    else:
                        book['asks'] = [get_swapped_order(Order(Decimal(b[0]), Decimal(b[1]))) for b in bids]
                        book['bids'] = [get_swapped_order(Order(Decimal(a[0]), Decimal(a[1]))) for a in asks]
                else:
                    self.log.info('No {} orders'.format(slug))

            base, alt = pair
            depth[base + '_' + alt] = book

        return depth

    def get_balance(self, currency):
        # TODO: Does it really return "available" balances? (not trading)
        balances = self.get_all_balances()
        if currency in balances:
            return balances[currency]
        else:
            return Decimal(0)

    def get_all_balances(self):
        balances = self.api.returnBalances()
        return balances

    def submit_order(self, order_type, pair, price, volume):
        true_pair, swapped = self.get_validated_pair(pair)
        if true_pair is not None:
            base, alt = true_pair
            slug = alt.upper() + '_' + base.upper()
            if not swapped:
                if order_type == 'buy':
                    self.api.buy(slug, price, volume)
                elif order_type == 'sell':
                    self.api.sell(slug, price, volume)
            else:
                order = get_swapped_order(Order(price, volume))
                if order_type == 'buy':
                    self.api.sell(slug, order.p, order.v)
                elif order_type == 'sell':
                    self.api.buy(slug, order.p, order.v)
        else:
            print("Invalid order: {}, {}".format(pair[0], pair[1]))

            # TODO: Save information such as order numbers

    def confirm_order(self, order_id):
        pass
