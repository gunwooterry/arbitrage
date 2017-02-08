import logging

import utils


class TriangularCalculator(object):
    """
    Profit calculator for single-exchange triangular arbitrage, trading
    minimum arbitrage volumes.
    all this data will be computed for a SINGLE exchange SINGLE pair
    (by single pair, I am referring to the start/end currencies of the arbitrage).
    therefore, data structures are different from PairwiseCalculator
    """

    def __init__(self, broker, target, roundtrip_pairs):
        self.broker = broker
        self.target = target
        self.roundtrip_pairs = roundtrip_pairs
        """
        self.spreads take the form of {'X_Y' : 0.1245, 'V_W' : 0.54321}
        """
        self.spreads = {}
        """
        self.roundtrips take the form of
        {
            'X_Y' : {
                'orders' : [<Order>,<Order>,<Order>]
                'profit' : 12.345
            },
            'V_W' : {
                'orders' :
                'profit' :
            }
        }
        """
        self.roundtrips = {}

        self.log = logging.getLogger(broker.xchg.name)

    def check_profits(self):
        """
        returns True if profitable round-trip exists between any 3 currencies.
        checks for spread between implied_hi_bid and market lo_ask
        """
        is_profitable = False

        for B, C in self.roundtrip_pairs:
            if self.check_profit_oneway(self.target, B, C) > 1 or \
                            self.check_profit_oneway(self.target, C, B) > 1:
                is_profitable = True
        return is_profitable

    def check_profit_oneway(self, A, B, C):
        """
        Calculates 'spread' of a given roundtrip (A, B, C)
        Accumulates profits on A (commonly BTC)
        Spread : expected gain of A, when 1A investigated.
        double check_profit_oneway(str A, str B, str C)
        """
        tx = 1 - self.broker.xchg.trading_fee

        # P_XY_Sell : price of 1X with respect to Y when we sell X
        P_AB_Sell = self.broker.get_highest_bid((A, B))
        P_BC_Sell = self.broker.get_highest_bid((B, C))
        P_CA_Sell = self.broker.get_highest_bid((C, A))

        # Exception Handling
        if not P_AB_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(A, B))
            return False
        if not P_BC_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(B, C))
            return False
        if not P_CA_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(C, A))
            return False

        # Calculate spread
        spread = P_AB_Sell * P_BC_Sell * P_CA_Sell * (tx * tx * tx)
        slug = B + '_' + C
        self.spreads[slug] = spread

        return spread

    def check_roundtrip(self, A, B, C):
        """
        Calculates minimum profit of a given roundtrip (A, B, C)
        Accumulates profits on A (commonly BTC)
        Minimum Profit : expected gain of A when minimum volume requirements for trades are 'tightly' satisfied.
        double check_roundtrip(str A, str B, str C)
        """
        tx = 1 - self.broker.xchg.trading_fee

        # O_XY_Sell : Order list of X_Y to sell (bids)
        O_AB_Sell = self.broker.get_orders((A, B), 'bids')
        O_BC_Sell = self.broker.get_orders((B, C), 'bids')
        O_CA_Sell = self.broker.get_orders((C, A), 'bids')

        if not O_AB_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(A, B))
            return False
        if not O_BC_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(B, C))
            return False
        if not O_CA_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(C, A))
            return False

