import copy


def get_swapped_order(order):
    # given a bid/ask price and volume being bought/sold,
    # return the same order but as units of the reverse market.
    c = copy.copy(order)
    alts_per_base = order.p
    vol_base = order.v
    c.v = vol_base * alts_per_base
    c.p = 1.0 / alts_per_base
    return c


highest_price = lambda arr: max([o.p for o in arr])
lowest_price = lambda arr: min([o.p for o in arr])
total_base_volume = lambda arr: sum([o.v for o in arr])
total_alt_volume = lambda arr: sum([o.p * o.v for o in arr])
