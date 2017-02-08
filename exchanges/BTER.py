import os

from Order import Order
from utils import get_swapped_order, total_base_volume
from .Exchange import Exchange
from .api import bter_api


class BTER(Exchange):
    def __init__(self, keyfile, logger_name):
        # TODO: Rename one of "keyfile"s
        keyfile = os.path.abspath(keyfile)
        self.keyhandler = bter_api.KeyHandler(keyfile)
        key = self.keyhandler.getKeys()[0]
        self.conn = bter_api.BTERConnection()
        self.api = bter_api.TradeAPI(key, self.keyhandler)
        self.min_volumes = bter_api.get_min_volumes()
        Exchange.__init__(self, 'BTER', 0.002, logger_name)

    def get_min_vol(self, pair, depth):
        test = self.get_validated_pair(pair)
        if test is not None:
            true_pair, swapped = test
            base, alt = true_pair
            slug = base.lower() + '_' + alt.lower()
            alt_vol = float(self.min_volumes[slug])
            if swapped:
                return alt_vol
            else:
                return total_base_volume(self.get_clipped_alt_volume(depth, alt_vol))

    def get_major_currencies(self):
        majors = []
        for sym, cap in bter_api.get_market_cap().items():
            if len(cap) >= 5:
                majors.append(sym)
        majors.append('CNY')  # BTER focuses on CNY.
        return majors

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in bter_api.all_pairs:
            a, b = pair.split("_")
            tradeable_pairs.append((a.upper(), b.upper()))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))
        if pair is None:
            return

        pairstr = pair[0].lower() + "_" + pair[1].lower()
        asks, bids = bter_api.getDepth(pairstr)

        if not swapped:
            book['bids'] = [Order(float(b[0]), float(b[1])) for b in bids]
            book['asks'] = [Order(float(a[0]), float(a[1])) for a in asks]
        else:
            book['asks'] = [get_swapped_order(Order(float(b[0]), float(b[1]))) for b in bids]
            book['bids'] = [get_swapped_order(Order(float(a[0]), float(a[1]))) for a in asks]

        return book

    def get_balance(self, currency):
        funds = self.api.getFunds(self.conn, error_handler=None)
        if currency in funds:
            return float(funds[currency])
        else:
            return 0.0
            # data = self.api.getInfo(connection = self.conn)
            # return getattr(data, 'balance_' + currency.lower())

    def get_all_balances(self):
        funds = self.api.getFunds(self.conn, error_handler=None)
        return {k: float(v) for k, v in funds}

    def submit_order(self, order_type, pair, price, volume):
        true_pair, swapped = self.get_validated_pair(pair)
        if true_pair is not None:
            base, alt = true_pair
            slug = base.lower() + '_' + alt.lower()
            if not swapped:
                if order_type == 'buy':
                    self.api.placeOrder(slug, 'buy', price, volume)
                elif order_type == 'sell':
                    self.api.placeOrder(slug, 'sell', price, volume)
            else:
                order = get_swapped_order(Order(price, volume))
                if order_type == 'buy':
                    self.api.placeOrder(slug, 'sell', order.p, order.v)
                elif order_type == 'sell':
                    self.api.placeOrder(slug, 'buy', order.p, order.v)
        else:
            self.log.info("Invalid order: {}, {}".format(pair[0], pair[1]))

    def confirm_order(self, order_id):
        pass
