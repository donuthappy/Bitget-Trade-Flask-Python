import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests
from pprint import pprint
from time import sleep, time

from func_messages import *
from func_utils import convert_usdt_base, convert_percentage_to_price, percent_of_wallet,format_number, check_positions, get_position_value_with_side, get_position_value
from func_advanced_features import con_pyramiding, DCA_STRATEGY





def close_open_positions(exchange, symbol, order_params=None):
    """
    ** Cancel all active orders for the given symbol **
    ** Close all open positions for the given symbol **

    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - json object with all the order parameters
    :return: None
    """
    
    try:
        print(" -- ⌛ Cancelling all active orders -- ")
        exchange.cancel_all_orders(symbol=symbol,params={"marginCoin":"USDT"})
        print(" -- ✅ Cancelling all active orders -- ")
    except Exception as e:
        print("Can't cancel all active orders {}".format(str(e)))

    try:

        exit_existing_trade = order_params.get('exit_existing_trade')

        if exit_existing_trade == "1":
            symbol = symbol
            #print(symbol)

            print(" -- ⌛ Fetching Data from exchange -- ")
            positions = exchange.fetch_positions(symbols=[symbol])
            print(" -- ✅ Fetching Data from exchange -- ")

            #print(positions)
        else:
            positions = None
    except Exception as e:
        print("Can't find any open positions: {}".format(str(e)))
        message = f"Can't find any open positions: {str(e)}"
        old_message = append_messages_new(old_message, message)
        pass

    if positions:
        for position in positions:
            pos_amt = float(position['info']['total'])
            pos_side = position['side'].lower()

            if pos_amt:
                try:
                    if pos_side == "short" or pos_side == "sell":
                        exchange.create_order(symbol, 'market', 'buy', pos_amt, None, {'reduceOnly': True})
                    elif pos_side == "long" or pos_side == "buy":
                        exchange.create_order(symbol, 'market', 'sell', pos_amt, None, {'reduceOnly': True})
                except Exception as e:
                    message = f"Tried closing existing positions but some positions could not be closed. \n ⚠️ ERROR : {e}"
                    old_message = append_messages_new(old_message, message)

    return "Done"



def check_over_leverage(old_message, exchange, symbol, sympbol_with_slash, last_price, pair_information, order_params=None):

    """
    ** Check if the leverage is over the max leverage **
    ** If the leverage is over the max leverage, then the order is cancelled **
    ** If the leverage is over the max leverage, then the order is cancelled **

    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param last_price: Last price of the symbol
    :param pair_information: Pair information - passed through the prepare_symbol() function
    :param order_params: Order parameters - passed through the prepare_symbol() function
    :return: True if the order is cancelled, False if the order is not cancelled
    """
    
    try:
        symbol_info = pair_information[sympbol_with_slash]  
   
        min_leverage = symbol_info['limits']['leverage']['min']
        max_leverage = symbol_info['limits']['leverage']['max']
        telegram_bot = order_params.get('telegram_bot')
        email_id = order_params.get('email_id')
        buy_leverage = order_params.get('buy_leverage')
        sell_leverage = order_params.get('sell_leverage')
        
    except Exception as e:

        print("Can't get the leverage information: {}".format(str(e)))


   
    

    # Validate min and max leverage
    #min_leverage = int(min_leverage)
    #max_leverage = int(max_leverage)

    if (min_leverage == None or str(min_leverage) == "None" ):
        #pprint("min_leverage : " + str(min_leverage))
        min_leverage = int("1")
    if (max_leverage == None or str(max_leverage) == "None"):
        #pprint("max_leverage : " + str(max_leverage))
        max_leverage = int("500")

    buy_leverage = int(buy_leverage)
    sell_leverage = int(sell_leverage)


    if (buy_leverage >= min_leverage) and (buy_leverage <= max_leverage):
        if (sell_leverage >= min_leverage) and (sell_leverage <= max_leverage):
            pass
        else:
            if telegram_bot == 0 or telegram_bot == 1:
                message = str(email_id) + " Invalid Sell leverage for coin pair " + str(symbol) + ": Min leverage allowed is - " + str(min_leverage) + " and Max leverage allowed is - " + str(max_leverage)
                old_message = append_messages_new(old_message,message)
                return 'Failed'
            else:
                pass
    else:
        if telegram_bot == 0 or telegram_bot == 1:
            message = str(email_id) + " Invalid Buy leverage for coin pair " + str(symbol) + ": Min leverage allowed is - " + str(min_leverage) + " and Max leverage allowed is - " + str(max_leverage)
            old_message = append_messages_new(old_message,message)
            return 'Failed'
        else:
            pass
    return 'Done'




