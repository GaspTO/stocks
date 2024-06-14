import requests
import pandas as pd
import os
from .stock_fpm import StockFPM
from .stock_evaluator import StockEvaluator
from datetime import datetime

class StockMarketFPM:
    def __init__(self, apikey="Sek7iGkE1GvNjfD4mxMrAIdJCu8tpeIh", dir_path="stock_data", forbid_fetch=False, exchange=None):
        self.apikey = apikey
        self.dir_path = dir_path
        self.base_url = f'https://financialmodelingprep.com/api/v3/'
        self.forbid_fetch = forbid_fetch

        ## Cache
        self._stock_list = None

    def fetch(self, data_type, **kwargs):
        """Generic method to fetch data based on the type specified."""
        if self.forbid_fetch:
            raise ValueError("Fetching data is forbidden!")
        
        url = f"{self.base_url}{data_type}/?apikey={self.apikey}"
        for key in kwargs:
            url += f"&{key}={kwargs[key]}"

        response = requests.get(url)
        data = pd.DataFrame(response.json())

        return data
    

    def stock_list(self):
        if self._stock_list is None:
            self._stock_list = self.fetch("/stock/list")
            self._stock_list = self._stock_list[self._stock_list["type"] == "stock"]
        return self._stock_list


    def save(self):
        # Create the directory for the symbol if it doesn't exist
        if not os.path.exists(self.dir_path):
            os.makedirs(self .dir_path)

        # Stock list 
        file_path = os.path.join(self.dir_path, "stock_listing.csv")
        self.stock_list().to_csv(file_path, index=False)


    def load(self):
        file_path = os.path.join(self.dir_path, "stock_listing.csv")
        if os.path.exists(file_path):
            self._stock_list = pd.read_csv(file_path)
            return True
        return False
    

    def evaluate_companies(self, stock_evaluator:StockEvaluator, output_name=None, companies=None, exchanges=None):  
        """ Iterates through a bunch of companies, evaluating them (which means calculating a bunch of properties
        that are useful, including a score).

        Args:
            stock_evaluator (StockEvaluator): Outputs a score and info about each stock
            output_name (string, optional): data frame name to be saved. Defaults to None.
            companies (dataframe, optional): dataframe with (symbol, name, exchange and exchangeShortName) to evaluate. Defaults to None.
            exchanges (list, optional): exchanges to consider. Defaults to None.

        Returns:
            dataframe with (symbol, name, exchange, exchangeShortName, score, *other metrics)
        """
        if output_name is None:
            today_date = datetime.now().strftime("%Y-%m-%d")
            output_name = f"{str(stock_evaluator)}_{today_date}.csv"
        
        if companies is None:
            companies = self.stock_list()

        if exchanges is not None:
            companies = companies[companies["exchangeShortName"].isin(exchanges)]
        companies = companies[["symbol","name","exchange","exchangeShortName"]]
        
        # Initialize an empty DataFrame for appending data
        company_evaluations = pd.DataFrame()
        for i in range(len(companies)):
            symbol, name, exchange, exchangeShortName = companies.iloc[i]

            stock = StockFPM(symbol)
            score, info = stock_evaluator.evaluate(stock)
            
            entry = {
                'symbol': symbol,
                'name': name,
                'exchange': exchange,
                'exchangeShortName':exchangeShortName,
                'score': score,
                **info
            }

            # Append the entry to the DataFrame
            company_evaluations = company_evaluations.append(entry, ignore_index=True)

            if company_evaluations.shape[0] % 5 == 0: # Regular saves
                # Save the DataFrame to a CSV file
                company_evaluations.to_csv(output_name, index=False)

        # Save the DataFrame to a CSV file
        company_evaluations.to_csv(output_name, index=False)
         
        return company_evaluations


