import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests



def connect_to_exchange(old_message, order_params=None):
    """
    ** Connect to the exchange and return the exchange object **

    :param old_message: The error message
    :param order_params: dict of order parameters from the JSON request
    :return: exchange object

    """
    if order_params is None:
        print("No order parameters provided")
        return None

    api_key = order_params.get('api_key')
    secret_key = order_params.get('secret_key')
    passphrase = order_params.get('passphrase')

    if not api_key or not secret_key or not passphrase:
        print("Missing required authentication parameters")
        return None

    exchange = None
    try:
        exchange = ccxt.bitget({
            "enableRateLimit": True,
            'apiKey': api_key,
            'secret': secret_key,
            'password': passphrase,
            'options': {
                'defaultType': 'swap',
                'defaultIsolated': True,
            }
        })
        information = exchange.load_markets() #TODO: check if this is needed
   

    except Exception as e:
        message = config.CANT_CONNECT
        old_message = append_messages_new(old_message, message)
        print("Error connecting to exchange: {}".format(str(e)))
        return None

    return exchange, information
