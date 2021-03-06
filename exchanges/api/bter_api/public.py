# Copyright (c) 2013 Alan McIntyre

import datetime
import decimal

from . import common


def get_market_cap(connection=None, error_handler=None):
    if connection is None:
        connection = common.BTERConnection()
    market_details = common.validateResponse(connection.makeJSONRequest('/api/1/marketlist', method='GET'),
                                             error_handler=error_handler)['data']
    caps = {}

    for market in market_details:
        if market['curr_b'] == 'BTC':
            if type(market['marketcap']) is str:
                caps[market['symbol']] = market['marketcap']

    return caps


def get_min_volumes(connection=None, error_handler=None):
    if connection is None:
        connection = common.BTERConnection()
    market_info = common.validateResponse(connection.makeJSONRequest('/api/1/marketinfo', method='GET'),
                                          error_handler=error_handler)['pairs']
    volumes = {}

    for wrapper in market_info:
        for slug, info in wrapper.items():
            volumes[slug] = info['min_amount']

    return volumes


def getDepth(pair, connection=None, error_handler=None):
    """
    Retrieve the depth for the given pair. Returns a tuple (asks, bids);
    each of these is a list of (price, volume) tuples.
    """
    common.validatePair(pair)

    if connection is None:
        connection = common.BTERConnection()

    depth = common.validateResponse(connection.makeJSONRequest('/api/1/depth/%s' % pair, method='GET'),
                                    error_handler=error_handler)

    asks = depth.get('asks')
    if type(asks) is not list:
        raise Exception("The response does not contain an asks list.")

    bids = depth.get('bids')
    if type(bids) is not list:
        raise Exception("The response does not contain a bids list.")

    if len(asks) > 0:
        ask_prices, ask_sizes = list(zip(*asks))
        ask_prices = [decimal.Decimal(p) for p in ask_prices]
        ask_sizes = [decimal.Decimal(s) for s in ask_sizes]
        asks = list(zip(ask_prices, ask_sizes))
    else:
        asks = []
    if len(bids) > 0:
        bid_prices, bid_sizes = list(zip(*bids))
        bid_prices = [decimal.Decimal(p) for p in bid_prices]
        bid_sizes = [decimal.Decimal(s) for s in bid_sizes]
        bids = list(zip(bid_prices, bid_sizes))
    else:
        bids = []

    return asks, bids


class Trade(object):
    __slots__ = ('pair', 'type', 'price', 'tid', 'amount', 'date')

    def __init__(self, **kwargs):
        for s in Trade.__slots__:
            setattr(self, s, kwargs.get(s))

        if type(self.date) in (int, float, decimal.Decimal):
            self.date = datetime.datetime.fromtimestamp(self.date)
        elif type(self.date) in str:
            if "." in self.date:
                self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S.%f")
            else:
                self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")


def getTradeHistory(pair, connection=None, start_tid=None, count=None, error_handler=None):
    """
    Retrieve the trade history for the given pair. Returns a list of
    Trade instances. If count is not None, it should be an integer, and
    specifies the number of items from the trade history that will be
    processed and returned.
    """
    common.validatePair(pair)

    if connection is None:
        connection = common.BTERConnection()

    if start_tid is None:
        result = connection.makeJSONRequest('/api/1/trade/%s' % pair, method='GET')
    else:
        result = connection.makeJSONRequest('/api/1/trade/%s/%d' % (pair, start_tid), method='GET')

    result = common.validateResponse(result, error_handler=error_handler)

    history = result['data']
    if type(history) is not list:
        raise Exception('The response does not contain a history list.')

    result = []
    # Limit the number of items returned if requested.
    if count is not None:
        history = history[:count]

    for h in history:
        h["pair"] = pair
        t = Trade(**h)
        result.append(t)
    return result
