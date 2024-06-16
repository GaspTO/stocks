from stocklib.simulator import Engine
from stocklib.stock import StockFPM
from stocklib.strategy import *
import argparse
    

def main(args):
    stock = StockFPM(args.name, args.symbol)
    stock.open()
    engine = Engine(LiabilitiesStrategy(years_to_average=args.years_to_avg,
                                                pe_to_buy=args.pe_to_buy,
                                                pe_to_sell=args.pe_to_sell,
                                                curr_al_ratio=args.curr_asset_liab_ratio,
                                                noncurr_al_ratio=args.noncurr_asset_liab_ratio), stock)
    simulation = engine.simulate()  
    simulation.print(buy_metrics=["eps_"+str(args.years_to_avg),"curr-asset-liab-ratio", "asset-liab-ratio"],
                             sell_metrics=["eps_"+str(args.years_to_avg)])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a single stock with specified financial metrics.")
    parser.add_argument('symbol', type=str, help='The stock symbol of the company, e.g., AAPL')
    parser.add_argument('--name', type=str, default= "", help='Optional: The full name of the company')
    parser.add_argument('--years_to_avg', type=int, default=5, help='Years to average earnings')
    parser.add_argument('--pe_to_buy', type=float, default=10.0, help='P/E ratio threshold to buy')
    parser.add_argument('--pe_to_sell', type=float, default=20.0, help='P/E ratio threshold to sell')
    parser.add_argument('--curr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')
    parser.add_argument('--noncurr_asset_liab_ratio', type=float, default=1.0, help='Minimum asset to liability ratio')

    args = parser.parse_args()
    main(args)