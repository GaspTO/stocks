import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime

class Engine:
    
    def __init__(self, strategy, stock):
        self.strategy = strategy
        self.stock = stock


    def simulate(self, start_year:int, end_year:int):
        """ Simulates money and networth gains at the end_year, starting to invest at
        start_year. This simulation assumes we are buying and selling the whole company.

        The simulation buys approximately two months after the filling date. It should be less
        than 3 months so that we do not miss on quarterly earnings, and at least 1 month
        just for caution.

        Args:
            start_year (int): filling year to start iterating over
            end_year (int): filling year to end

        Returns:
            money - money made or spent in the total simulation
            networth - capitalization of the company at the end_year
        """
        if end_year < datetime.now().year:
            raise ValueError("End year needs to be previous to the current one")

        money, own = 0, False
        market_cap = self.stock.market_cap(datetime(start_year, 1, 1), datetime(end_year, 12, 31))
        cash_statement = self.stock.cash_flow()
        
        for year in range(start_year, end_year + 1):
            current_cash_statement = cash_statement[cash_statement["fillingDate"].dt.year == year]
            assert current_cash_statement.shape[0] == 1
            current_cash_statement = current_cash_statement.iloc[0]
            filling_date = current_cash_statement["fillingDate"]

            # buy one month after the filling date
            buy_sell_date = current_cash_statement["fillingDate"] + relativedelta(months=2) 
                        
            # market cap
            market_cap["diff"] = (market_cap["date"] - buy_sell_date).abs()
            market_cap_closest_entry = market_cap.loc[market_cap['diff'].idxmin()]
            company_price = market_cap_closest_entry["marketCap"]
            assert market_cap_closest_entry["diff"].days <= 15 ## Allow only a tolerance of 15 days

            ## Dividends
            if own:
                money += current_cash_statement["dividendsPaid"]

            ## Buy/Sell ?            
            if not own and self.strategy.buy(filling_date, buy_sell_date, company_price, self.stock):
                money -= market_cap_closest_entry["marketCap"]
                own = True
            elif own and self.strategy.sell(filling_date, buy_sell_date, company_price, self.stock):
                money += market_cap_closest_entry["marketCap"]
                own = False

        net_worth = market_cap_closest_entry["marketCap"] if own else 0

        return money, net_worth











