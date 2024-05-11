import requests
import pandas as pd
import os


class StockMarket_FPM:
    def __init__(self, apikey="Sek7iGkE1GvNjfD4mxMrAIdJCu8tpeIh", dir_path="stock_data", forbid_fetch=False):
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
            os.makedirs(self.dir_path)

        # Stock list 
        file_path = os.path.join(self.dir_path, "stock_listing.csv")
        self.stock_list().to_csv(file_path, index=False)


    def load(self):
        file_path = os.path.join(self.dir_path, "stock_listing.csv")
        if os.path.exists(file_path):
            self._stock_list = pd.read_csv(file_path)
            return True
        return False


if __name__ == "__main__":
    market = StockMarket_FPM()
    lista = market.stock_list()
    market.save()
    print("hey")