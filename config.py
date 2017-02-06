#
# Global user settings
# DO NOT let this file fall into the wrong hands!

TICK_DIR = './data'  # path to folder containing serialized historical tick data

# reference values in USD for each currency
# this is approximate. Unless values are a magnitude away from true values, I should be fine
# The main_pair purpose of this is to just pass by opportunities that net insignificant profit
VALUE_REF = {
    'BTC': 1023.0,  # bitcoin
    'LTC': 4.03,  # litecoin
    'DOGE': 0.00021,  # dogecoin
    'PPC': 0.30,  # peercoin
    'NMC': 0.25,  # namecoin
    'QRK': 0.00154,  # quarkcoin
    'NXT': 0.01,  # nxt
    'WDC': 0.00325,  # worldcon
    'ETH': 11.0,
    'CNY': 0.1455,
}

# I use this in arbitrage -> do not attempt trade unless profit > 1 cent
# PROFIT_THRESH = {k: 0.01 / v for k, v in VALUE_REF.items()}
PAPER_BALANCE = {k: 20 / v for k, v in VALUE_REF.items()}  # for 7 exchanges, have

# a better metric of whether I should go after a trade or not should be instead based on
# the amount of money I have to move to perform the trade.
# i.e. I don't want to move 1.0 BTC (1000 USD) just to profit 1 cent!!!
# BTC risk is how much BTC I expect to profit per BTC I move.
# In a paired trade, I'm really moving twice as much value on both ends.
# as you grow more confident in the stability of the trading bot, you can increase riskiness by decreasing this number.
BTC_RISK = 0.001

keys_dir = "exchanges/keys/"
# BTER API
BTER_KEYFILE = keys_dir + "bter_key.txt"
# POLONIEX API
POLO_KEYFILE = keys_dir + "poloniex_key.txt"
