"""
Historical Simulation Script

Description:
This script is designed to run simulations on a set of stocks to evaluate potential investment returns
based on specified financial metrics and strategies.

The script utilizes parameters such as the P/E buy and sell thresholds, asset to liability ratios, and
minimum years in business to filter and analyze stocks. Users can configure these parameters through
command-line arguments to tailor the simulation according to different investment strategies or hypotheses.

Usage:
The script can be run from the command line with various options to specify the operational parameters.

Examples:
To simulate returns for 500 companies from NYSE and NASDAQ:
   python script_name.py --N 500 --end_year 2021 --minimum_years 5 --exchanges NYSE NASDAQ --pe_to_buy 10 --pe_to_sell 20 --asset_liability_ratio 2

Parameters:
--N (int): The number of companies to simulate (default is 1000).
--minimum_years (int): Minimum number of years a company has been in business (default is 10).
--exchanges (list of str): List of stock exchanges to include, e.g., NYSE, NASDAQ (default).
--pe_to_buy (float): The P/E ratio threshold to consider buying a stock (default is 10).
--pe_to_sell (float): The P/E ratio threshold to consider selling a stock (default is 20).
--asset_liability_ratio (float): Minimum asset to liability ratio required for a stock to be considered (default is 2).

Note:
At the moment, the simulations happen using the entire historical data available.

Author:
Tiago Oliveira
"""


from stocklib.simulator import Engine
from stocklib.stock import StockFPM, StockMarketFPM
from stocklib.strategy import *
import argparse
    
class CompanyCriteria:
    """ This class serves to verify if the selected company meets one which
    properties we are interested in.
    """
    def __init__(self, minimum_years, currencies = ["USD","EUR"]):
        self.minimum_years = minimum_years

    def check(self, stock):
        if not stock.is_open:
            stock.open()
        income = stock.income_statement()
        cash_flow = stock.cash_flow()
        if income.empty or cash_flow.empty:
            raise ValueError("Income or cash flow is empty")
        #!self._check_currency(stock)
        self._check_years(stock)
        
    def _check_currency(self, stock):
        currency = stock.income_statement().iloc[-1]["reportedCurrency"]
        if  currency not in ["USD"]:
            raise ValueError("CompanyCriteria::_check_currency: " + str(stock) + " is in currency " + currency)

    def _check_years(self, stock):
        years = len(stock.income_statement())
        if years < self.minimum_years:
            raise ValueError("CompanyCriteria::_check_years: it only has " + str(years) + " years")




def main(args):
    companies = StockMarketFPM().stock_list()
    companies = companies[companies["exchangeShortName"].isin(args.exchanges)]
    company_criteria = CompanyCriteria(args.minimum_years, currencies=["USD","EUR"])
    
    avg_returns = []
    while len(avg_returns) < args.N:
        try:
            company = companies.sample(n=1).iloc[0]
            stock = StockFPM(company["name"], company["symbol"])
            stock.open()
            company_criteria.check(stock)
            
            engine = Engine(LiabilitiesStrategy(years_to_average=args.years_to_avg,
                                                pe_to_buy=args.pe_to_buy,
                                                pe_to_sell=args.pe_to_sell,
                                                curr_al_ratio=args.curr_asset_liab_ratio,
                                                noncurr_al_ratio=args.noncurr_asset_liab_ratio), stock)
            simulation = engine.simulate()
                         
            if len(simulation.returns) > 0:
                avg_returns.append(simulation.returns["return"].mean())
            
            print("[Echange] " + company["exchange"])
            simulation.print(buy_metrics=["eps_"+str(args.years_to_avg),"curr-asset-liab-ratio", "asset-liab-ratio"],
                             sell_metrics=["eps_"+str(args.years_to_avg)])

        except Exception as e:
            print(e)
            #pass

    return avg_returns


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run stock simulations with configurable parameters.')
    parser.add_argument('--N', type=int, default=100, help='Number of companies to simulate')
    parser.add_argument('--minimum_years', type=int, default=10, help='Minimum number of years in business for a company')
    parser.add_argument('--exchanges', type=str, nargs='+', default=["NYSE", "NASDAQ"], help='List of stock exchanges to include')
    parser.add_argument('--years_to_avg', type=int, default=5, help='Years to average earnings')
    parser.add_argument('--pe_to_buy', type=float, default=10.0, help='P/E ratio threshold to buy')
    parser.add_argument('--pe_to_sell', type=float, default=20.0, help='P/E ratio threshold to sell')
    parser.add_argument('--curr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')
    parser.add_argument('--noncurr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')


    args = parser.parse_args()

    avg_returns = main(args)
    avg_return = sum(avg_returns) / len(avg_returns) if avg_returns else 0
    print(f"Average Return: {avg_return:.2f}%")

