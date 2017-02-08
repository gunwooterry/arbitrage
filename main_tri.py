import config_tri as config
from TriangularBot import TriangularBot

if __name__ == "__main__" :
    for xchg in config.EXCHANGES:
        TriangularBot(xchg, config.TARGETS[xchg], config.TICK_PERIOD).start()
