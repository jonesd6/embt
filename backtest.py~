#! python3
# backtest.py

import data
import strategy
import event
import portfolio
import datetime
import execution
import exposure
from multiprocessing import Queue
import queue
import os

start_date = datetime.datetime(2016, 8, 8, 9, 30, 0)
initial_capital = 100000
event_queue = Queue()
csv_directory = "C:\\Users\\jonesdl6\\Desktop\\EminiBacktest"
csv_filename = '1weekemini.csv'
bars = data.EMiniCSVHandler(event_queue, 
                            csv_filename)
bars.update_bars()
                                   

                                       
portfolio = portfolio.EMiniPortfolio(bars, 
                                     event_queue, 
                                     start_date, 
                                     initial_capital)

strategy = strategy.SMAtoEMA(bars, 
                             event_queue)                                     
broker = execution.SimulatedExecutionHandler(event_queue)

while True:
    
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break
    
    # Handle the events
    while True:
        try:
            event = event_queue.get(True, .001)
        except queue.Empty:
            print("Queue empty")
            break
        else:
            if event is not None:
                print(event.type)
                if event.type == 'MARKET':
                    #print('1')
                    #portfolio.update(event)
                    strategy.calculate_signals(event, portfolio)
                elif event.type == 'SIGNAL':
                    #print('2')
                    portfolio.update_signal(event)
                    
                elif event.type == 'ORDER':
                    #print('3')
                    broker.execute_order(event)
                    
                elif event.type == 'FILL':
                    #print('4')

                    portfolio.update_fill(event)
                    
# print("debt: %s" % portfolio.debt)
# print("equity: %s" % portfolio.current_holdings['total'])   
# print("cash: %s" % portfolio.cash)  
# print("commission: %s" % portfolio.current_holdings['commission'])         
