# Triangular Arbitrage Bot
# SINGLE exchange algorithm -> allows for near-instantaneous arbitrage without
# necessitating positions in multiple currencies.

import logging
import logging.handlers
from threading import Thread
import time

from Bot import Bot
from TriangleProfitCalculator import TriangleProfitCalculator


class TriangularArbitrageBot(Bot):
    def __init__(self, config, brokers, targets):
        super(TriangularArbitrageBot, self).__init__(config, brokers)
        # this bot only trades on ONE broker!!!
        # the reason I am doing this is to make the initial prototype system more robust to failure
        # i.e. others keep trading even if one exchange fails.
        if len(self.brokers) > 1:
            self.log.warning("TriangleArbitrageBot only trades on one exchange! Ignoring the others...")
        self.broker = self.brokers[0]
        self.log = logging.getLogger(self.broker.xchg.name)
        self.targets = targets
        file_handler = logging.FileHandler('./log/%s.log' % (self.broker.xchg.name,))
        streamHandler = logging.StreamHandler()
        self.log.setLevel(logging.INFO)
        self.log.addHandler(file_handler)
        self.log.addHandler(streamHandler)
        self.init_cross_markets()

    # requires HTTP Connection
    def get_roundtrip_pairs(self, target):
        """
        given currency A, returns an array of all tradeable pairs (B, C) if
        the exchange supports markets (A_B or B_A) and (B_C or C_B) and (C_A or A_C).
        """
        xchg = self.broker.xchg
        pairs = []
        big_coins = xchg.get_major_currencies()

        for curr1 in big_coins:
            for curr2 in big_coins:
                if curr1 >= curr2:
                    continue
                if xchg.get_validated_pair((target, curr1)) is not None \
                        and xchg.get_validated_pair((target, curr2)) is not None \
                        and xchg.get_validated_pair((curr1, curr2)) is not None:
                    pairs.append((curr1, curr2))
                    self.log.info("Selected a pair: ({}, {})".format(curr1, curr2))
        return pairs

    def init_cross_markets(self):
        """
        stores which orderbook depths to also update when
        calculating spreads for a single pair
        cross-markets data structure:
        {
        'Vircurex' : {
                'A_B' : ['C',etc.] # A_B is the pair that we wish to trade
                'D_E' : ['F','G', etc.]
            },
        etc.
        }
        """
        self.cross_market_pairs = {}
        self.update_pairs = {}
        for target in self.targets:
            self.cross_market_pairs[target] = self.get_roundtrip_pairs(target)
            self.update_pairs[target] = []
            for curr1, curr2 in self.cross_market_pairs[target]:
                self.update_pairs[target].append((target, curr1))
                self.update_pairs[target].append((target, curr2))
                self.update_pairs[target].append((curr1, curr2))
            self.log.info("Update pairs for {}: {}".format(target, self.update_pairs[target]))

    def tick(self):
        """
        instead of looping over each pair, it makes more sense to trade one broker at a time
        (otherwise if we update all the brokers first and then trade each pair, slippage time increases!)
        """
        self.log.info('%s tick %s' % (time.strftime('%b %d, %Y %X'), self.broker.xchg.name))
        self.broker.clear()
        # we could update the ENTIRE depth here but
        # it turns out that some exchanges trade FAR more currencies than we want to see.
        # better to just update on each pair we trade (after all, we affect the orderbook)
        for target in self.targets:
            self.broker.update_multiple_depths(self.update_pairs[target])
            if self.trading_enabled:
                self.trade_pair(self.broker, target)

    def trade_pair(self, broker, target):
        """
        unlike the cross-exchange arbitrage bot, this one only trades
        one exchange at a time!
        """
        pc = TriangleProfitCalculator(broker, target, self.cross_market_pairs[target])
        # type1 and type2 roundtrips are in fact completely mutually exclusive!
        # that means that if we detect both type1 and type2 roundtrips, we can simultaneously
        # execute both without worrying about moving the market.
        if pc.check_profits():
            pc.get_best_roundtrip()
            # submit each order in sequence.

            # if order_triplet is not None:
            #    print('Type%d Arbitrage Opportunity Detected!' % type)
            # submit each order

            # triplet = pc.get_best_roundtrip()
            # for (bidder, order) in triplet:
            # for now, just print the order, test to see if you can execute manually.
            # order_id, t = bidder.submit(order)

            # production TODO - each broker automatically cancels orders if they don't go through.
            # while not bidder.confirm_order(order_id):
            #     if time.time() - t > 3:
            #         error = bidder.order_error(order_id)
            #     else:
            #         print('round trip incurred an error')

            # wait
            # if time > threshold, swallow losses
            # and cancel this one
            # and don't submit all remaining orders
