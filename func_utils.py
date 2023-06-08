import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests
from datetime import datetime, timedelta
from func_messages import *
from pprint import pprint


import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import pbkdf2_hmac

from time import sleep, time




def get_position_value(exchange, symbol, order_params=None):
    """
    ** Checks if the user has an active position **
    ** If the user has an active position, WITHOUT SIDE **
    
    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - passed through the prepare_symbol() function
    :return: Trade amount
    """
    order = exchange.fetch_positions(symbols=[symbol])

    buy_active_qty = order['result'][0]['size']
    buy_value = order['result'][0]['positionValue']

    sell_active_qty = order['result'][1]['size']
    sell_value = order['result'][1]['positionValue']

    if float(buy_active_qty) > 0:
        return buy_value
    elif float(sell_active_qty) > 0:
        return sell_value
    else:
        return 0

def get_position_value_with_side(exchange, symbol, order_params=None):
    """
    ** Checks if the user has an active position **
    ** If the user has an active position, check if the position is the same side as the order **
    
    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - passed through the prepare_symbol() function
    :return: Trade amount
    """
    try:
        order = exchange.fetch_positions(symbols=[symbol])
    except Exception as e:
        print(e)

    try:
        sleep(1)
        side = order_params.get('side')
        positions = exchange.fetch_positions(symbols=[symbol])

        total_margin = 0.0
        for position in positions:
            if position['symbol'] == symbol:
                total_margin += position['info']['collateral']
        
        _active_qty = 0.0
        _value = total_margin
            
    except Exception as e:
        warning_message(f"Error getting position size: {str(e)}")
        _value = 0.0

    print('Order qty', _value)
    if float(_value) > 0:
        return _value
    else:
        return 0

def check_positions(exchange, symbol, order_params=None):
    """
    ** Checks if the user has an active position **
    ** If the user has an active position, check if the position is the same side as the order **
    
    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - passed through the prepare_symbol() function
    :return: Trade amount
    """    

    
    order = exchange.fetch_positions(symbols=[symbol])


    buy_info = order[0]['info']
    buy_side = buy_info['side']
    buy_active_qty = buy_info['size']

    sell_info = order[1]['info']
    sell_side = sell_info['side']
    sell_active_qty = sell_info['size']
    if float(buy_active_qty) > 0:
        return float(buy_active_qty), buy_side
    elif float(sell_active_qty) > 0:
        return float(sell_active_qty), sell_side
    else:
        return 0, 0



def decrypter(salt, encrypted_key, passphrase):
  salt = base64.b64decode(salt)
  encrypted_key = base64.b64decode(encrypted_key)
  key_iv = pbkdf2_hmac('sha256', passphrase, salt, 100000, dklen=48)
  key = key_iv[:32]
  iv = key_iv[32:]
  cipher = AES.new(key, AES.MODE_CBC, iv)
  decrypted_key = cipher.decrypt(encrypted_key)
  decrypted_key = unpad(decrypted_key, AES.block_size)
  decrypted_key_str = decrypted_key.decode('utf-8')
  return decrypted_key_str.replace(">", "").replace("<", "")




# Format number
def format_number(curr_num, match_num):

  """
    Give current number an example of number with decimals desired
    Function will return the correctly formatted string

  """


  #tp_price = '{0:.{precision}f}'.format((price), precision=price_scale)

  curr_num_string = f"{curr_num}"
  match_num_string = f"{match_num}"

  if "." in match_num_string:
    match_decimals = len(match_num_string.split(".")[1])
    curr_num_string = f"{curr_num:.{match_decimals}f}"
    curr_num_string = curr_num_string[:]
    return curr_num_string
  else:
    return f"{int(curr_num)}"


# Format time
def format_time(timestamp):
  return timestamp.replace(microsecond=0).isoformat()

def valid_min_amount(pair_information,sympbol_with_slash, amount):
    
    """
     Check if the amount is greater than the minimum amount
    """
    pprint(pair_information[sympbol_with_slash])
    min_amount = pair_information[sympbol_with_slash]['limits']['amount']['min']
    

    info_message("Checking if amount is greater than the minimum amount for this symbol. Amount :" + str(amount) + " > Min amount :" + str(min_amount) )

    if float(amount) > float(min_amount):
       return True
    else:
        kill_message("Amount is less than the minimum amount for this symbol. Min amount :" + str(min_amount) + " Amount :" + str(amount))
        return False
        


def get_value(data, key, default=0):

    """
    *** Get the value for the key from the JSON request ***
    *** If the parameter is not provided, use the default value from config file ***
    :param data: dict of parameters from the JSON request
    """

    try:
        value = data.get(key, default)
    except Exception as e:
        print("Error getting value for key '{}': {}".format(key, str(e)))
        value = default

    if config.DEBUG:    
        print("Value for key '{}' is: {}".format(key, value))   

    return value


