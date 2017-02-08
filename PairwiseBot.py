# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

from itertools import combinations
import itertools
import time

from Bot import Bot
from PairwiseCalculator import PairwiseCalculator
from utils_broker import create_broker


class PairwiseBot(Bot):
    def __init__(self, xchg_names, sleep):
        Bot.__init__(self, "Pairwise", sleep)
        self.brokers = [create_broker('PAPER', name, "Pairwise") for name in xchg_names]
        self.shared_pairs = {}          # shared_pairs[(X, Y)] is a list of pairs (A, B) shared by two exchanges
        self.pairs_to_update = {}       # pairs_to_update[X] is a list of pairs to update for one exchange

    def init(self):
        self.update_pairs()

    def tick(self):
        self.log.info("{} tick".format(time.strftime('%b %d, %Y %X')))

    # Requires HTTP connection
    def get_possible_pairs(self, xchg):
        """
        Return major currency pairs available in the exchange
        """
        majors = xchg.get_major_currencies()
        pairs = []
        for a, b in combinations(majors, 2):
            if xchg.get_validated_pair((a, b)) is not None:
                pairs.append(frozenset([a, b]))
        return pairs

    def update_pairs(self):
        exchanges = [broker.xchg for broker in self.brokers]
        # possible_pairs is only required in this initialization step
        possible_pairs = {}
        
        for xchg in exchanges:
            self.pairs_to_update[xchg] = set()
            possible_pairs[xchg] = self.get_possible_pairs(xchg)
        
        print(possible_pairs)
        
        for x, y in combinations(exchanges, 2):
            self.shared_pairs[frozenset([x, y])] = list(set.intersection(set(possible_pairs[x]), set(possible_pairs[y])))
            for p in self.shared_pairs[frozenset([x, y])] :
                self.pairs_to_update[x].add(p)
                self.pairs_to_update[y].add(p)
            
        for x in exchanges :
            self.pairs_to_update[x] = list(self.pairs_to_update[x])

    def trade_pair(self, pair):
        # - initial test - compare high_bid and low_ask prices
        # - if spread is positive, fetch market depth and re-assess arb opportunity
        base, alt = pair
        pc = PairwiseCalculator(self.brokers, pair)
        if pc.check_profits():
            (bidder, asker, profit_obj) = pc.get_best_trade()
            bidder_order = profit_obj["bidder_order"]
            asker_order = profit_obj["asker_order"]
            bidder_tx = 1.0 - bidder.xchg.trading_fee
            asker_tx = 1.0 - asker.xchg.trading_fee
            if self.config.MODE == 'PAPER':
                bidder.balances[base] -= bidder_order.v
                bidder.balances[alt] += bidder_order.p * bidder_order.v * bidder_tx
                asker.balances[base] += asker_order.v * asker_tx
                asker.balances[alt] -= asker_order.p * asker_order.v
                print('Success! Bought %f %s for %f %s from %s and sold %f %s for %f %s at %s' %
                      (asker_order.v * asker_tx, base, asker_order.p * asker_order.v, alt, asker.xchg.name,
                       bidder_order.v, base, bidder_order.p * bidder_order.v * bidder_tx, alt, bidder.xchg.name))
                print('Profit : %f %s' % (
                    bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))
            else:
                # live trade - do this manually for now!
                print(
                    'Profitable Arbitrage Opportunity Detected!! Buy %f %s for %f %s from %s and sell %f %s for %f %s at %s' %
                    (asker_order.v * asker_tx, base, asker_order.p * asker_order.v, alt, asker.xchg.name,
                     bidder_order.v, base, bidder_order.p * bidder_order.v * bidder_tx, alt, bidder.xchg.name))
                print('Profit : %f %s' % (
                    bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))

            # asker.buy(pair, asker_order.p, asker_order.v)
            # bidder.sell(pair, bidder_order.p, bidder_order.v)
