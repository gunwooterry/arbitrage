# represents a single order object
# very simple data structure!


class Order(object):
    def __init__(self, price, volume, type=None, pair=None, order_id=None, timestamp=None):
        """
        markets are usually expressed in terms of BASE_ALT where you buy
        and sell units of BASE with ALT.
        price = price (in units alt) of 1 unit of base
        volume = total volume of base desired
        orderID = necessary for tracking & cancelling & ignoring already executed orders when backtesting
        """
        self.p = price
        self.v = volume
        self.type = type  # buy or sell
        self.pair = pair  # market we are trading on
        self.id = order_id
        self.time = timestamp

    def __str__(self, *args, **kwargs):
        return '%s_%s price:%f volume:%f type:%s' % (self.pair[0], self.pair[1], self.p, self.v, self.type)