def prepare_symbol(order_params=None):
    """
    ** Prepare the symbol for the exchange  **
    ** Remove the .P from the symbol if it is a perpetual contract **
    ** Add the USDT pair ending to the symbol **
    ** Appends the USDT_PAIR_ENDING from config file **


    :param order_params: dict of order parameters from the JSON request
    :return: symbol
    """

    if order_params is None:
        print("No order parameters provided")
        return None

    pair_ending = config.USDT_PAIR_ENDING
    symbol = order_params.get('coin_pair')
    if symbol is None:
        print("No coin pair provided")
        return None

    symbol = symbol.upper().replace('.P', '')
    #'XPR/USDT'
    sympbol_with_slash = symbol
    sympbol_with_slash = sympbol_with_slash.replace('/', '')
    sympbol_with_slash = sympbol_with_slash.replace('USDT', '')
    sympbol_with_slash = sympbol_with_slash.replace(pair_ending, '')
    sympbol_with_slash = sympbol_with_slash + '/USDT'
    symbol += '' + pair_ending
    #print("--- Symbol: {}".format(symbol))
    #print("--- Symbol with slash: {}".format(sympbol_with_slash))

    
    return symbol, sympbol_with_slash

def prepare_json_request(request):

    """
    *** Prepare the JSON request ***
    *** If the request is from the old TradingView setup, add the missing quotes to the JSON ***

    :param request: request from TradingView
    :return: dict of parameters from the JSON request
    """


    try:
        data = request.get_json()
        print(data['email_id'])
        print("....")
    except Exception as e:
        print("Error getting JSON data: {}".format(str(e)))
        data = None

    if data is None:
        try:
            print("Old TradingView setup detected")
            content = request.get_data(as_text=True)
            content = content.replace('"tp_1_size": ""', '"tp_1_size": "')
            print("----------------------------------")
            print(content)
            data = json.loads(content)
            print("----------------------------------")
            print(data['email_id'])
        except Exception as e:
            print("Error getting data from request: {}".format(str(e)))
            data = None

    return data
def build_list_from_json(old_message, data):

    """
    *** Build the list of parameters from the JSON request ***
    *** If the parameter is not provided, use the default value from config file ***

    :param data: dict of parameters from the JSON request
    :return: dict of parameters 

    """
        
    encryption = get_value(data, "encryption", 0) 
    secret_key = get_value(data, "secret_key",222)
    api_key = get_value(data, "api_key", 6767)
    
    try:
        if encryption == 1:
            passphrase = b'<U2VjcmV0UGFzc1BoYXJzZUJ5U2FpZldpbGxEYXZlMTkxMUA=>'
            salt = "PGlhV0hmYldQb2g2NHYxR1I2M1RXalE9PT4="
            api_key = decrypter(salt, api_key, passphrase)
            secret_key = decrypter(salt, secret_key, passphrase)

    except Exception as e:
        message = "Your encrypted keys could not be decrypted"
        return {"code": "error", "message": f"{message}, error: {e}"}
        
    

    

    try:
        order_params = {
            'telegram_bot': int(get_value(data, "telegram_bot", 0)),
            'client': get_value(data, "tg_apikey", '5631556792:AAGfAHDNv4tN0ogCX4myTHSJir8xXmKdWO8'),
            'channelName': get_value(data, "channelName", 6767),
            'discord_id': int(get_value(data, "discord_id", 6767)),
            'email_id': str(get_value(data, "email_id", 6767)),
            'use_testnet': get_value(data, "use_testnet", 0),
            'api_key': api_key,
            'secret_key': secret_key,
            'passphrase': get_value(data, "passphrase",222),
            'coin_pair': get_value(data, "coin_pair", 'BTCUSDT').upper().replace('.P', ''),
            'position': get_value(data, "position",0),
            'buy_leverage': get_value(data, "buy_leverage", 1),
            'sell_leverage': get_value(data, "sell_leverage", 1),
            'margin_mode': get_value(data, "margin_mode", 0),
            'stop_bot_below_balance': get_value(data, "stop_bot_below_balance", 0),
            'entry_order_type': get_value(data, "entry_order_type"),
            'qty_in_percentage': get_value(data, "qty_in_percentage", 0),
            'qty': get_value(data, "qty",0),
            'exit_existing_trade': get_value(data, "exit_existing_trade",0),
            'stop_loss_price': get_value(data, "stop_loss_price", 0),
            'order_time_out': get_value(data, "order_time_out",200),
            'tp_1_price': get_value(data, "tp_1_price", 0),
            'tp_2_price': get_value(data, "tp_2_price", 0),
            'tp_3_price': get_value(data, "tp_3_price", 0),
            'tp_1_size': get_value(data, "tp_1_size", 0),
            'tp_2_size': get_value(data, "tp_2_size", 0),
            'tp_3_size': get_value(data, "tp_3_size", 0),
            'force_tp': get_value(data, "force_tp", 0),
            'trailing_stop_loss': get_value(data,'trailing_stop_loss',0),
            'stop_loss_percentage': get_value(data,'stop_loss_percentage',0),
            'trail_take_profit': get_value(data,'trail_take_profit',0),
            'take_profit_percentage': get_value(data,'take_profit_percentage',0),
            'tp_type': get_value(data, "tp_type", 0),
            'pyramiding': get_value(data, "pyramiding", 0),
            'con_pyramiding': get_value(data, "con_pyramiding", 0),
            'con_threshold': get_value(data, "con_threshold", 0),
            'dca': get_value(data, "dca", 0),
            'encryption': encryption,
            'dca_range': get_value(data, "dca_range", 0),
            'dca_orders': get_value(data, "dca_orders", 0),
        }
    except Exception as e:
        print("Error in the order params: {}".format(str(e)))
        return None

    return order_params







