class EarningsStrategy:
    """
    This strategy buys when the company is PE is below pe_to_buy (defaults to 15) and 
    sells when it is above pe_to_sell (defaults to 25).
    The PE results from averaging over years_to_average (defaults 5). 
    If there is not years_to_average before the current date, then it doesn't buy
    """    
    def __init__(self, years_to_average=5, pe_to_buy=15, pe_to_sell=25):
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
        print(pe)
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
            return True, {"eps_"+str(self.years_to_average): (sell_date, pe)}
        return False, {}
    



class CurrentLiabilitiesStrategy(EarningsStrategy):
    def __init__(self, years_to_average=5, pe_to_buy=15, pe_to_sell=25, curr_al_ratio=1):
        super().__init__(years_to_average, pe_to_buy, pe_to_sell, )
        self.current_asset_liability_ratio = curr_al_ratio

    def buy(self, fiscal_date_ending, buy_date, company_price, stock):
        buy, info = super().buy(fiscal_date_ending,buy_date,company_price,stock)
        if not buy:
            return False, {}
        else:
            balance_statement = stock.balance_sheet()
            current_balance_statement = balance_statement[balance_statement["fiscalDateEnding"] == fiscal_date_ending].iloc[0]
            
            curr_liabilities = current_balance_statement["totalCurrentLiabilities"]
            curr_assets = current_balance_statement["totalCurrentAssets"] 
            curr_assets_liabilities_ratio = curr_assets/curr_liabilities
            #print(assets_liabilities_ratio)
            good_debt = curr_assets_liabilities_ratio >= self.current_asset_liability_ratio
            if not good_debt:
                return False, {}
            else:
                info["curr-asset-liab-ratio"] = (buy_date, curr_assets_liabilities_ratio)
                return True, info


    def sell(self, fiscal_date_ending, sell_date, company_price, stock):
        sell, info = super().sell(fiscal_date_ending,sell_date,company_price,stock)
        if not sell:
            return False, {}
        else:
            return True, info



class LiabilitiesStrategy(CurrentLiabilitiesStrategy):
    def __init__(self, years_to_average=5, pe_to_buy=15, pe_to_sell=25, curr_al_ratio=1, noncurr_al_ratio=1):
        super().__init__(years_to_average, pe_to_buy, pe_to_sell, curr_al_ratio)
        self.asset_liability_ratio = noncurr_al_ratio

    def buy(self, fiscal_date_ending, buy_date, company_price, stock):
        buy, info = super().buy(fiscal_date_ending,buy_date,company_price,stock)
        if not buy:
            return False, {}
        else:
            balance_statement = stock.balance_sheet()
            current_balance_statement = balance_statement[balance_statement["fiscalDateEnding"] == fiscal_date_ending].iloc[0]
            
            liabilities = current_balance_statement[["totalNonCurrentLiabilities","totalCurrentLiabilities"]].sum() 
            assets = current_balance_statement[["totalNonCurrentAssets","totalCurrentAssets"]].sum() 
            assets_liabilities_ratio = assets/liabilities
            good_debt = assets_liabilities_ratio >= self.asset_liability_ratio
            if not good_debt:
                return False, {}
            else:
                info["asset-liab-ratio"] = (buy_date, assets_liabilities_ratio)
                return True, info


    def sell(self, fiscal_date_ending, sell_date, company_price, stock):
        sell, info = super().sell(fiscal_date_ending,sell_date,company_price,stock)
        if not sell:
            return False, {}
        else:
            return True, info
