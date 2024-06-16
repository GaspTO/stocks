
from stocklib.simulator import Engine
from stocklib.stock import StockFPM, StockMarketFPM
from stocklib.strategy import *
import argparse
from datetime import datetime
    
class CompanyCriteria:
    """ This class serves to verify if the selected company meets one which
    properties we are interested in.
    """
    def __init__(self, minimum_years, currencies = ["USD","EUR"]):
        self.currencies = currencies
        self.minimum_years = minimum_years

    def check(self, stock):
        if not stock.is_open:
            stock.open()
        income = stock.income_statement()
        cash_flow = stock.cash_flow()
        if income.empty or cash_flow.empty:
            raise ValueError("Income or cash flow is empty")
        self._check_currency(stock)
        self._check_years(stock)
        
    def _check_currency(self, stock):
        currency = stock.income_statement().iloc[-1]["reportedCurrency"]
        if  currency in self.currencies: #!
            raise ValueError("CompanyCriteria::_check_currency: " + str(stock) + " is in currency " + currency)

    def _check_years(self, stock):
        years = len(stock.income_statement())
        if not years >= self.minimum_years:
            raise ValueError("CompanyCriteria::_check_years: it only has " + str(years) + " years")




def main(args):
    companies = StockMarketFPM().stock_list()
    companies = companies[companies["exchangeShortName"].isin(args.exchanges)]
    company_criteria = CompanyCriteria(args.minimum_years, currencies=["USD"])
    

    strategy = LiabilitiesStrategy(years_to_average=args.years_to_avg,
                         pe_to_buy=args.pe_to_buy,
                         pe_to_sell=args.pe_to_buy + 5,
                         curr_al_ratio=args.curr_asset_liab_ratio,
                         noncurr_al_ratio=args.noncurr_asset_liab_ratio)

    for i in range(len(companies)):
        try:
            company = companies.iloc[i]
            #stock = StockFPM(company["name"], company["symbol"])
            stock = StockFPM("Nokia Oyj", "NOK")
            stock.open()
            company_criteria.check(stock)

            current_market_cap = stock.current_market_cap()
            current_income_statement = stock.income_statement().iloc[0]

            if (datetime.now() - current_income_statement["fillingDate"]).days > 365:
                raise ValueError("Last filling date is older than a year")
            
            if (datetime.now() - current_market_cap["date"].item()).days > 60:
                raise ValueError("Market cap date is older than 60 days")

           
            x = strategy.buy(current_income_statement["fiscalDateEnding"],current_market_cap["date"].item(),
                            current_market_cap["marketCap"].item(), stock)
            
            if x[0]:
                print(str(i) + "/" + str(len(companies)) + ": " + company["name"] + "(" + company["symbol"] + ")")
                for item, val in x[1].items():
                    print(str(item) + ": " + str(val[1]))
                print()
            else:
                print(str(i) + "/" + str(len(companies)) + ": failed")


        except Exception as e:
            print(str(i) + "/" + str(len(companies))  + ": " + str(e))
            #pass

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run stock simulations with configurable parameters.')
    #parser.add_argument('--N', type=int, default=100, help='Number of companies to simulate')
    parser.add_argument('--minimum_years', type=int, default=10, help='Minimum number of years in business for a company')
    parser.add_argument('--exchanges', type=str, nargs='+', default=["NYSE", "NASDAQ"], help='List of stock exchanges to include')
    parser.add_argument('--years_to_avg', type=int, default=5, help='Years to average earnings')
    parser.add_argument('--pe_to_buy', type=float, default=10.0, help='P/E ratio threshold to buy')
    parser.add_argument('--curr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')
    parser.add_argument('--noncurr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')


    args = parser.parse_args()

    avg_returns = main(args)
    avg_return = sum(avg_returns) / len(avg_returns) if avg_returns else 0
    print(f"Average Return: {avg_return:.2f}%")

