import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests
from func_messages import *
def prepare_account(old_message, exchange, symbol, order_params=None):
    """
    
    ** Prepare the account for trading **
    ** Set the leverage for the symbol **
    ** Close any open positions for the symbol -- Closes LONG or SHORT or BOTH**
    ** Set the testnet flag for the exchange **
    ** Set the telegram bot flag for the exchange **
    ** Converts account to a hedge mode on symbol **

    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - json object with all the order parameters
    :return: None

    """

    message = ""
    try:
        if order_params is None:
            raise ValueError("order_params cannot be None")
        #symbol = order_params.get('coin_pair')
        buy_leverage = order_params.get('buy_leverage')
        sell_leverage = order_params.get('sell_leverage')
        testnet = order_params.get('use_testnet')
        telegram_bot = order_params.get('telegram_bot')
        exit_existing_trade = order_params.get('exit_existing_trade')
        margin_mode = order_params.get('margin_mode')


        if buy_leverage is None or sell_leverage is None or testnet is None:
            raise ValueError("order_params is missing required parameters")
    except Exception as e:
        print("Problem setting prepare account: {}".format(str(e)))
        #old_message = append_messages_new(old_message, message)
        pass

    try:
        if testnet == "1":
            exchange.set_sandbox_mode(True)
    except Exception as e:
        print("Problem setting to testnet: {}".format(str(e)))
        message = config.CANT_SET_TESTNET
        old_message = append_messages_new(old_message, message)
        pass

    # Switch margin
    try:
        if margin_mode == "1" or margin_mode == 1:
            #set_margin_mode(self, marginMode, symbol=None, params={}):
            exchange.set_margin_mode(config.ISOLATED_MARGIN_MODE_KEYWORD, symbol,  params={"symbol": symbol,"marginCoin": "USDT","marginMode": config.ISOLATED_MARGIN_MODE_KEYWORD})
        elif margin_mode == "0" or margin_mode == 0:
            exchange.set_margin_mode(config.CROSSED_MARGIN_MODE_KEYWORD, symbol,  params={"symbol": symbol,"marginCoin": "USDT","marginMode": config.CROSSED_MARGIN_MODE_KEYWORD})

    except Exception as e:
        print("Problem setting margin mode: {}".format(str(e)))
        message = config.CANT_SET_MARGIN_MODE
        #old_message = append_messages_new(old_message, message)
        pass




    # Set leverage
    try:
        exchange.set_leverage(buy_leverage, symbol, params={"symbol":symbol,"marginCoin": "USDT","leverage": buy_leverage, "holdSide": "long"} )
        exchange.set_leverage(sell_leverage, symbol,params={"symbol": symbol,"marginCoin": "USDT","leverage": sell_leverage, "holdSide": "short"}  )
    except Exception as e:
        print("Problem setting leverage: {}".format(str(e)))
        message = config.CANT_SET_LEVERAGE
        old_message = append_messages_new(old_message, message)
        pass


    return True


def get_wallet_balance(exchange):
    try:
        wallet = exchange.fetch_balance()
        usdt_balance = float(wallet['USDT']['free'])
    
    except Exception as e:
        print("Unable to get wallet balance {}".format(str(e)))
        #old_message = append_messages_new(old_message, message)
        return False
    return float(usdt_balance)


def usdt_balance_more_than_threshold(usdt_balance, order_params=None):

    try:
        
        usdt_balance = usdt_balance
        stop_bot_below_balance = order_params.get('stop_bot_below_balance')
       
       
        if stop_bot_below_balance is None or stop_bot_below_balance is "" :
            stop_bot_below_balance = 0

        if usdt_balance is None or usdt_balance is "" :
            usdt_balance = 0

    except Exception as e:
        warning_message("Unable to get wallet balance {}".format(str(e)))
        return False
    
    try:
        if float(usdt_balance) < 1:
            stop_the_bot = True
            message = f"Hi {email_id}, Can't initiate the trade! Wallet balance(USDT) is below 1!"

        else:
            stop_the_bot = False
    except Exception as e:
        warning_message("Less than one dollar {}".format(str(e)))
        return False
    
    try:
        # Stop bot if balance is below user defined reserve amount
        if float(stop_bot_below_balance) > 0:
            if usdt_balance < float(stop_bot_below_balance):
                stop_the_bot = True
                message = f"Hi {email_id}, Can't initiate the Trade! Wallet balance is below the reserved amount!"
            else:
                stop_the_bot = False

    except Exception as e:
        warning_message("Threshold wallet problems {}".format(str(e)))
        return False

    return stop_the_bot