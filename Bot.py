# generic class for trading/market-watching bots

# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

import abc
import logging
import logging.handlers
import threading
import time
from os.path import abspath


class Bot(object):
    def __init__(self, config, brokers):
        """
        config = configuration file
        brokers = array of broker objects
        """
        super(Bot, self).__init__()
        self.config = config
        self.brokers = brokers
        self.error = False
        self.log = logging.getLogger("default bot")
        self.log.setLevel(logging.INFO)
        self.backtest_data = None
        self.max_ticks = 0
        self.data_path = abspath(config.TICK_DIR)
        self.trading_enabled = True
        self.tick_i = 0

    def start(self, sleep=0):
        start = time.time()
        last_tick = start - sleep
        while not self.error:
            delta = time.time() - last_tick
            if delta < sleep:
                # sleep for the remaining seconds
                time.sleep(sleep - delta)
            last_tick = time.time()
            self.tick()

    def trade_tri(self, broker, target):
        pass

    def trade_pair(self, pair):
        pass

    @abc.abstractmethod
    def tick(self):
        """
        self.log.info('%s tick' % (time.strftime('%b %d, %Y %X %Z'),))
        for broker in self.brokers:
            # clear data so that if API call fails, we don't mistakenly
            # report last tick's data
            broker.clear()
        for pair in self.config.PAIRS:
            # print('fetching xchg data for %s' % (pair,))
            # multithreaded update of the pair on each exchange
            if self.config.USE_MULTITHREADED:
                threads = []
                threadLock = threading.Lock()
                for broker in self.brokers:
                    # multithreaded update balance
                    # balance_thread = UpdateBalanceThread(broker)
                    # balance_thread.start()
                    # threads.append(balance_thread)
                    # multithreaded update depth
                    depth_thread = UpdateDepthThread(broker, pair, self.backtest_data, self.tick_i)
                    depth_thread.start()
                    threads.append(depth_thread)
                for t in threads:
                    t.join()  # wait for all update threads to complete
                    # elapsed = time.time() - start
                    # print('Broker update finished in %d ms' % (elapsed * 1000))
            else:
                # single threaded update
                for broker in self.brokers:
                    # broker.balances = broker.xchg.get_all_balances()
                    # print(broker.xchg.name)
                    broker.update_all_balances()
                    if broker.xchg.get_validated_pair(pair) is not None:
                        if self.backtest_data is not None:
                            broker.update_depth(pair, self.backtest_data, self.tick_i)
                        else:
                            broker.update_depth(pair)
            # custom function for each trading bot to implement
            # the default implementation is to do nothing - useful in situations like
            # data gathering
            if self.trading_enabled:
                self.trade_pair(pair)
        """
        return NotImplemented
