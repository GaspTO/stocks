import os

class Stock:
    """
    APIs:
        Available: alphavantage

        Future: financialmodelingprep

    General:
        The idea of these APIs is to return pandas dataframes with the financial
        statements (and market capitalization) of the respective company.
        Dataframes are dynamic structures that can have many different fields,
        and, depending on the platform/database we use, these dataframes can
        have more or less fields. With this being said, each statement needs
        to have a minimum of reliable columns, and each method utilizing these
        statements should only rely on these and not any extra one.
    """

    ## MAIN COLUMNS
    INCOME_COLUMNS = ['fiscalDateEnding', 'reportedCurrency',
                        'revenue', 'costOfRevenue', 'grossMargin', 'operatingExpenses',
                        'operatingIncome', 'incomeBeforeTax', 'netIncome',
                        'eps', 'epsdiluted',
                        'weightedAverageSharesOut', 'weightedAverageSharesOutDil']

    BALANCE_COLUMNS = ['fiscalDateEnding', 'reportedCurrency',
                        'cashAndCashEquivalents', 'shortTermInvestments', 'accountsReceivables', 'inventory', 'totalCurrentAssets',
                        'propertyPlantEquipmentNet', 'longTermInvestments', 'goodwill', 'intangibleAssets', 'otherNonCurrentAssets', 'totalNonCurrentAssets', 
                        'totalAssets',
                        'totalCurrentLiabilities',
                        'longTermDebt', 'totalNonCurrentLiabilities',
                        'preferredStock', 'commonStock', 'retainedEarnings',
                        'totalEquity', 'nonControllingInterest', 'totalStockholdersEquity', 'totalLiabilitiesAndTotalEquity']
        
    CASH_COLUMNS = ['fiscalDateEnding', 'reportedCurrency',
                    'cashAtBeginningOfPeriod', 'netIncome',
                    'netCashProvidedByOperatingActivities',
                    'netCashUsedForInvestingActivities',
                    'debtRepayment', 'commonStockIssued', 'commonStockRepurchased', 'dividendsPaid', 'netCashUsedProvidedByFinancingActivities',
                    'netChangeInCash', 'cashAtEndOfPeriod']
                    
        

    def __init__(self, base_url, symbol, apikey, dir_path="stock_data", forbid_fetch=False):
        ## Basic settings
        self.base_url = base_url
        self.symbol = symbol
        self.apikey = apikey
        self.dir_path = dir_path 
        self.forbid_fetch = forbid_fetch
        
        ## Cache
        self._income_statement = None
        self._balance_sheet = None
        self._cash_flow = None
        self._market_cap = None


    def fetch(self, data_type, **kwargs):
        """Generic method to fetch data based on the type specified."""
        raise NotImplementedError


    def income_statement(self, dense=True):
        """ Income statements """
        raise NotImplementedError


    def balance_sheet(self, dense=True):
        """ Balance sheet statements """
        raise NotImplementedError


    def cash_flow(self, dense=True):
        """ Cash flow statements """
        raise NotImplementedError


    def market_cap(self, max_years=5):
        """ Market cap over time """
        raise NotImplementedError
        

    def load(self):
        """ Loads attributes from a csv instead of fetching """
        raise NotImplementedError

    
    def save(self):
        """ Saves attributes to a csv """
        raise NotImplementedError