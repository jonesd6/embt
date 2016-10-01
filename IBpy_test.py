#! python3
# IBpy_test.py

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, message
import time
import datetime
import csv

def error_handler(msg):
    """Handles the capturing of error messages"""
    print("Server Error: %s" % msg)
    
def reply_handler(msg):
    """Handles server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))
    
def create_fut_contract(symbol, sec_type, expiry, exch, prim_exch, curr):
    """
    Create a Contract object defining what will be pruchased, at which
    exchange and in which currency.
    
    symbol - The ticker symbol for the contract.
    sec_type - The security type for the contract ('STK' is 'stock').
    exch - The exchange to carry out the contract on.
    prim_exch - The primary exchagne to carry out the contract on.
    curr - The currency in which to purchase the contract
    """
    
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_expiry = expiry
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract
    
def create_stk_contract(symbol, sec_type, exch, prim_exch, curr):
    """
    Create a Contract object defining what will be pruchased, at which
    exchange and in which currency.
    
    symbol - The ticker symbol for the contract.
    sec_type - The security type for the contract ('STK' is 'stock').
    exch - The exchange to carry out the contract on.
    prim_exch - The primary exchagne to carry out the contract on.
    curr - The currency in which to purchase the contract
    """
    
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract
    
def create_order(order_type, quantity, action):
    """
    Create an Order object (Market/Limit) to go long/short.
    
    order_type - 'MKT', 'LMT' for Market or Limit orders.
    quantity - Integral number of assets to order.
    action - 'BUY' or 'SELL'
    """
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order

def process_data(msg):
    outfile = open('1weekemini.csv', 'a')
    d_writer = csv.writer(outfile)
    
    if msg.open != -1:
        a_array = [msg.date, msg.open, msg.high, msg.low, msg.close, msg.volume, msg.count, msg.WAP]
        d_writer.writerow(a_array)
        
    else:
        print("not")

if __name__ == "__main__":
    # Connect to the Trader Workstation (TWS) running on the usual port of
    # 7496, with a clientId of 100 (separate ID required for both execution
    # connection and market data connection)
    tws_conn = Connection.create(port=7497, clientId=100)
    

    tws_conn.connect()
    
    tws_conn.register(error_handler, 'Error')
    tws_conn.registerAll(reply_handler)
    order_id = 14
    es_contract = create_fut_contract("ES", 'FUT', "20161216", 'GLOBEX', 'GLOBEX', 'USD')
    goog_contract = create_stk_contract('GOOG', 'STK', 'SMART', 'SMART', 'USD')
    #goog_order = create_order('MKT', 10, 'SELL')
    #tws_conn.placeOrder(order_id, goog_contract, goog_order)
   
    
    endtime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
    
    
    tws_conn.reqHistoricalData(
            tickerId=1,
            contract=es_contract,
            endDateTime=endtime,
            durationStr='1 W',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=0,
            formatDate=1)
    
    
    tws_conn.register(process_data, message.historicalData)
    

    time.sleep(100)
    tws_conn.disconnect()