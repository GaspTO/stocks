class EarningsStrategy:
    """
    This strategy buys when the company is PE is below pe_to_buy (defaults to 15) and 
    sells when it is above pe_to_sell (defaults to 25).
    The PE results from averaging over years_to_average (defaults 5). 
    If there is not years_to_average before the current date, then it doesn't buy
    """    
    def __init__(self, pe_to_buy=15, pe_to_sell=25, years_to_average=5):
        self.pe_to_buy = pe_to_buy
        self.pe_to_sell = pe_to_sell
        self.years_to_average = years_to_average
        if pe_to_sell < pe_to_buy:
            raise ValueError("PE to Sell is smaller than PE to buy")

    def buy(self, fiscal_date_ending, buy_date, company_price, stock):
        income_statement = stock.income_statement()
        last_n_statements = income_statement[income_statement["fiscalDateEnding"] <= fiscal_date_ending].iloc[0:self.years_to_average]
        if len(last_n_statements) != self.years_to_average:
            return False, {}
        pe = company_price / last_n_statements["netIncome"].mean()
        if pe <= self.pe_to_buy and pe > 0:
            return True, {"eps_"+str(self.years_to_average): (buy_date, pe)}
        return False, {}


    def sell(self, fiscal_date_ending, sell_date, company_price, stock):
        income_statement = stock.income_statement()
        last_n_statements = income_statement[income_statement["fiscalDateEnding"] <= fiscal_date_ending].iloc[0:self.years_to_average]
        if len(last_n_statements) != self.years_to_average:
            return False, {}
        pe = company_price / last_n_statements["netIncome"].mean()
        if pe >= self.pe_to_sell and pe > 0:
            return True, {}
        return False, {}
    



class DebtEarningsStrategy(EarningsStrategy):
    def __init__(self, pe_to_buy=15, pe_to_sell=25, asset_to_liability_ratio=1, years_to_average=5):
        super().__init__(pe_to_buy, pe_to_sell, years_to_average)
        self.asset_to_liability_ratio = asset_to_liability_ratio

    def buy(self, fiscal_date_ending, buy_date, company_price, stock):
        simple_buy, info = super().buy(fiscal_date_ending,buy_date,company_price,stock)
        if not simple_buy:
            return False, {}
        else:
            balance_statement = stock.balance_sheet()
            current_balance_statement = balance_statement[balance_statement["fiscalDateEnding"] == fiscal_date_ending].iloc[0]
            current_liabilities_assets_ratio = current_balance_statement["totalCurrentAssets"]/current_balance_statement["totalCurrentLiabilities"]
            good_debt = current_liabilities_assets_ratio >= self.asset_to_liability_ratio
            if not good_debt:
                return False, {}
            else:
                info["current-liabilities-assets-ratio"] = (buy_date, current_liabilities_assets_ratio)
                return True, info


    def sell(self, fiscal_date_ending, sell_date, company_price, stock):
        if not super().sell(fiscal_date_ending,sell_date,company_price,stock):
            return False, {}
        else:
            return True, {}
