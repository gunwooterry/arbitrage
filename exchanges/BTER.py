import logging
import os

from Order import Order
from utils import get_swapped_order

from .Exchange import Exchange
from .api import bterapi


class BTER(Exchange):
    def __init__(self, keyfile):
        keyfile = os.path.abspath(keyfile)
        self.keyhandler = bterapi.KeyHandler(keyfile)
        key = self.keyhandler.getKeys()[0]
        self.conn = bterapi.BTERConnection()
        self.api = bterapi.TradeAPI(key, self.keyhandler)
        super(BTER, self).__init__()
        self.name = 'BTER'
        self.trading_fee = 0.002
        self.log = logging.getLogger(self.name)

    def get_major_currencies(self):
        majors = []
        for sym, cap in bterapi.getMarketCap().items():
            if len(cap) >= 11:
                majors.append(sym)
        majors.append('CNY')  # BTER focuses on CNY.
        return majors

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in bterapi.all_pairs:
            a, b = pair.split("_")
            tradeable_pairs.append((a.upper(), b.upper()))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))
        if pair is None:
            return

        pairstr = pair[0].lower() + "_" + pair[1].lower()
        asks, bids = bterapi.getDepth(pairstr)

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

    def submit_order(self, gc, gv, rc, rv):
        return NotImplemented

    #         pair, swapped = self.get_validated_pair((rc, gc))
    #         print swapped
    #         if pair is None:
    #             return
    #         pairstr = pair[0].lower() + "_" + pair[1].lower()
    #         if swapped:
    #             price = rv/gv
    #             self.api.trade(pairstr, 'sell', price, gv)
    #         else:
    #             price = gv/rv
    #             self.api.trade(pairstr, 'buy', price, rv)

    def confirm_order(self, order_id):
        pass
