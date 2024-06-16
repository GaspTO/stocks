from fredapi import Fred
import pandas as pd


"""https://fred.stlouisfed.org/categories/95"""

class CurrencyConverter:
    
    def __init__(self, apikey="eb72c70ce9cee8a56b5a4eb1c3d2ac9a"):
        self.fred = Fred(api_key=apikey)
        self.cache = {}

    def to_usd(self, currency, date):
        if currency == "USD":
            return 1
        elif currency == "EUR":
            return self.eur_to_usd(date)
        elif currency == "CHF":
            return self.chf_to_usd(date)
        elif currency == "JPY":
            return self.jpy_to_usd(date)
        elif currency == "AUD":
            return self.aud_to_us(date)
        elif currency == "CAD":
            return self.cad_to_usd(date)
        elif currency == "CNY":
            return self.cny_to_usd(date)
        elif currency == "MXN":
            return self.mxn_to_usd(date)
        elif currency == "GBP":
            return self.gbp_to_usd(date)
        elif currency == "TWD":
            return self.twd_to_usd(date)
        elif currency == "INR":
            return self.inr_to_usd(date)
        elif currency == "BRL":
            return self.brl_to_usd(date)
        elif currency == "KRW":
            return self.krw_to_usd(date)
        elif currency == "HKD":
            return self.hkw_to_usd(date)
        elif currency == "SEK":
            return self.sek_to_usd(date)
        elif currency == "THB":
            return self.thb_to_usd(date)
        else:
            raise ValueError(str(currency) + " conversion to USD not available")

    def eur_to_usd(self, date):
        return self._get_rate("DEXUSEU", date)
    
    def chf_to_usd(self, date):
        return 1/self._get_rate("EXSZUS", date)
        
    def jpy_to_usd(self, date):
        return 1/self._get_rate("DEXJPUS", date)

    def aud_to_us(self, date):
        return self._get_rate("DEXUSAL", date)

    def cny_to_usd(self, date):
        return 1/self._get_rate("DEXCHUS", date)

    def cad_to_usd(self, date):
        return 1/self._get_rate("DEXCAUS", date)

    def won_to_usd(self, date):
        return 1/self._get_rate("DEXKOUS", date)

    def mxn_to_usd(self, date):
        return 1/self._get_rate("DEXMXUS", date)

    def inr_to_usd(self, date):
        return 1/self._get_rate("DEXINUS", date)

    def gbp_to_usd(self, date):
        return self._get_rate("EXUSUK", date)

    def twd_to_usd(self, date):
        return 1/self._get_rate("EXTAUS", date)

    def brl_to_usd(self, date):
        return 1/self._get_rate("EXBZUS", date)
    
    def krw_to_usd(self, date):
        return 1/self._get_rate("EXKOUS", date)
    
    def hkw_to_usd(self, date):
        return 1/self._get_rate("EXHKUS", date)
    
    def sek_to_usd(self, date):
        return 1/self._get_rate("EXSDUS", date)
    
    def thb_to_usd(self, date):
        return 1/self._get_rate("EXTHUS", date)

    def _get_rate(self, series_name, date):
        if series_name not in self.cache:
            series = self.fred.get_series(series_name)
            series.dropna(inplace=True)
            self.cache[series_name] = series

        series = self.cache[series_name]
        i = series.index.get_indexer([date],method="nearest").item()
        rate = series.iloc[i]
        return rate
        
    


if __name__ == "__main__":
    from datetime import datetime
    # Example usage
    cc = CurrencyConverter()

    # Using today's date
    today = datetime.now()

    # Sample conversions using the current date
    print("KRW to USD:", cc.won_to_usd(today, 1000000))  # Example for 1,000,000 KRW
    print("JPY to USD:", cc.yen_to_usd(today, 10000))    # Example for 10,000 JPY
    print("CNY to USD:", cc.yuan_to_usd(today, 5000))    # Example for 5,000 CNY
    print("CAD to USD:", cc.cad_to_usd(today, 1200))     # Example for 1,200 CAD
    print("MXN to USD:", cc.peso_to_usd(today, 8000))    # Example for 8,000 MXN
    print("INR to USD:", cc.rupee_to_usd(today, 15000))  # Example for 15,000 INR
    print("EUR to USD:", cc.eur_to_usd(today, 500))      # Example for 500 EUR