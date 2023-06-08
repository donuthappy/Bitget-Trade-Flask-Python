import ccxt
from time import sleep, time
import json
#from mainFunctions import *
from json import dumps
import time
import config
import requests
from pprint import pprint

from func_messages import *
from func_utils import convert_usdt_base, convert_percentage_to_price, percent_of_wallet,format_number, check_positions, get_position_value_with_side, get_position_value

 

def con_pyramiding(exchange, symbol, order_params):
   
    con_pyramiding = order_params.get('stop_bot_below_balance')
    position = int(order_params.get('position'))
    con_threshold = float(order_params.get('con_threshold'))
    qty = float(order_params.get('qty'))

    con_pyramiding_check = False

    if position == 0:
            pos_idx = 1
            side = "Buy"
            tp_side = "Sell"
            leverage = order_params.get('buy_leverage')
    else:
            pos_idx = 2
            side = "Sell"
            tp_side = "Buy"
            leverage = order_params.get('sell_leverage')


    if con_pyramiding == 1 or con_pyramiding == "1":
        pos_qty, pos_side = check_positions(exchange, symbol, order_params)
        current_value = get_position_value_with_side(symbol, position)
        accu_current_value = float(current_value) + float(qty)
        
        if float(accu_current_value) > con_threshold:
            con_pyramiding_check = True

    if con_pyramiding == 3 or con_pyramiding == "3":
        current_value = get_position_value(symbol)
        pos_qty, pos_side = check_positions(exchange, symbol, order_params)

        if float(current_value) > con_threshold and pos_side == side:
            con_pyramiding_check = True

        if pos_side != side:
            con_pyramiding_check = True

    if con_pyramiding == 4 or con_pyramiding == "4":
        current_value = get_position_value(symbol)
        if float(current_value) > con_threshold:
            con_pyramiding_check = True

    return con_pyramiding_check
        


def DCA_STRATEGY(exchange, symbol, last_price, margin, order_params=None):
    #(contract_qty, max_cost, DCA_orders, DCA_Range, last_price, side, self.session, tp, sl, coin_pair, qty_step, price_scale)
   
   
    #DCA_STRATEGY(contract_qty, max_cost, DCA_orders, DCA_Range, last_price, side, self.session, tp, sl, coin_pair, qty_step, price_scale)
    #DCA_STRATEGY(contract_qty, max_cost, order_num, percent, cur_price, side,session, tp, sl, coin_pair, qty_step, price_scale):
    qty_in_percentage = order_params.get('qty_in_percentage')
    if qty_in_percentage == 1 or qty_in_percentage == "1" or qty_in_percentage == 0 or qty_in_percentage == "0": 
        contract_qty = 1
    else:
        contract_qty = 0
    contract_qty = 0
    coin_pair = symbol

   
    max_cost = margin
    tp_type = order_params.get('tp_type')
    params_tp = {}
    DCA_orders = order_params.get('dca_orders')
    DCA_Range = order_params.get('dca_range')
    range_dist = (int(DCA_Range) * float(last_price)) / 100
    position = int(order_params.get('position'))
    order_num = int(DCA_orders)

    average_cost = float(max_cost) / int(order_num)

    
    if position == 0 or position == "0":
            pos_idx = 1
            side = "Buy"
            tp_side = "Sell"
            leverage = order_params.get('buy_leverage')
    else:
            pos_idx = 2
            side = "Sell"
            tp_side = "Buy"
            leverage = order_params.get('sell_leverage')

    info_message("DCA STRATEGY: " + str(side) + " ON : " + str(coin_pair) + " Average cost: " + str(average_cost) + " Number of orders: " + str(order_num) + " Average distance: " + str(range_dist) + " Last price: " + str(last_price) + " contract_qty: " + str(contract_qty) + " max_cost: " + str(max_cost) + " DCA_orders:" + str(DCA_orders) + " DCA_Range:" + str(DCA_Range))
    
    
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

    order_num = int(order_num)
    for i in range(order_num):
        i += 1
        print("i: " + str(i) + " order_num: " + str(order_num))
        if side == "Buy":
            price = last_price - (range_dist * i)
            price2 = price
            if contract_qty == 1:
                qty = average_cost
            else:
                qty = average_cost / price

        elif side == "Sell":
            price = last_price + (range_dist * i)
            price2 = price
            if contract_qty == 1:
                qty = average_cost
            else:
                qty = average_cost / price

            qty = qty

        if i == 1:
            info_message("First order : " + str(side) + " PAIR : " + str(coin_pair) + " Price: " + str(price2) + " Qty: " + str(qty) + " Leverage: " + str(leverage))
            order = exchange.create_order(symbol, 'market', side.lower(), average_cost, price2, params_tp)
            #order_id = order['result']['order_id']
        else:
            info_message(str(i) + " order : " + str(side) + " PAIR : " + str(coin_pair) + " Price: " + str(price2) + " Qty: " + str(qty) + " Leverage: " + str(leverage))
            order = exchange.create_order(symbol, 'limit', side.lower(), average_cost, price2, params_tp)
        print("Order: " + str(order))

            
            
            #pprint(response)
    pprint("Order ID : " + order_id)       

    """
    
    
    if tp_3_price is not None:
        response = exchange.create_order(symbol, 'market', side, margin, tp_3_price, { 'takeProfitPrice': tp_3_price, "reduceOnly": True, "closePosition": True})
    if stop_loss_price is not None:
        response = exchange.create_order(symbol, 'market', side, margin, stop_loss_price,  { 'stopLossPrice': stop_loss_price, "reduceOnly": True, "closePosition": True })
    """

    return qty, order_id