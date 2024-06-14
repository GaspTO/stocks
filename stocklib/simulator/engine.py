import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime
from copy import deepcopy

# A simple argmax function
argmax = lambda lst: max(enumerate(lst), key=lambda x: x[1])[0]

#
def average_annual_return_compound(principal, final_amount, years):
    average_annual_return = (final_amount / principal)**(1/years) - 1
    return average_annual_return


class Engine:
    
    def __init__(self, strategy, stock):
        self.strategy = strategy
        self.stock = stock


    def simulate(self, start_year:int=None, end_year:int=None):
        """ Simulates money and networth gains at the end_year, starting to invest at
        start_year. This simulation assumes we are buying and selling the whole company.

        The simulation buys approximately two months after the filling date. It should be less
        than 3 months so that we do not miss on quarterly earnings, and at least 1 month
        just for caution.

        Args:
            start_year (int): fiscal year to start iterating over
            end_year (int): fiscal year to end

        Returns:
            money - money made or spent in the total simulation
            networth - capitalization of the company at the end_year
        """
        if end_year is not None and end_year > datetime.now().year:
            raise ValueError("Engine::simulate: End year needs to be previous to the current one")

        if not self.stock.is_open:
            self.stock.open(correct=True)

        base_date_key, delta_months = "fiscalDateEnding", 3
        money, own = 0, False

        # Get statements
        cash_statement = self.stock.cash_flow()
        first_statement_date = cash_statement.iloc[-1][base_date_key].to_pydatetime()
        last_statement_date = cash_statement.iloc[0][base_date_key].to_pydatetime()

        market_cap = self.stock.market_cap(first_statement_date, last_statement_date + relativedelta(years=1))
        if market_cap.empty:
            raise ValueError("Engine::simulate: Can't retrieve market cap")
        if cash_statement.empty:
            raise ValueError("Engine::simulate: Cash statement is empty")
        
        # Crop cash flow statement
        earliest_mc_date = market_cap.iloc[-1]["date"] - pd.DateOffset(months=delta_months)
        if start_year is None or earliest_mc_date > start_year:
            start_year = earliest_mc_date   
  
        latest_mc_date = market_cap.iloc[0]["date"] - pd.DateOffset(months=delta_months)
        if end_year is None or latest_mc_date < end_year:
            end_year = latest_mc_date

        statement_base_dates = cash_statement[base_date_key] ## We'll use fiscalDateEnding and not fillingDate because the filling date is often wrong
        cash_statement = cash_statement[(statement_base_dates < end_year) & (statement_base_dates > start_year)]

        if cash_statement.empty:
            raise ValueError("Engine::simulate: Cash statement is empty after restricting dates to market cap")


        # Main
        simulation_result = SimulationResult(self.stock.company_name, self.stock.symbol)

        for index in range(len(cash_statement)-1,-1,-1):
            current_cash_statement = cash_statement.iloc[index] 
            base_date = current_cash_statement[base_date_key]

            # Buy one month after the filling date
            base_date_plus_delta = base_date + pd.DateOffset(months=delta_months) 
            market_cap["diff"] = (market_cap["date"] - base_date_plus_delta).abs()
            market_cap_closest_entry = market_cap.loc[market_cap['diff'].idxmin()]
            considering_market_date, company_price = market_cap_closest_entry[["date","marketCap"]]
            
            # Checks
            if abs(market_cap_closest_entry["diff"].days) > 15:
               raise ValueError("Engine::simulate: Something went wrong. Tolerance is at most 15 days")## Allow only a tolerance of 15 days

            # Store market cap
            #!simulation_result.market_cap(considering_market_date, company_price)

            fiscal_date_ending = current_cash_statement["fiscalDateEnding"]  ## yes, yes, it's the same as base_date at the moment, but its not the same thing
            # Dividends
            if own:
                dividends = current_cash_statement["dividendsPaid"] * -1 # dividends are accounted as negative in the statement
                assert dividends >= 0
                simulation_result.info("dividend",fiscal_date_ending, dividends)

            # Buy/Sell ?
            buy, info_buy = self.strategy.buy(fiscal_date_ending, considering_market_date, company_price, self.stock)            
            sell, info_sell = self.strategy.sell(fiscal_date_ending, considering_market_date, company_price, self.stock)
            if not own and buy:
                money -= company_price
                own = True
                simulation_result.buy("market_cap",considering_market_date, company_price)
                for metric, (date, value) in info_buy.items():
                    simulation_result.buy(metric, date, value)
                
            elif own and sell:
                money += company_price
                own = False
                simulation_result.sell("market_cap",considering_market_date, company_price)
                for metric, (date, value) in info_sell.items():
                    simulation_result.sell(metric, date, value)
                

        #net_worth = company_price if own else 0
        if own:
            simulation_result.end(date=considering_market_date, value=company_price)
        else:
            simulation_result.end()

        #return money, net_worth, buys, sells 
        return simulation_result
    



