from Order import Order
from utils import get_swapped_order, total_base_volume

from .Exchange import Exchange
from .api.bitfinex_api import Client, TradeClient


class Bitfinex(Exchange):
    def __init__(self, keyfile, logger_name):
        Exchange.__init__(self, 'Bitfinex', 0, logger_name)

    def get_min_vol(self, pair, depth):
        pass

    def get_major_currencies(self):
        pass

    def get_tradeable_pairs(self):
        pass

    def get_depth(self, base, alt):
        pass
