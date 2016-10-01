#! python3
# data.py

import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod

from event import MarketEvent

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for all
    subsequent (inherited) data handlers (both live and historic).
    
    The goal of a (derive) DataHandler object is to output a generated set of
    bars (OLHCVI) for each symbol requested.
    
    This will replicate how a live strategy would function as current market
    data would be sent "down the pipe". Thus a historic and live system will be
    treated identically by the rest of the backtesting suite.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list, or fewer if less
        bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")
        
    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bar to the latest symbol structure for all symbols in
        the symbol list.
        """
        
        raise NotImplementedError("Should implement update_bars()")
        
class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for each requested
    symbol from disk and provide an interface to obtain the "latest" bar in a
    manner identical to a live trading interface.
    """
    
    def __init__(self, events, csv_dir, symbol_list):
        """
        Initializes the historic data handler by requseting the locaiton of the
        CSV files and a list of symbols.
        
        It will be assumed that all files are of the form "symbol.csv", where
        symbol is a string in the list.
        
        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        
        self._open_convert_csv_files()
        
    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting them into pandas
        DataFrames within a symbol dictionary.
        
        Ensure proper formatting for the data source being used.
        """
        
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on datetime
            self.symbol_data[s] = pd.io.parsers.read_csv(
                                    os.path.join(self.csv_dir, '%s.csv' % s),
                                    header = 0, index_col = 0,
                                    names = ['datetime','close','volume'])
                                    
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
                
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
            
        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = (self.symbol_data[s]
                                       .reindex(index=comb_index, method='pad') 
                                       .iterrows())
                                        
    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of (symbol, datetime,
        close, volume).
        """
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, 
                         datetime.datetime.strptime(b[0], '%Y-%m-%d %H:%M:%S'),
                         b[1][0],
                         b[1][1]])
                         
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list, or N-k if less
        available.
        """
        
        try:
            bars_list = self.latest_symbol_data[symbol]
        except:
            print("That symbol is not available in the historic data set")
        else:
            return bars_list[-N:]
            
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure for all symbols
        in the symbol list.
        """
        
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
        
class EMiniCSVHandler(DataHandler):
    """
    Data handler for the e-mini csv.
    """
    
    def __init__(self, events, csv_filename):
        """
        Initializes the historic data handler by requseting the locaiton of the
        CSV files and a list of symbols.
        
        It will be assumed that all files are of the form "symbol.csv", where
        symbol is a string in the list.
        
        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        
        self.events = events
        self.csv_filename = csv_filename
        self.csv_data = {}
        self.latest_data = []
        self.continue_backtest = True    
        self._open_convert_csv_files()
        
    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting them into pandas
        DataFrames within a symbol dictionary.
        
        Ensure proper formatting for the data source being used.
        """
        
        self.csv_data = pd.read_csv(self.csv_filename, 
                                    delimiter=',',
                                    header=0,
                                    index_col=0)
                                    
        new_index = self.csv_data.index     
        self.csv_data = self.csv_data.reindex(new_index).iterrows()
 
    def _get_new_bar(self):
        """
        Returns the latest bar from the data feed as a tuple of:
        ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Count', 'WAP'].
        """
        for b in self.csv_data:
            yield tuple([datetime.datetime.strptime(b[0], '%Y%m%d %H:%M:%S'), 
                         b[1][0], b[1][1], b[1][2], b[1][3], b[1][4], b[1][5],
                         b[1][6]])
                         
    def get_latest_bars(self, N=1):
        """
        Returns the last N bars from the latest_symbol list, or N-k if less
        available.
        """
        
        try:
            bars_list = self.latest_data
        except:
            print("That symbol is not available in the historic data set")
        else:
            return bars_list[-N:]
            
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure for all symbols
        in the symbol list.
        """
        
        try:
            bar = next(self._get_new_bar())
        except StopIteration:
            self.continue_backtest = False
        else:
            if bar is not None:
                self.latest_data.append(bar)
        self.events.put(MarketEvent())