#         self.log.info('============================')
#         for o in O_AB_Sell :
#             self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
#         self.log.info('============================')
#         for o in O_BC_Sell :
#             self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
#         self.log.info('============================')
#         for o in O_CA_Sell :
#             self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
#         self.log.info('============================')

        # min_XY : Minimum volume requirement for X, in the corresponding volume of Y
        min_AA = self.broker.xchg.get_min_vol((A, B), O_AB_Sell)
        min_BB = self.broker.xchg.get_min_vol((B, C), O_BC_Sell)
        min_CC = self.broker.xchg.get_min_vol((C, A), O_CA_Sell)

        # P_XY_Sell : price of 1X with respect to Y when we sell X
        P_AB_Sell = self.broker.get_highest_bid((A, B))
        P_BC_Sell = self.broker.get_highest_bid((B, C))
        P_CA_Sell = self.broker.get_highest_bid((C, A))

        if not P_AB_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(A, B))
            return False
        if not P_BC_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(B, C))
            return False
        if not P_CA_Sell:
            self.log.info('Empty {}_{} bid orders, skipping...'.format(C, A))
            return False

        # Now we transform minBB to minBA, minCC to minCB to minCA to compare.
        min_BA = min_BB / P_AB_Sell / tx
        min_CA = min_CC / P_BC_Sell / P_AB_Sell / tx / tx

        # V : Minimum volume of A which satisfies minimum volume requirements for trades
        # Margin for precision error
        V = max(min_AA, min_BA, min_CA) * 1.01

        max_AA = O_AB_Sell[0].v
        max_BB = O_BC_Sell[0].v
        max_CC = O_CA_Sell[0].v
        
        max_BA = max_BB / P_AB_Sell / tx
        max_CA = max_CC / P_BC_Sell / P_AB_Sell / tx / tx
        
        W = min(max_AA, max_BA, max_CA) * 0.99
        
        # O_XY_Sell_Clipped : Clipped Order list of X_Y to sell (bids)
        O_AB_Sell_Clipped = self.broker.xchg.get_clipped_base_volume(O_AB_Sell, V)
        O_BC_Sell_Clipped = self.broker.xchg.get_clipped_base_volume(O_BC_Sell,
                                                                     utils.total_alt_volume(O_AB_Sell_Clipped) * tx)
        O_CA_Sell_Clipped = self.broker.xchg.get_clipped_base_volume(O_CA_Sell,
                                                                     utils.total_alt_volume(O_BC_Sell_Clipped) * tx)

        self.log.info('============================')
        for o in O_AB_Sell_Clipped :
            self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
        self.log.info('============================')
        for o in O_BC_Sell_Clipped :
            self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
        self.log.info('============================')
        for o in O_CA_Sell_Clipped :
            self.log.info('(price:{}, volume:{})'.format(o.p, o.v))
        self.log.info('============================')
        
        if not O_AB_Sell_Clipped:
            return False
        if not O_BC_Sell_Clipped:
            return False
        if not O_CA_Sell_Clipped:
            return False

        netA = utils.total_alt_volume(O_CA_Sell_Clipped) * tx - utils.total_base_volume(O_AB_Sell_Clipped)
        netB = utils.total_alt_volume(O_AB_Sell_Clipped) * tx - utils.total_base_volume(O_BC_Sell_Clipped)
        netC = utils.total_alt_volume(O_BC_Sell_Clipped) * tx - utils.total_base_volume(O_CA_Sell_Clipped)

        slug = B + '_' + C
        self.roundtrips[slug] = {}
        self.roundtrips[slug]['profit'] = netA

        self.log.info('check_roundtrip({}, {}, {}) : {} BTC'.format(A, B, C, netA))
        self.log.info('    netA : {}'.format(netA))
        self.log.info('    netB : {}'.format(netB))
        self.log.info('    netC : {}'.format(netC))
        self.log.info('    Volume : {} ~ {}'.format(V, W))
        self.log.info('    P_AB_Sell : {}'.format(P_AB_Sell))
        self.log.info('    P_BC_Sell : {}'.format(P_BC_Sell))
        self.log.info('    P_CA_Sell : {}'.format(P_CA_Sell))

        return netA

    def get_best_roundtrip(self):
        """
        Calculate the optimal roundtrip for you to execute
        Takes the form of 3 trades that are computed to fill specific quantities of orders
        in each of 3 different markets in a single exchange.
        """
        for slug, spread in self.spreads.items():
            # Risk avoidance threshold 0.1%
            B = slug.split('_')[0]
            C = slug.split('_')[1]
            if spread > 1:
                self.log.info('check_profit_oneway({}, {}, {}) : {}'.format(self.target, B, C, spread))
            if spread > 1.001:
                self.log.info('check_roundtrip({}, {}, {}) : {}'.format(self.target, B, C,
                                                                        self.check_roundtrip(self.target, B, C)))

        #TODO: Return orders to place
