# generic class for trading/market-watching bots

# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

import abc
import logging
import logging.handlers
import time
from threading import Thread


class Bot(Thread):
    def __init__(self, name, sleep):
        self.error = False
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.INFO)
        self.sleep = sleep
    
    def getLogger(self):
        return self.log
    
    def kill(self):
        self.error = True

    def run(self):
        start = time.time()
        last_tick = start - self.sleep
        while not self.error:
            delta = time.time() - last_tick
            if delta < self.sleep:
                # sleep for the remaining seconds
                time.sleep(self.sleep - delta)
            last_tick = time.time()
            self.tick()

    @abc.abstractmethod
    def tick(self):
        return NotImplemented
