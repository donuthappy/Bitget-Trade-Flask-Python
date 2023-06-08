
USDT_PAIR_ENDING = "_UMCBL" # for example: BTC_USDT becomes BTC_USDT_UMCBL in the exchange bitget or BTCUSDT becomes BTCUSDT.P in the exchange bybit // see perpare_symbol() in main.py


"""
Here I would like to add the error and warning messages to a list and then send them to telegram at the end of the function.
This way I can send all the error messages at once instead of one by one.
"""


CANT_CONNECT = "Can't connect to the exchange."
CANT_SET_LEVERAGE = "Can't set leverage for this exchange."
CANT_SET_MARGIN_MODE = "Can't set margin mode to isolated for this exchange."

CANT_SET_TESTNET = "Problem setting to testnet"

DEBUG = False

CROSSED_MARGIN_MODE_KEYWORD = "crossed"
ISOLATED_MARGIN_MODE_KEYWORD = "fixed"