class SimulationResult:
    def __init__(self, company_name, symbol=None):
        self.company_name = company_name
        self.symbol = symbol

        self.buy_df = []
        self.sell_df = []
        self.info_df = []
        self.end_simulation = False
     
    
    def buy(self, metric, date, value):
        if self.end_simulation:
            raise ValueError("Simulation is over")
        #self.buys.append((date,value))
        self.buy_df.append({"operation": "buy", "metric": metric, "date": date, "value": value})
        return self
    

    def sell(self, metric, date, value):
        if self.end_simulation:
            raise ValueError("Simulation is over")
        #self.sells.append((date,value))
        self.sell_df.append({"operation": "sell", "metric": metric, "date": date, "value": value})
        return self


    def info(self, metric, date, value):
        if self.end_simulation:
            raise ValueError("Simulation is over")
        self.info_df.append({"operation": "info", "metric": metric, "date": date, "value": value})
        return self
    
    
    def end(self, date=None, value=None):
        if date is None and value is None:
            self.end_ownership = False
        elif date is not None and value is not None:
            self.end_ownership = True
            self.end_date = date
            self.end_market_cap = value
        else:
            raise ValueError("Error!")

        self.end_simulation = True
        self.buy_df = pd.DataFrame(self.buy_df, columns=["operation", "metric", "date", "value"]).sort_values("date")
        self.sell_df = pd.DataFrame(self.sell_df, columns=["operation", "metric", "date", "value"]).sort_values("date")
        self.info_df = pd.DataFrame(self.info_df, columns=["operation", "metric", "date", "value"]).sort_values("date")
        return self

    #
    # Methods after simulation ends
    #
    def gather_statistics(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        
        if self.statistics_gathered:
            return
        else:
            self.statistics_gathered = True
        
        df = self.df
        self.total_spent = sum(df[df["operation"] == "buy"]["value"])
        self.total_sold = sum(df[df["operation"] == "sell"]["value"])
        self.total_dividends = sum(df[df["operation"] == "dividend"]["value"])
        self.total_earned = self.total_sold + self.total_dividends
        
        self.returns = []
        buys, sells = df[df["operation"] == "buy"], df[df["operation"] == "sell"]
        sold_buys = buys.iloc[0:len(sells)]
        for i in range(len(sells)):
            b, s = sold_buys.iloc[i], sells.iloc[i]
            years = (s["date"] - b["date"]).days / 365
            avg_ret = average_annual_return_compound(b["value"], s["value"], years)
            self.returns.append(avg_ret)

        if len(self.returns) == 0:
            self.average_return = None
        else:
            self.average_return = sum(self.returns)/len(self.returns)
            

        _ownership_df = df[df["operation"] == "ownership"]
        if len(_ownership_df) == 0:
            self.ownership = 0
        else:
            self.ownership = _ownership_df.value.item()
            self.ownership_return = average_annual_return_compound(self.ownership, sold_buys.iloc[-1]["value"], years)
            self.returns_with_ownership = deepcopy(self.returns) + [self.ownership_return]
            self.average_return_with_ownership = sum(self.returns_with_ownership)/len(self.returns_with_ownership)
        
        self.net_worth = self.total_earned - self.total_spent + self.total_dividends + self.ownership 
        

    @property
    def total_spent(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        return sum(self.buy_df[self.buy_df["metric"] == "market_cap"]["value"])
    
    @property
    def total_sold(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        return sum(self.sell_df[self.sell_df["metric"] == "market_cap"]["value"])
    
    @property
    def total_dividends(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        return sum(self.info_df[self.info_df["metric"] == "dividend"]["value"])

    @property
    def total_earned(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        return self.total_sold + self.total_dividends
    
    @property
    def dividends(self): #!!! TO BE ADAPTED
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        _dividends = []
        buys = self.buy_df[self.buy_df["metric"] == "market_cap"]
        sells = self.sell_df[self.sell_df["metric"] == "market_cap"]
        dividends = self.info_df[self.info_df["metric"] == "dividend"]
        sold_buys = buys.iloc[0:len(sells)]
        for i in range(len(sells)):
            b, s = sold_buys.iloc[i], sells.iloc[i]
            dividend_condition = (dividends["date"] < s["date"]) & (dividends["date"] >= b["date"])
            dividend_sum = dividends[dividend_condition]["value"].sum()
            _dividends.append((s["date"],dividend_sum))

        if len(sells) < len(buys):
            dividend_condition = (dividends["date"] > buys.iloc[-1]["date"])
            dividend_sum = dividends[dividend_condition]["value"].sum()
            _dividends.append((s["date"],dividend_sum))

        return pd.DataFrame(_dividends, columns=["date","dividend"])
    
    @property
    def returns(self):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        _returns = []
        buys = self.buy_df[self.buy_df["metric"] == "market_cap"]
        sells = self.sell_df[self.sell_df["metric"] == "market_cap"]
        dividends = self.info_df[self.info_df["metric"] == "dividend"]
        sold_buys = buys.iloc[0:len(sells)]
        for i in range(len(sells)):
            b, s = sold_buys.iloc[i], sells.iloc[i]
            years = (s["date"] - b["date"]).days / 365

            dividend_condition = (dividends["date"] < s["date"]) & (dividends["date"] >= b["date"])
            dividend_sum = dividends[dividend_condition]["value"].sum()
            avg_ret = average_annual_return_compound(b["value"], s["value"]+ dividend_sum, years)
            _returns.append((s["date"],avg_ret))

        return pd.DataFrame(_returns, columns=["date","return"])
    
    @property
    def average_return(self):
        returns = self.returns
        if len(returns):
            return returns["return"].mean()
        return None


    def print(self, buy_metrics=[], sell_metrics=[]):
        if self.end_simulation is False:
            raise ValueError("End simulation first")
        
        # Buys
        buys = self.buy_df[self.buy_df["metric"] == "market_cap"].reset_index(drop=True)
        for metric in buy_metrics:
            metric_df = self.buy_df[self.buy_df["metric"] == metric].copy()
            metric_df.drop(columns=["metric"], inplace=True)
            metric_df.rename(columns={'value': metric}, inplace=True)
            buys = buys.merge(metric_df)
        buys.drop(columns=["metric"], inplace=True)
        buys.rename(columns={'value': 'market_cap'}, inplace=True)
        
        # Sells
        sells = self.sell_df[self.sell_df["metric"] == "market_cap"].reset_index(drop=True)
        for metric in sell_metrics:
            metric_df = self.sell_df[self.sell_df["metric"] == metric].copy()
            metric_df.drop(columns=["metric"], inplace=True)
            metric_df.rename(columns={'value': metric}, inplace=True)
            sells = sells.merge(metric_df)
        sells.drop(columns=["metric"], inplace=True)
        sells.rename(columns={'value': 'market_cap'}, inplace=True)

        if sells.empty:
            return

        sells = sells.merge(self.dividends).merge(self.returns)

        buys["market_cap"] /= 10**6
        sells["market_cap"] /= 10**6
        sells["dividend"] /= 10**6

        if len(buys) != len(sells):
            last_market_cap = self.df[self.df["operation"] == "marketCap"].iloc[-1]
            hypothetical_years = (last_market_cap["date"] - buys.iloc[-1]["date"]).days / 365
            if hypothetical_years == 0:
                    hypothetical_return = 0
            else:
                hypothetical_return = average_annual_return_compound(buys.iloc[-1]["value"],last_market_cap["value"]/10**6,hypothetical_years)
            new_row = {
                "operation": "hypothetical sell",
                "date": last_market_cap["date"],
                "value": last_market_cap["value"]/10**6,
                "return": hypothetical_return,
                "dividends": self.dividends[-1]/10**6
            }
            sells.loc[len(sells)] = new_row
            hypothetical = True
        else:
            hypothetical = False

        print("[Company]: " + str(self.company_name))
        print("[Symbol]: " + str(self.symbol))
        if len(buys) >  0:
            print("[BUYS]")
            print(buys, end="\n")
            print("[SELLS]")
            print(sells, end="\n")
            print("[Average_return]: " + str(self.average_return))

            if hypothetical:
                returns = self.returns
                if hypothetical_years == 0:
                    count = 0
                else:
                    count = 1
                hypothetical_avg_return = (sum(returns) + hypothetical_return)/(len(returns) + count)
                print("[Hypothetical average return]: " + str(hypothetical_avg_return))
        else:
            print("--No buys--")
        print("\n\n")


        
        
        
