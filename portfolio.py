#! python3
# portfolio.py

import datetime
import numpy as np
import pandas as pd
from multiprocessing import Queue

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent

class Portfolio(object):
    """
    The Portfolio class handles the positions and market value of all
    instruments at a resolution of a "bar", i.e. secondly, minutely, 5-min,
    30-min, 60-min, or EOD.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio
        logic
        """
        
        raise NotImplementedError("Should implement update_signal()")
        
    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current postions and holdings from a FillEvent
        """
        
        raise NotImplementedError("Should implement update_fill()")
        
class EMiniPortfolio(Portfolio):
    """
    E-mini S&P500
    """
    
    def __init__(self, bars, events, start_date, initial_capital):
        """
        Initializes the portfolio with bars and event queue. Also includes a
        starting datetime index and intial capital (USD).
        
        Parameters:
        bars - The DataHandler objext with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        
        self.bars = bars
        self.events = events
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.es_positions = 0
        self.es_holdings = 0
             
        self.debt = 0
        self.cash = initial_capital
        self.value = initial_capital
        
    def update(self, event):
        """
        Adds a new record to the positions matrix for the current market data
        bar. This reflects the PREVIOUS bar, i.e. all current market data at
        this stage is known (OLHCVI).
        
        Makes use of a MarketEvent from the events queue.
        """
        
        bars = self.bars.get_latest_bars(N=1)
        price_close = bars[0][4]
        self.es_holdings = self.es_positions * price_close
        
        
    def update_positions_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the positions matrix to reflect
        the new position.
        
        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
            
        # Update positions list with new quantities
        self.es_positions += fill_dir*fill.quantity
        
    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix to reflect the
        holdings value.
        
        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
            buy_price = self.bars.get_latest_bars(N=1)[0][4] # Close price
            #self.cash -= abs(fill_dir * buy_price * fill.quantity)
        if fill.direction == 'SELL':
            fill_dir = -1
            buy_price = self.bars.get_latest_bars(N=1)[0][4] # Close price
            #self.debt += abs(fill_dir * buy_price * fill.quantity)
        self.cash -= fill.commission    
        # Update holdings list with new quanities
        fill_cost = self.bars.get_latest_bars(N=1)[0][4] # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.cash -= cost
        print(cost)
        print(self.cash)    
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        """
        
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
    def generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity sizing of
        the signal object, without risk management or positions sizing
        considerations.
        
        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None
        
        symbol = signal.symbol
        direction = signal.signal_type
        strength = 1
        
        mkt_quantity = floor(1*strength)
        cur_quantity = self.es_positions
        order_type = 'MKT'
        
        if direction == 'LONG':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
            
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order
        
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio
        logic.
        """
        
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)
            
    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings list of dictionaries.
        """
        
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0*curve['returns'].cumprod())
        self.equity_curve = curve
