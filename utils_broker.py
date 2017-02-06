from Broker import Broker
from exchanges.BTER import BTER
from exchanges.Poloniex import Poloniex

import config


# Broker utils
def create_broker(mode, xchg_name):
    # returns an array of Broker objects
    if xchg_name == 'BTER':
        xchg = BTER(config.BTER_KEYFILE)
    elif xchg_name == 'POLO':
        xchg = Poloniex(config.POLO_KEYFILE)
    else:
        print('Exchange ' + xchg_name + ' not supported!')
        return None

    broker = Broker(mode, xchg)
    if mode == 'LIVE':
        broker.balances = broker.xchg.get_all_balances()  # use real starting balances.
    if mode == 'PAPER':
        broker.balances = config.PAPER_BALANCE
    return broker


def get_assets(brokers):
    # prints out total assets held across all brokers
    assets = {}
    for broker in brokers:
        for currency, balance in broker.balances.items():
            if currency in assets:
                assets[currency] += balance
            elif balance > 0.0:
                assets[currency] = balance
    return assets


def print_assets(brokers):
    print(get_assets(brokers))
