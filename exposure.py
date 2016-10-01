#! python3
# exposure.py

class ExposureManager():

    def __init__(self, 
                 target_leverage,
                 target_long_exposure,
                 target_short_exposure,
                 initial_balance):
        """
        Initialize the ExposureManager.
        
        Parameters:
        target_leverage - 
        target_long_exposure -
        target_short_exposure -
        initial_balance -
        """
        
        self.buying_power = initial_balance*2.0
        self.target_leverage = target_leverage
        self.target_long_exposure = target_long_exposure
        self.target_short_exposure = target_short_exposure
        
        self.current_long_exposure = 0.0
        self.current_short_exposure = 0.0
        self.current_leverage = 0.0
        
        self.available_cash_short = 0.0
        self.available_cash_long = 0.0
        
    def calculate_current_leverage(self, portfolio):
        #total number of long positions
        #total number of short positions
        #total capital in portfolio
        #return gross leverage
        #self.current_leverage = portfolio.current_holdings/portfolio.value
        #return self.current_leverage
        return 1
    def update(self, current_holdings, symbol_list):
        self.current_long_exposure = 0
        self.current_short_exposure = 0
        for ticker in symbol_list:
            if current_holdings[ticker] < 0:
                self.current_short_exposure += abs(current_holdings[ticker])
            elif current_holdings[ticker] > 0:
                self.current_long_exposure += current_holdings[ticker]      
        
    def calculate_buying_power(self, portfolio):
        """
        Calculate cash based on non-day-trading margin.
        """
        
        self.buying_power = portfolio.current_holdings['cash']*2.0
        self.calculate_current_leverage(portfolio)
        self.available_cash_short = self.buying_power*(1.0-self.current_leverage)
        self.available_cash_long = self.buying_power
        
        return self.available_cash_short, self.available_cash_long