def get_trade_margin_base(last_price, usdt_balance, pair_information, sympbol_with_slash, order_params=None):
    """
    *** Get the trade amount in Base currency ***
    * if the BTC/USDT pair is selected, BTC is the Base asset and USDT is the Quote asset.

    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param last_price: Last price of the symbol
    :param pair_information: Pair information - passed through the prepare_symbol() function
    :param order_params: Order parameters - passed through the prepare_symbol() function
    :return: Trade amount
 
    "qty_in_percentage": "2",
    "qty": "20",
    """
 
    try:      

        qty_in_percentage = order_params.get('qty_in_percentage')
        qty = order_params.get('qty')


    except Exception as e:
        warning_message("Problem preparing margin: {}".format(str(e)))
        return False



    try:    


        if qty_in_percentage == 0 or qty_in_percentage =="0" :

            info_message("User has selected to trade in base currency")
            qty = qty

        elif qty_in_percentage == 1 or qty_in_percentage =="1" :

            info_message("User has selected to trade in percentage of wallet")
            qty = percent_of_wallet(float(qty), float(usdt_balance), float(last_price),order_params)
  
        elif qty_in_percentage == 2 or qty_in_percentage =="2" :

            info_message("User has selected to trade in quote currency")
            qty = convert_usdt_base(float(qty), float(last_price),order_params)

        else:
            info_message("Defaulting to trade in quote currency")
            qty = convert_usdt_base(float(qty), float(last_price))
            


    except Exception as e:
        warning_message("Problem preparing margin: {}".format(str(e)))
        return False

    #pprint(pair_information)


    return qty





def enter_order(exchange, symbol, last_price, margin, order_params=None):
    """
    
    ** Enter an order **
    ** Set Stoploss **
    ** Set Take profits **
    
    
    :param old_message: The error message
    :param exchange: Exchange object - ccxt
    :param symbol: Symbol to close positions for - passed through the prepare_symbol() function
    :param order_params: Order parameters - json object with all the order parameters
    :return: None

    
    
    """

    message = ""
    try:      
        position = order_params.get('position')
        price = order_params.get('price')
        if position == 0 or position == "0":
            side = "buy"  
        elif position == 1 or position == "1":
            side = "sell"
        else:
            raise ValueError("Invalid position value")
 
        tp_type = order_params.get('tp_type')
        DCA = order_params.get('dca')


        """
        'trailingPercentage': stop_loss_percentage,
    'close': {
        'type': 'trailing_take_profit',
        'trailingPercentage': take_profit_percentage,
        'stopPrice': None,
    }
        
        
        """
         
        if DCA == 1 or DCA == "1":

            
            wait_message("Making order to exchange DCA")
            qty, order_id = DCA_STRATEGY(exchange, symbol, last_price, margin, order_params)
            done_message("Making order to exchange DCA")
        else:
            if tp_type == 1 or tp_type == "1":  
                #tp_type = "percentage"
                tp_3_price = order_params.get('tp_3_price')  
                stop_loss_price = order_params.get('stop_loss_price')

                if len(tp_3_price) > 0:
                    tp_3_price = convert_percentage_to_price(side, float(last_price), float(tp_3_price),"tp")
                if len(stop_loss_price) > 0:
                    stop_loss_price = convert_percentage_to_price(side, float(last_price), float(stop_loss_price),"sl")

            else: 
                tp_3_price = order_params.get('tp_3_price')   
                tp_3_size = order_params.get('tp_3_size')   
                stop_loss_price = order_params.get('stop_loss_price')

            position = order_params.get('position')


            trailing_stop_loss = order_params.get('trailing_stop_loss')
            stop_loss_percentage = order_params.get('stop_loss_percentage')
            trail_take_profit = order_params.get('trail_take_profit')
            take_profit_percentage = order_params.get('take_profit_percentage')


            if (trailing_stop_loss == 1 or trailing_stop_loss == "1") and (trail_take_profit == 1 or trail_take_profit == "1"):
                params_tp = {
                                'type': 'trailing_stop',
                                'stopPrice': None,
                                'trailingPercentage': stop_loss_percentage,
                                'close': {
                                    'type': 'trailing_take_profit',
                                    'trailingPercentage': take_profit_percentage,
                                    'stopPrice': None,
                            }
                        }
                
            elif (trailing_stop_loss == 1 or trailing_stop_loss == "1") :
                params_tp = {
                                'type': 'trailing_stop',
                                'stopPrice': None,
                                'trailingPercentage': stop_loss_percentage,
                        }
            else:
                params_tp = {}

            price = ""
        
            info_message("Entering order for " + str(symbol) + " with " + str(margin) + " margin" + " side  " + str(side) + " ")
            info_message("FINAL TP Price " + str(tp_3_price) + " STOP LOSS Price " + str(stop_loss_price) + " ")


            response = exchange.create_order(symbol, 'market', side, margin, price, params_tp)
            #pprint(response)
            
            if tp_3_price is not None:
                response = exchange.create_order(symbol, 'market', side, margin, tp_3_price, { 'takeProfitPrice': tp_3_price, "reduceOnly": True, "closePosition": True})
            if stop_loss_price is not None:
                response = exchange.create_order(symbol, 'market', side, margin, stop_loss_price,  { 'stopLossPrice': stop_loss_price, "reduceOnly": True, "closePosition": True })
        
    except Exception as e:
        print("Problem Making order: {}".format(str(e)))
        #old_message = append_messages_new(old_message, message)
        return False
    
    
    #pprint(response)

    return True




