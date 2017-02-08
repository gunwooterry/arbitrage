from PairwiseBot import PairwiseBot
import config_tri as config

bot = PairwiseBot(config.EXCHANGES, 2)
bot.init()