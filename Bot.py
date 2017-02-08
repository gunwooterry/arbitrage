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
        self.logger_name = name
        self.error = False
        self.log = logging.getLogger(self.logger_name)
        self.log.setLevel(logging.INFO)
        file_handler = logging.FileHandler('./log/{}.log'.format(self.logger_name))
        stream_handler = logging.StreamHandler()
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_handler)
        self.sleep = sleep
    
    def kill(self):
        self.error = True

    def init(self):
        pass

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

    @abc.abstractmethod
    def tick(self):
        return NotImplemented
