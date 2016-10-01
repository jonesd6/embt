#! python3
# event.py

class Event(object):
    """
    Event is base class providing an interface for all subsequent (inherited)
    events, that will trigger further events in the trading infrastructure.
    """
    
    pass
    
class MarketEvent(Event):
    """
    Handles the event of receiving a newmarket update with corresponding bars.
    """
    
    def __init__(self):
        """
        Initializes the MarketEvent.
        """
        self.type = 'MARKET'
        
class SignalEvent(Event):
    """
    Handles the event of sending a signal froma strategy object. This is
    received by a Portfolio object and acted upon.
    """
    
    def __init__(self, symbol, datetime, signal_type):
        """
        Initializes the SignalEvent.
        
        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
        """
        
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
    
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system. The order
    contains a symbol (e.g. GOOG), a type (market or limit), quantity, and
    direction.
    """
    
    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initilizes the order type, setting whether it is a Market order ('MKT')
        or Limit order ('LMT'), has a quantity (integral) and its direction
        ('BUY' or 'SELL').
        
        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        
    def print_order(self):
        
        
        print("Order: Symbol=%s, Type-%s, Quantity=%s, Direction=%s" %
                (self.symbol, self.order_type, self.quantity, self.direction))
                
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned from a brokerage.
    Stores the quantity of an instrument actually filled and at what price.
    In addition, stores the commission of the trade from the brokerage.
    """
    
    def __init__(self, timeindex, symbol, exchange, quantity, direction, 
                 fill_cost, commission=None):
        """
        Initializes the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional commission.
                
        If commission is not provided, the Fill objext will calculate
        it based on the trade size and IB fees.
                
        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
                
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
                
        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission
                   
    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an IB fee structure for API,
        in USD.
        
        Uses fixed pricing structure.
        
        Based on "US API Direction Order":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """

        min_per_order = 1.0
        commission_per_share = 0.005
        fill_cost = max(min_per_order, commission_per_share*self.quantity)

        return fill_cost