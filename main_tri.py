from TriangularArbitrageBot import TriangularArbitrageBot
from utils_broker import create_broker
import config_tri as config
from threading import Thread


def thread_bot(conf, brks, pairs):
    bot = TriangularArbitrageBot(conf, [brks], pairs)
    bot.start(5)

for xchg in config.EXCHANGES:
    broker = create_broker('PAPER', xchg)
    t = Thread(target=thread_bot, args=(config, broker, config.PAIRS[xchg]))
    t.start()
