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
        Thread.__init__(self)
        self.error = False
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.INFO)
        file_handler = logging.FileHandler('./log/{}.log'.format(name))
        stream_handler = logging.StreamHandler()
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_handler)
        self.sleep = sleep

    @abc.abstractmethod
    def init(self):
        pass

    @abc.abstractmethod
    def tick(self):
        return NotImplemented

    def get_logger(self):
        return self.log
    
    def kill(self):
        self.error = True



    def run(self):
        self.init()
        
        start = time.time()
        last_tick = start - self.sleep
        while not self.error:
            delta = time.time() - last_tick
            if delta < self.sleep:
                # sleep for the remaining seconds
                time.sleep(self.sleep - delta)
            last_tick = time.time()
            self.tick()
