import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
#import time
import config
import requests
from time import sleep, time

from func_connect import connect_to_exchange
from func_utils import get_value, prepare_json_request, build_list_from_json, prepare_symbol, convert_percentage_to_price, format_number, format_time, valid_min_amount
from func_telegram import send_message_to_telegram, append_messages_new, Notify_telegram
from func_account import prepare_account, usdt_balance_more_than_threshold, get_wallet_balance
from func_trade import close_open_positions, enter_order, check_for_pyramiding, check_over_leverage, get_trade_margin_base, check_positions, create_multi_tp_order
from func_public import get_latest_price
from func_messages import *
from func_advanced_features import con_pyramiding, DCA_STRATEGY

from message_log import ErrorMessages

start_time = time()

error_messages = ErrorMessages()
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
  #trade(request)
  return 'Hello from Flask! Use this as your webhook : https://CCXT-Flask.daviddtech.repl.co/trading'


@app.route('/trading', methods=['POST', 'GET'])
def trading():
  trade(request)
  return 'All good'


def trade(request):
  #start_time = time() # start the timer



  """
    *** Main function ***
    *** This function is called by TradingView when a new alert is triggered ***
    
    ** Prepareration **
    * Error hanadling
    * 🟠 Check for true false return values

    * ✅ Extract the order parameters from the TradingView alert
    * ✅ Prepare the exchange object
    * ✅ decrypter
    * ✅ Prepare the symbol
    * ✅ Prepare the TESTNET flag
    * ✅ Prepare the account
    * ✅ Close existing open positions if user has enabled this option
    * ✅ Check if pyramiding is enabled - if yes, check if the position is already open.
    * ✅ Check max levergae is not exceeded
    * ✅ Stop trading if below balance threshold
    
    ** The order **
    * ✅ Convert % into absolute values for stoploss and take profits
    
    
    * ✅ Set the stoploss
    * ✅ Set the take profits
    * ✅ Order size is calculated based on the user's risk or percentage of the account balance or fixed amount
    * ✅ Enter the order
    * ✅ Set Multiple take profits can be set
  
    ** Extra features **
    * 🟠 DCA can be enabled
    * 🟠 Conditional Pyramiding can be enabled
    * 🟠 Add if statement for enable_multi_tp
    * 🟠 Close all positions in one direction if  
 

    ** Notifications **
    [Optional] - in development
    * 6. Send a notification to Telegram 🟠 Uncomment the request last line to enable

    * 7. Send a notification to email
    * 8. Send a notification to SMS
    * 9. Send a notification to Discord

    ** NOTES **
    * check_positions and 2 other functions need checking.
    * format_number(curr_num, match_num) needs checking - match num should maybe use presicion price_scale = int(info["priceScale"])
    * multi_tp needs checking - format_number
    * force tp needs checking - format_number

    * 🟠 Percentage of wallet balance needs checking
    * 🟠 cross to isolated as an option     "margin_mode": "1", //1 = isolated 0 = cross




    ** TODO **

    * When postion opened and trying to set margin mode, it fails. Send telegram message.
    * 🔴 Set the trailing stoploss if enabled


    ** TESTS **

    * ✅ Test with no TP or SL
    * ✅ Test with TP and SL

    * Test with TP and SL and DCA
    * Test with TP and SL and DCA and pyramiding
    * Test with TP and SL and DCA and pyramiding and trailing stoploss
    * Test with TP and SL and DCA and pyramiding and trailing stoploss and force tp
    * Test with TP and SL and DCA and pyramiding and trailing stoploss and force tp and multi tp
    * Test with TP and SL and DCA and pyramiding and trailing stoploss and force tp and multi tp and cross to isolated


    * Test all above on TESTNET
    * Test SHORT orders all above

    
    * Close all positions in one directio 
    * Test change leverage



    
    """
  old_message = ""

  try:
    data = request.get_json()
    print(data['email_id'])
    print("First JSON worked")
  except:
    print("didnt work")
    pass
  try:
    if data:
      print("Moving on")
    else:
      # data = request.get_json()
      content = request.get_data(as_text=True)
      # d = json.loads(request.data)
      # data = request.get_json(force=True, silent=True)
      content = content.replace('"tp_1_size": ""', '"tp_1_size": "')
      print("----------------------------------")
      print(content)
      data = json.loads(content)
      print("----------------------------------")
      print(data['email_id'])
    # data =  data.replace('"tp_1_size": ""', '"tp_1_size": "')
  except:
    print(content)

  try:
    #with open('orders/json.json') as file:
    #data = json.load(file)

    if config.DEBUG:
      print(data)

    wait_message("Extracting paramas from json")
    order_params = build_list_from_json(old_message, data)
    done_message("Extracting paramas from json")

    if order_params is None:
      raise ValueError("Failed to extract order parameters from JSON")

    wait_message("Connecting to exchange")
    exchange, pair_information = connect_to_exchange(old_message, order_params)
    done_message("Connecting to exchange")

    if exchange is None:
      raise ValueError("Failed to connect to exchange")

    wait_message("Preparing Symbol")
    symbol, sympbol_with_slash = prepare_symbol(order_params)
    done_message("Preparing Symbol")

    wait_message("Preparing Account")
    prepare_account(old_message, exchange, symbol, order_params)
    done_message("Preparing Account")

  except Exception as e:
    print("** Trading Error **\n{} \n**END**".format(str(e)))
    pass

  try:
    # Close existing open positions if user has enabled this option
    wait_message("Closing all open positions")
    close = close_open_positions(exchange, symbol, order_params)
    done_message("Closing all open positions")
  except Exception as e:
    warning_message("Couldn't close open orders : {}".format(str(e)))
    #message = config.CANT_CLOSE_POSITIONS
    #old_message = append_messages_new(old_message,message)
  else:
    pass

  try:
    wait_message("Check for pyramding")
    check_for_pyramiding(exchange, symbol, order_params)
    done_message("Check for pyramding")
  except Exception as e:
    warning_message("Couldn't check if prymading is active : {}".format(
      str(e)))

  try:
    wait_message("Check for CON pyramding")
    con_pyramiding_check = con_pyramiding(exchange, symbol, order_params)
    done_message("Check for CON pyramding")
  except Exception as e:
    warning_message("Problem getting latest price information : {}".format(
      str(e)))

  try:
    wait_message("Getting latest price")
    last_price, ask_price, bid_price = get_latest_price(exchange, symbol)
    done_message("Getting latest price")
  except Exception as e:
    warning_message("Problem getting latest price information : {}".format(
      str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Check not over leveraged")
    check_over_leverage(old_message, exchange, symbol, sympbol_with_slash,
                        last_price, pair_information, order_params)
    done_message("Check not over leveraged")
  except Exception as e:
    warning_message("Couldn't check if leverage is too high : {}".format(
      str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Get wallet balance")
    usdt_balance = get_wallet_balance(exchange)
    done_message("Get wallet balance  -- {}".format(str(usdt_balance)))
  except Exception as e:
    warning_message("Problem getting wallet balance: {}".format(str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Check wallet balance is above threshold")
    usdt_balance_more_than_threshold(usdt_balance, order_params)
    done_message("Check wallet balance is above threshold")
  except Exception as e:
    warning_message("Problem wallet threshold:  {}".format(str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Convert base balance to trade amount")
    trade_margin = get_trade_margin_base(ask_price, usdt_balance,
                                         pair_information, sympbol_with_slash,
                                         order_params)
    done_message("Convert base balance to trade amount : " + str(trade_margin))
  except Exception as e:
    warning_message("Promblem converting to trade margin:  {}".format(str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Convert tick amount to trade amount")

    tick_size = pair_information[sympbol_with_slash]['precision']['amount']
    info_message("tick_size : " + str(tick_size))

    margin = format_number(trade_margin, tick_size)

    done_message("Convert tick amount to trade amount : " + str(margin))
  except Exception as e:
    warning_message("Promblem converting to tickSize  {}".format(str(e)))

  try:
    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Minimum order size check")

    is_valid_min_amount = valid_min_amount(pair_information, symbol, margin)

    done_message("Minimum order size check: " + str(is_valid_min_amount))
  except Exception as e:
    warning_message("Minimum order size   {}".format(str(e)))

  try:

    # Check if pyramiding is enabled - if yes, check if the position is already open.
    wait_message("Making order to exchange")
    order_id = enter_order(exchange, symbol, last_price, margin, order_params)
    done_message("Making order to exchange : " + str(order_id))
  except Exception as e:
    warning_message("Problem Making order:  {}".format(str(e)))

  try:

    # Check if pyramiding is enabled - if yes, check if the position is already open.
    tp_1_size = order_params.get('tp_1_size')
    tp_1_price = order_params.get('tp_1_price')

    if len(tp_1_size) > 0:
      tp_size = int(tp_1_size)
      tp_price = int(tp_1_price)
      tp_1_price = int(order_params.get('tp_1_price'))
      tp_num = 1
      wait_message("MUTLI TP 1 Making order to exchange")
      order_tp1_id = create_multi_tp_order(exchange, symbol, tp_price, tp_size,
                                           tp_num, tick_size, last_price,
                                           margin, order_params)
      done_message("Making order MUTLI TP 1 to exchange : " + str(order_id))

  except Exception as e:
    warning_message("Problem Making order:  {}".format(str(e)))

  try:

    # Check if pyramiding is enabled - if yes, check if the position is already open.
    tp_2_size = order_params.get('tp_2_size')
    tp_2_price = order_params.get('tp_2_price')

    if len(tp_2_size) > 0:
      tp_size = int(tp_2_size)
      tp_price = int(tp_2_price)
      tp_2_price = int(order_params.get('tp_2_price'))
      tp_num = 2
      wait_message("MUTLI TP 2 Making order to exchange")
      order_tp2_id = create_multi_tp_order(exchange, symbol, tp_price, tp_size,
                                           tp_num, tick_size, last_price,
                                           margin, order_params)
      done_message("Making order MUTLI TP 2 to exchange : " + str(order_id))

  except Exception as e:
    warning_message("Problem Making order:  {}".format(str(e)))
  """


    try:
       
            # Check if pyramiding is enabled - if yes, check if the position is already open.
            wait_message("Making order to exchange")
            order_id =  create_multi_tp_order(exchange, symbol, qty, price, tp_size, price_scale, qty_step, tp_side, last_price,tp_num)
            done_message("Making order to exchange : "+str(order_id)) 
    except Exception as e:
        warning_message("Problem Making order:  {}".format(str(e)))

    """

  try:
    wait_message("Checking for order to be filled")
    elapsed_time = time() - start_time
    success_message("Elapsed time: " + str(round(elapsed_time, 2)) +
                    " seconds")
  except Exception as e:
    warning_message("Can't complet!!!:  {}".format(str(e)))
  """
    IN DEV below this line
    
    """

  try:
    telegram_chat_id = order_params.get('channelName')
    for message in error_messages.get_messages():
      send_message_to_telegram(telegram_chat_id, message)
    # Clear error messages
    error_messages.clear_messages()

  except Exception as e:
    warning_message("** Trading Error **\n{} \n**END**".format(str(e)))
    pass

  try:
    position = order_params.get('position')
    if position == 0 or position == 1:

      #enter_order(old_message, exchange, symbol, order_params)
      print("Order placed")
      """


            response = exchange.create_order(symbol, 'market', side, amount, price, params_tp)
            response = exchange.create_order(symbol, 'market', side, amount, price,  { 'stopLossPrice': 27000 })
            response = exchange.create_order(symbol, 'market', side, amount_TP1, price, { 'takeProfitPrice': 30000 })
            
            
            response = exchange.create_order(symbol, 'market', side, amount_TP1, price, { 'takeProfitPrice': 33000 })
            response = exchange.create_order(symbol, 'market', side, amount_TP1, price, { 'takeProfitPrice': 28000 })
            """

    #create_order(self, symbol, type, side, amount, price=None, params={}):
    print(response)
  except ccxt.ExchangeError as e:
    print('Failed to place order:', e)


app.run(host='0.0.0.0', port=81)
