from threading import Thread

import config_pair as config
from PairwiseBot import PairwiseBot
from utils_broker import create_broker


def thread_bot(conf, brks, pairs):
    bot = PairwiseBot(conf, [brks])
    bot.start(config.TICK_PERIOD)

for xchg in config.EXCHANGES:
    broker = create_broker('PAPER', xchg)
    t = Thread(target=thread_bot, args=(config, broker, config.PAIRS[xchg]))
    t.start()
