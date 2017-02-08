import config_tri as config
from TriangularBot import TriangularBot

for xchg in config.EXCHANGES:
    TriangularBot(xchg, config.TARGETS[xchg], config.TICK_PERIOD).start()
