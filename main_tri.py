from threading import Thread

import config_tri as config
from TriangularBot import TriangularBot
from utils_broker import create_broker


def thread_bot(conf, brks, pairs):
    bot = TriangularBot(conf, [brks], pairs)
    bot.start(5)

for xchg in config.EXCHANGES:
    broker = create_broker('PAPER', xchg)
    t = Thread(target=thread_bot, args=(config, broker, config.PAIRS[xchg]))
    t.start()
