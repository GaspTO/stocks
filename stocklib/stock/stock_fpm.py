from .stock_api import Stock
import pandas as pd
import requests
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

#! TODO check that everything is in dollars
def find_common(a, b, c):
    if a == b or a == c:
        return a
    elif b == c:
        return b
    else:
        return None

class StockFPM(Stock):
    """
        STOCK API for the "Financial Modeling Prep" API
    """
    def __init__(self, company_name, symbol, apikey="Sek7iGkE1GvNjfD4mxMrAIdJCu8tpeIh", dir_path="stock_data", forbid_fetch=False, correct=True):
        base_url = f'https://financialmodelingprep.com/api/v3/'
        self.forbid_fetch = forbid_fetch
        super().__init__(base_url, company_name, symbol, apikey, dir_path)
        self._maximum_date = None
        self._minimum_date = None
      
        self._is_open = False  

    
    # IO and Basic operations
    def fetch(self, data_type, **kwargs):
        """Generic method to fetch data based on the type specified."""
        if self.forbid_fetch:
            raise ValueError("Fetching data is forbidden!")
        
        url = f"{self.base_url}{data_type}/{self.symbol}?apikey={self.apikey}"
        for key in kwargs:
            url += f"&{key}={kwargs[key]}"

        response = requests.get(url)

        if response.status_code == 429:
            raise ValueError("Limit API has been achieved")
        
        data = pd.DataFrame(response.json())

        if len(data) == 0:
            return pd.DataFrame()

        return data
    

    def open(self, correct=True):
        """
        Returns true if reports were read correctly and false otherwise.
        """
        if not self._is_open:
            
            self._set_income_statement()
            self._set_cash_flow()
            self._set_balance_sheet()

            if self._income_statement.empty or self._balance_sheet.empty or self._cash_flow.empty:
                raise ValueError("Can't retrieve statements")

            if correct:
                self._correct_reports()

            self._is_open = True

        else:
            raise ValueError("Already Opened")
        

    def close(self):
        self._income_statement = None
        self._balance_sheet = None
        self._cash_flow = None
        self._market_cap = None
        self._is_open = False

    @property
    def is_open(self):
        return self._is_open
    

    def save(self):
        # Create the directory for the symbol if it doesn't exist
        symbol_dir = os.path.join(self.dir_path, self.symbol)
        if not os.path.exists(symbol_dir):
            os.makedirs(symbol_dir)

        # Income statement  
        file_path = os.path.join(symbol_dir, "income_statement.csv")
        self.income_statement(dense=True).to_csv(file_path, index=False)

        # Balance sheet   
        file_path = os.path.join(symbol_dir, "balance_sheet.csv")
        self.balance_sheet(dense=True).to_csv(file_path, index=False)

        # Cash flow
        file_path = os.path.join(symbol_dir, "cash_flow.csv")
        self.cash_flow(dense=True).to_csv(file_path, index=False)

        # Market cap
        '''
        file_path = os.path.join(symbol_dir, "market_cap.csv")
        self.market_cap().to_csv(file_path, index=False)
        '''


    def load(self):
        symbol_dir = os.path.join(self.dir_path, self.symbol)
        inc, bs, cf, mc = False, False, False, False
        
        # Income statement  
        file_path = os.path.join(symbol_dir, "income_statement.csv")
        if os.path.exists(file_path):
            self._income_statement = pd.read_csv(file_path)
            self._income_statement["fiscalDateEnding"] = pd.to_datetime(self._income_statement["fiscalDateEnding"])
            self._income_statement["fillingDate"] = pd.to_datetime(self._income_statement["fillingDate"])
            inc = True

        # Balance sheet 
        file_path = os.path.join(symbol_dir, "balance_sheet.csv")
        if os.path.exists(file_path):
            self._balance_sheet = pd.read_csv(file_path)
            self._balance_sheet["fiscalDateEnding"] = pd.to_datetime(self._balance_sheet["fiscalDateEnding"])
            self._balance_sheet["fillingDate"] = pd.to_datetime(self._balance_sheet["fillingDate"])
            bs = True
        
        # Cash flow
        file_path = os.path.join(symbol_dir, "cash_flow.csv")
        if os.path.exists(file_path):
            self._cash_flow = pd.read_csv(file_path)
            self._cash_flow["fiscalDateEnding"] = pd.to_datetime(self._cash_flow["fiscalDateEnding"])
            self._cash_flow["fillingDate"] = pd.to_datetime(self._cash_flow["fillingDate"])
            cf = True

        # Market cap
        '''
        file_path = os.path.join(symbol_dir, "market_cap.csv")
        if os.path.exists(file_path):
            self._market_cap = pd.read_csv(file_path)
            self._market_cap["date"] = pd.to_datetime(self._market_cap["date"])
            mc = True
        '''

        return inc, bs, cf, mc 
    

    # Report
    def income_statement(self, dense=True):
        if not self._is_open:
            raise ValueError("Open stock first")
        
        if dense:
            return self._income_statement[self.INCOME_COLUMNS]
        else:
            return self._income_state


    def balance_sheet(self, dense=True):
        if not self._is_open:
            raise ValueError("Open stock first")
        
        if dense:
            return self._balance_sheet[self.BALANCE_COLUMNS]
        else:
            return self._balance_sheet
        

    def cash_flow(self, dense=True):
        if not self._is_open:
            raise ValueError("Open stock first")
        
        if dense:
            return self._cash_flow[self.CASH_COLUMNS]
        else:
            return self._cash_flow


    def _set_income_statement(self):
        """Fetches the latest income statement."""

        if self._income_statement is None:
            self._income_statement = self.fetch("income-statement",period="annual")
            if self._income_statement.empty:
                return False
            
            # Format income statement
            columns_order = ['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate','acceptedDate', 'calendarYear', 'period', 'link', 'finalLink',
             'revenue', 'costOfRevenue', 'grossProfit', 'grossProfitRatio', 'researchAndDevelopmentExpenses', 'generalAndAdministrativeExpenses', 
             'sellingAndMarketingExpenses', 'sellingGeneralAndAdministrativeExpenses', 'otherExpenses', 'operatingExpenses', 
             'costAndExpenses', 'operatingIncome', 'operatingIncomeRatio', 'interestIncome', 'interestExpense', 'depreciationAndAmortization', 
             'ebitda', 'ebitdaratio',
             'totalOtherIncomeExpensesNet', 'incomeBeforeTax', 'incomeBeforeTaxRatio', 
             'incomeTaxExpense', 'netIncome', 'netIncomeRatio', 
             'eps', 'epsdiluted', 'weightedAverageShsOut','weightedAverageShsOutDil']
            
            self._income_statement = self._income_statement[columns_order]                 
            self._income_statement = self._income_statement.drop(["symbol","cik","acceptedDate", "calendarYear","period","link","finalLink" ],axis=1)
            self._income_statement = self._income_statement.rename(columns={"date": "fiscalDateEnding", "grossProfit": "grossMargin",
                                                                            "weightedAverageShsOut": "weightedAverageSharesOut",
                                                                            "weightedAverageShsOutDil": "weightedAverageSharesOutDil"})
            for field in self._income_statement.keys()[3:]:
                self._income_statement[field]  = pd.to_numeric(self._income_statement[field], errors='coerce')

            self._income_statement['fiscalDateEnding'] = pd.to_datetime(self._income_statement['fiscalDateEnding'], errors='coerce')
            self._income_statement['fillingDate'] = pd.to_datetime(self._income_statement['fillingDate'], errors='coerce')
            self._income_statement = self._income_statement.sort_values("fiscalDateEnding", ascending=False)
  

    def _set_balance_sheet(self):
        """ Balance sheet statements """
        
        if self._balance_sheet is None:
            self._balance_sheet = self.fetch("balance-sheet-statement",period="annual")
            if self._balance_sheet.empty:
                return False

            # Format data
            columns_order = ['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate','acceptedDate', 'calendarYear', 'period', 'link', 'finalLink',
                'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 'netReceivables', 'inventory', 'otherCurrentAssets', 'totalCurrentAssets',
                'propertyPlantEquipmentNet', 'longTermInvestments', 'goodwill', 'intangibleAssets', 'goodwillAndIntangibleAssets', 'taxAssets', 'otherNonCurrentAssets', 'totalNonCurrentAssets', 
                'otherAssets', 'totalAssets',
                'shortTermDebt', 'accountPayables', 'taxPayables', 'deferredRevenue', 'otherCurrentLiabilities', 'totalCurrentLiabilities',
                'longTermDebt', 'deferredRevenueNonCurrent', 'deferredTaxLiabilitiesNonCurrent', 'otherNonCurrentLiabilities', 'totalNonCurrentLiabilities', 
                'otherLiabilities', 'capitalLeaseObligations', 'totalLiabilities',
                'preferredStock', 'commonStock', 'accumulatedOtherComprehensiveIncomeLoss', 'retainedEarnings',
                'totalStockholdersEquity', 'othertotalStockholdersEquity', 'minorityInterest', 'totalEquity', 'totalLiabilitiesAndStockholdersEquity', 'totalLiabilitiesAndTotalEquity',
                'totalInvestments', 'totalDebt', 'netDebt']

            self._balance_sheet = self._balance_sheet[columns_order]
            self._balance_sheet = self._balance_sheet.drop(["symbol","cik","acceptedDate", "calendarYear","period","link","finalLink"],axis=1)
            self._balance_sheet = self._balance_sheet.rename(columns={"date":"fiscalDateEnding",
                                                                      "netReceivables": "accountsReceivables",
                                                                      "minorityInterest":"nonControllingInterest"})
            for field in self._balance_sheet.keys()[3:]:
                self._balance_sheet[field]  = pd.to_numeric(self._balance_sheet[field], errors='coerce')

            self._balance_sheet['fiscalDateEnding'] = pd.to_datetime(self._balance_sheet['fiscalDateEnding'], errors='coerce')
            self._balance_sheet['fillingDate'] = pd.to_datetime(self._balance_sheet['fillingDate'], errors='coerce')
            self._balance_sheet = self._balance_sheet.sort_values("fiscalDateEnding", ascending=False)
     

    def _set_cash_flow(self):
        """ Cash flow statements """
        if self._cash_flow is None:
            self._cash_flow = self.fetch("cash-flow-statement", period="annual")
            if self._cash_flow.empty:
                return False

            # Format Data
            columns_order = ['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period', 'link', 'finalLink',
                            'cashAtBeginningOfPeriod', 'netIncome',
                            'depreciationAndAmortization', 'stockBasedCompensation', 'deferredIncomeTax', 'accountsReceivables', 
                                'inventory', 'accountsPayables', 'otherWorkingCapital', 'otherNonCashItems', 'netCashProvidedByOperatingActivities',
                            'investmentsInPropertyPlantAndEquipment', 'acquisitionsNet', 'purchasesOfInvestments', 'salesMaturitiesOfInvestments', 'otherInvestingActivites', 'netCashUsedForInvestingActivites',
                            'debtRepayment', 'commonStockIssued', 'commonStockRepurchased', 'dividendsPaid', 'otherFinancingActivites', 'netCashUsedProvidedByFinancingActivities',
                            'effectOfForexChangesOnCash',
                            'netChangeInCash', 'cashAtEndOfPeriod', 
                            'operatingCashFlow', 'capitalExpenditure', 'freeCashFlow']

            self._cash_flow = self._cash_flow[columns_order]
            self._cash_flow = self._cash_flow.drop(["symbol","cik","acceptedDate", "calendarYear","period","link","finalLink"],axis=1)
            self._cash_flow = self._cash_flow.rename(columns={"date":"fiscalDateEnding",
                                                            "otherInvestingActivites":"otherInvestingActivities",
                                                            "netCashUsedForInvestingActivites":"netCashUsedForInvestingActivities",
                                                            "otherFinancingActivites":"otherFinancingActivities",
                                                            "netCashUsedProvidedByFinancingActivites":"netCashUsedProvidedByFinancingActivities"})
            for field in self._cash_flow.keys()[3:]:
                self._cash_flow[field]  = pd.to_numeric(self._cash_flow[field], errors='coerce')

            self._cash_flow['fiscalDateEnding'] = pd.to_datetime(self._cash_flow['fiscalDateEnding'], errors='coerce')
            self._cash_flow['fillingDate'] = pd.to_datetime(self._cash_flow['fillingDate'], errors='coerce')
            self._cash_flow = self._cash_flow.sort_values("fiscalDateEnding", ascending=False)


    def _correct_reports(self):        
        if (self._income_statement.empty or self._balance_sheet.empty or self._cash_flow.empty):
            raise ValueError("Statements are empty")
        
        income_fiscalDateEndings =  self._income_statement["fiscalDateEnding"]
        balance_fiscalDateEndings = self._balance_sheet["fiscalDateEnding"]
        cash_fiscalDateEndings = self._cash_flow["fiscalDateEnding"]

        intersection_fiscalDateEndings = set(income_fiscalDateEndings) & set(balance_fiscalDateEndings) & set(cash_fiscalDateEndings)
 
        self._income_statement = self._income_statement[self._income_statement["fiscalDateEnding"].isin(intersection_fiscalDateEndings)]
        self._balance_sheet = self._balance_sheet[self._balance_sheet["fiscalDateEnding"].isin(intersection_fiscalDateEndings)]
        self._cash_flow = self._cash_flow[self._cash_flow["fiscalDateEnding"].isin(intersection_fiscalDateEndings)]

        if (self._income_statement.empty or self._balance_sheet.empty or self._cash_flow.empty):
            raise ValueError("Corrections made the statements empty")



    def market_cap(self, start_date=None, end_date=None):
        """ Market cap over time """
        def ensure_datetime(date):
            if isinstance(date, str):
                return datetime.strptime(date, "%Y-%m-%d").date()
            return date

        # Convert start_date and end_date
        if end_date is None:
            end_date = datetime.today().date()
        else:
            end_date = ensure_datetime(end_date)

        if start_date is None:
            start_date = end_date - relativedelta(years=5)
        else:
            start_date = ensure_datetime(start_date)

        assert end_date > start_date

        market_cap = []
        current = end_date
        while start_date <= current:
            until = current 
            since = current - relativedelta(years=5) - relativedelta(days=1)
            params = {"from":since.strftime("%Y-%m-%d"), "to":until.strftime("%Y-%m-%d") }
            mc = self.fetch("historical-market-capitalization", **params)
            if len(mc) == 0:
                break
            market_cap.append(mc)
            current = current - relativedelta(years=5)
        
        if len(market_cap) == 0:
            market_cap = pd.DataFrame() # empty
        else:
            market_cap = pd.concat(market_cap, ignore_index=True)
            market_cap["date"] = pd.to_datetime(market_cap ["date"])
            market_cap = market_cap[["symbol","date","marketCap"]]

        return market_cap


    def __str__(self):
        return self.company_name + "[" + self.symbol + "]"