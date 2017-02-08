from threading import Thread

import config_tri as config
from TriangularBot import TriangularBot
from utils_broker import create_broker


def thread_bot(conf, broker, targets):
    bot = TriangularBot(conf, broker, targets)
    bot.start(config.TICK_PERIOD)

for xchg in config.EXCHANGES:
    broker = create_broker('PAPER', xchg)
    t = Thread(target=thread_bot, args=(config, broker, config.TARGETS[xchg]))
    t.start()