def create_multi_tp_order(exchange, symbol, tp_price, tp_size, tp_num, tick_size, last_price, margin, order_params=None):
    
    # Validate take profit size
   

    position = order_params.get('position')
    tp_size = float(tp_size)

    price = order_params.get('price')
    tp_type = order_params.get('tp_type')
    if position == 0 or position == "0":
        side = "buy"  
    elif position == 1 or position == "1":
        side = "sell"
    else:
        raise ValueError("Invalid position value")
 
    if tp_type == 1 or tp_type == "1":  
        #tp_type = "percentage"
        tp_3_price = order_params.get('tp_3_price')  
        stop_loss_price = order_params.get('stop_loss_price')

        if len(tp_3_price) > 0:
            tp_3_price = convert_percentage_to_price(side, float(last_price), float(tp_3_price),"tp")
        if len(stop_loss_price) > 0:
            stop_loss_price = convert_percentage_to_price(side, float(last_price), float(stop_loss_price),"sl")

    else: 
        tp_3_price = order_params.get('tp_3_price')   
        tp_3_size = order_params.get('tp_3_size')   
        stop_loss_price = order_params.get('stop_loss_price')




    try:
        #qty = margin
        #tp_price =  qty
        

        #info_message(f"Getting postion size etc for  {qty}  side")
        #qty_step = 0
        #qty = ((float(qty)) / 100)*(tp_size) 
       
       
       
        if side == "buy" or position == 0 or position == "0":
            tp_price = (tp_3_price - last_price) * (tp_size/100)
            inversed_side = "sell"
        elif side == "sell" or position == 1 or position == "1":
            tp_price = (last_price - tp_3_price) * (tp_size/100)
            inversed_side = "buy"
        

        tp_price = tp_price + last_price
        qty = float(margin) * (int(tp_size)/100)
       

    except Exception as e:
        message = "Getting postion size etc --> " + str(e)
        warning_message(message)



    try:
        
        order = exchange.create_order(symbol=symbol, amount=qty, side=inversed_side, type="limit", price=tp_price, params={"timeInForce": "GoodTillCancel", "reduceOnly": True, "closeOnTrigger": True})
     
        if tp_num == 3:
            message = f"*TP{tp_num} --> Price:* {tp_price}\n *TP{tp_num} --> Size:* {qty} "
            info_message(message)

    except Exception as e:

        if "Qty not in range" in str(e):
            #tp_set = "qty out of range"
            message = f"TP{tp_num} ({qty}) size is either smaller than min allowed size or bigger than allowed size"
            warning_message(message)

            #print(message)
        else:
            #tp_set = 'tp error'
            print(str(e))
            message = "ERRR : Placing Multi TP  --> " + str(e)

            warning_message(message)
            qty = 0
            
    return message, qty


def check_for_pyramiding(exchange, symbol, order_params=None):
    """
    ** Check if the user has pyramiding enabled and if so, check if the user has an active position **
    ** If the user has an active position, check if the position is the same side as the order **
    ** If the position is the same side as the order, return False, else return True **
    ** If the user does not have an active position, return True **
    ** If the user does not have pyramiding enabled, return True **
    ** If the user has pyramiding enabled, but the position is the same side as the order, return False **
    ** If the user has pyramiding enabled, but the position is the opposite side as the order, return True **
    
    :param exchange: exchange object
    :param symbol: symbol for the exchange
    :param order_params: dict of order parameters from the JSON request
    :return: True or False
    """
    
    positions = exchange.fetch_positions(symbols=[symbol])
    pyramid_check = True
    pyramiding = order_params.get('pyramiding')
    position = order_params.get('position')
    

    if position == 0:
        side = "buy"
    else:
        side = "sell"

    if positions:
        for position in positions:
            pos_amt = float(position['info']['total'])
            pos_side = position['side'].lower()

            if pos_amt:

                if pos_side == "short" or pos_side == "sell":
                    pos_side = "sell"
                    pos_qty = pos_amt
                    #return float(buy_active_qty), buy_side

                elif pos_side == "long" or pos_side == "buy":
                    pos_side = "buy"
                    pos_qty = pos_amt
                    #return float(sell_active_qty), sell_side
                else:
                    return 'Done'
                
                if pyramiding == 1:
                    
                    if pos_qty > 0 and pos_side == side:
                        #ignore the signal
                        message = f"Can't add order, pyramiding is deactivated and you already have a posision open for {symbol}"
                        #old_message = append_messages_new(old_message, message)
                        return 'Failed'
                    if pyramiding == 2:
                        #pos_qty, pos_side = check_positions(exchange, symbol, order_params)
                        if pos_qty > 0:
                            #ignore the signal
                            message = f"Can't add order, pyramiding is deactivated and you already have a posision open for {symbol}"
                            #old_message = append_messages_new(old_message, message)
                            return 'Failed'

            else:
                return 'Done'
            

    else:
        return 'Done'
    
