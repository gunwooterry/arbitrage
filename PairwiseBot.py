# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

import threading
from itertools import combinations

from Bot import Bot
from PairwiseCalculator import PairwiseCalculator
from utils_broker import create_broker


# Requires HTTP connection
def update_possible_pairs(xchg, possible_pairs):
    """
    Return major currency pairs available in the exchange
    """
    majors = xchg.get_major_currencies()
    pairs = []
    for a, b in combinations(majors, 2):
        if xchg.get_validated_pair((a, b)) is not None:
            pairs.append(frozenset([a, b]))
    possible_pairs[xchg] = pairs


class PairwiseBot(Bot):
    def __init__(self, xchg_names, sleep):
        Bot.__init__(self, "Pairwise", sleep)
        self.brokers = [create_broker('PAPER', name, "Pairwise") for name in xchg_names]
        self.possible_pairs = {}
        self.shared_pairs = {}  # shared_pairs[(X, Y)] is a list of pairs (A, B) shared by two exchanges
        self.pairs_to_update = {}  # pairs_to_update[X] is a list of pairs to update for one exchange

    def init(self):
        self.update_pairs()

    def tick(self):
        self.log.info("tick")
        threads = [broker.update_multiple_depths(self.pairs_to_update[broker.xchg]) for broker in self.brokers]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.trade_pair()

    def update_pairs(self):
        exchanges = [broker.xchg for broker in self.brokers]
        possible_pairs = {}

        threads = [threading.Thread(target=update_possible_pairs, args=(xchg, possible_pairs)) for xchg in exchanges]
        [t.start() for t in threads]
        [t.join() for t in threads]
        print(possible_pairs)

        for xchg in exchanges:
            self.pairs_to_update[xchg] = set()

        for x, y in combinations(exchanges, 2):
            self.shared_pairs[frozenset([x, y])] = list(
                set.intersection(set(possible_pairs[x]), set(possible_pairs[y])))
            for p in self.shared_pairs[frozenset([x, y])]:
                self.pairs_to_update[x].add(p)
                self.pairs_to_update[y].add(p)

        for xchg in exchanges:
            self.pairs_to_update[xchg] = list(self.pairs_to_update[xchg])

    def trade_pair(self):
        pc = PairwiseCalculator(self.brokers, self.pairs_to_update, self.shared_pairs, self.logger_name)
        if pc.check_profits():
            pc.get_best_trade()