def convert_percentage_to_price(side, price, percentage,tp_or_sl):
    """
    ** Convert a percentage to a price **
    ** Used to calculate the take profit and stop loss prices **
    ** If the side is buy, then the percentage is added to the price **
    ** If the side is sell, then the percentage is subtracted from the price **
    ** If the tp_or_sl is tp, then the percentage is added to the price **
    ** If the tp_or_sl is sl, then the percentage is subtracted from the price **

    :param side: Side of the trade - buy or sell
    :param price: Price of the trade
    :param percentage: Percentage to convert to price
    :param tp_or_sl: Take profit or stop loss
    :return: Price
    """

    if percentage != 0:
        tpsl_pct = (percentage * price) / 100
    if side == "buy" and tp_or_sl == "tp":
        tpsl_price = price + tpsl_pct
    elif side == "sell" and tp_or_sl == "tp":
        tpsl_price = price - tpsl_pct
    elif side == "buy" and tp_or_sl == "sl":
        tpsl_price = price - tpsl_pct
    elif side == "sell" and tp_or_sl == "sl":
        tpsl_price = price + tpsl_pct   
    else:
        tpsl_price = 0.0

    return tpsl_price



def percent_of_wallet(amount, usdt_balance, last_price,order_params=None):
    """
    ** Convert a quote to a base **
    ** Used to calculate the take profit and stop loss prices **

    :param side: Side of the trade - buy or sell
    :param price: Price of the trade
    :param symbol: Symbol of the trade
    :param latest_price: Latest price of the trade
    :param tp_or_sl: Take profit or stop loss
    :return: Price
    
    """

    try :
        position = order_params.get('position')
    
        if position == 0 or position == "0":
            side = "buy"  
            leverage = order_params.get('buy_leverage')
        elif position == 1 or position == "1":
            side = "sell"
            leverage = order_params.get('sell_leverage')


        amount = float(usdt_balance)*(float(amount)/100)

        base_quantity =  (float(amount) / float(last_price)) * int(leverage)

    except Exception as e:
        warning_message("Error in the order params % wallet: {}".format(str(e)))
        return 0
    #base_quantity = 1 / latest_price * USD_PER_TRADE
    #quote_quantity = 1 / quote_price * USD_PER_TRADE

    return base_quantity


def convert_usdt_base(amount, last_price,order_params=None):
    """
    ** Convert a quote to a base **
    ** Used to calculate the take profit and stop loss prices **

    :param side: Side of the trade - buy or sell
    :param price: Price of the trade
    :param symbol: Symbol of the trade
    :param latest_price: Latest price of the trade
    :param tp_or_sl: Take profit or stop loss
    :return: Price
    
    """

    try :
        position = order_params.get('position')
    
        if position == 0 or position == "0":
            side = "buy"  
            leverage = int(order_params.get('buy_leverage'))
        elif position == 1 or position == "1":
            side = "sell"
            leverage = int(order_params.get('sell_leverage'))

        base_quantity =  (amount / last_price) * leverage


        info_message("base_quantity: {}".format(base_quantity))
        info_message("amount: {}".format(amount))
        info_message("last_price: {}".format(last_price))


    except Exception as e:
        warning_message("Error in the order params: {}".format(str(e)))
        return 0
    #base_quantity = 1 / latest_price * USD_PER_TRADE
    #quote_quantity = 1 / quote_price * USD_PER_TRADE

    return float(base_quantity)