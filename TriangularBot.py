# Triangular Arbitrage Bot
# SINGLE exchange algorithm -> allows for near-instantaneous arbitrage without
# necessitating positions in multiple currencies.

from itertools import combinations

from Bot import Bot
from TriangularCalculator import TriangularCalculator
from utils_broker import create_broker


class TriangularBot(Bot):
    def __init__(self, xchg_name, targets, sleep):
        # TriangularBot only trades on ONE broker
        Bot.__init__(self, 'TriangularBot[{}]'.format(xchg_name), sleep)
        self.broker = create_broker('PAPER', xchg_name, self.logger_name)
        self.targets = targets
        self.available_pairs = {}           # available_pairs[A] is a list of all possible (B, C)
        self.pairs_to_update = {}           # pairs_to_update[A] is [(A, B), (B, C), (C, A), (A, B'), ...]

    def init(self):
        self.update_pairs()

    def tick(self):
        # Instead of looping over each pair, it makes more sense to trade one broker at a time
        # (Otherwise if we update all the brokers first and then trade each pair, slippage time increases!)
        self.log.info("tick")
        self.broker.clear()
        # We could update the ENTIRE depth here,
        # but it turns out that some exchanges trade FAR more currencies than we want to see.
        # Better to just update on each pair we trade (after all, we affect the orderbook)
        for target in self.targets:     # This loop is actually only ONE iteration
            self.broker.update_multiple_depths(self.pairs_to_update[target])
            self.trade_tri(self.broker, target)

    # Requires HTTP connection
    def get_roundtrip_pairs(self, target):
        """
        Given currency A, returns an array of all tradeable pairs (B, C) but not (C, B)
        if the exchange supports markets (A_B or B_A) and (B_C or C_B) and (C_A or A_C).
        """
        xchg = self.broker.xchg
        pairs = []
        majors = xchg.get_major_currencies()

        for b, c in combinations(majors, 2):
            if xchg.get_validated_pair((target, b)) is not None \
                    and xchg.get_validated_pair((target, c)) is not None \
                    and xchg.get_validated_pair((b, c)) is not None:
                pairs.append((b, c))
                self.log.info("Selected a pair: ({}, {})".format(b, c))
        return pairs

    def update_pairs(self):
        """
        Stores which orderbook depths to also update when calculating spreads for a single pair
        """
        for target in self.targets:
            self.available_pairs[target] = self.get_roundtrip_pairs(target)
            self.pairs_to_update[target] = []
            for b, c in self.available_pairs[target]:
                self.pairs_to_update[target].append((target, b))
                self.pairs_to_update[target].append((target, c))
                self.pairs_to_update[target].append((b, c))
            self.log.info("Update pairs for {}: {}".format(target, self.pairs_to_update[target]))

    def trade_tri(self, broker, target):
        # This bot only trades on one exchange at a time
        pc = TriangularCalculator(broker, target, self.available_pairs[target], self.logger_name)
        if pc.check_profits():
            pc.get_best_roundtrip()

        # TODO: Submit order
        # TODO: Each broker automatically cancels orders if they don't go through.
