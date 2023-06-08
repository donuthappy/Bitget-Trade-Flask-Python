import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests

from pprint import pprint

def get_latest_price(exchange, symbol):
    """
    ** Get the latest price for a symbol **
    ** Used to get the latest price for a symbol to enter a trade **

    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to get the latest price for
    :return: Last price, ask price, bid price
    """

    ticker = exchange.fetch_ticker(symbol)

    last_price = ticker['last']
    ask_price = ticker['ask']
    bid_price = ticker['bid']
    return last_price, ask_price, bid_price

