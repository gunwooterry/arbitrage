import config_tri as config
from TriangularBot import TriangularBot
from utils_broker import create_broker

for xchg in config.EXCHANGES:
    broker = create_broker('PAPER', xchg)
    TriangularBot(broker, config.TARGETS[xchg], config.TICK_PERIOD).start()
