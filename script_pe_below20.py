import argparse
from stocklib import StockFPM, StockMarket_FPM
import pandas as pd


###! 

def find_stocks_with_good_pe(exchange, start_index, end_index=None, avg_years=5, max_pe=20, load_stocks=True, save_stocks=False, output_name=None):
    # Load stock market data
    stock_market = StockMarket_FPM()
    stock_market.load()
    stk_list = stock_market.stock_list()

    # Filter stock list based on the exchange
    stocks = stk_list[stk_list["exchangeShortName"] == exchange]

    # Find stocks within the specified range
    good_pe_stocks = []

    for i in range(start_index, end_index if end_index else len(stocks)):
        symbol, name, exchange = stocks.iloc[i][["symbol","name","exchange"]]
        stock = StockFPM(symbol)

        if load_stocks:
            stock.load()

        if save_stocks: 
            stock.save()

        income = stock.income_statement()
        mk_cap = stock.market_cap()

        # Ensure there are values to process
        if not income.empty and not mk_cap.empty:
            net_income_mean = income['netIncome'][0:avg_years].mean() 
            market_cap = mk_cap.iloc[0]["marketCap"]
            
            if net_income_mean != 0:
                pe = market_cap / net_income_mean
                if 0 < pe <= max_pe:
                    good_pe_stocks.append({
                        "symbol": symbol,
                        "name": name,
                        "exchange": exchange,
                        "PE": pe,
                        "marketCap": market_cap,
                        "netIncome": net_income_mean
                    })
                    print(f"{name} ({symbol})")
                    print(f"\tPE({len(income)}): {pe:.2f} ")


        # Convert list to DataFrame
    if good_pe_stocks:
        pe_stocks_df = pd.DataFrame(good_pe_stocks)
        print(pe_stocks_df)
        if output_name:  # Save to file if output name is provided
            pe_stocks_df.to_csv(output_name, index=False)
            print(f"DataFrame saved to {output_name}")
        return pe_stocks_df
    else:
        print("No stocks found with PE under specified limit.")
        return pd.DataFrame()
    

def main():

    # Setup argument parser
    parser = argparse.ArgumentParser(description="Calculate PE ratios for stocks.")
    
    parser.add_argument("",
                        type=str,
                        choices=['NYSE', 'NASDAQ', 'EURONEXT'],
                        default="NYSE",
                        help="The stock exchange to target.")

    parser.add_argument("--exchange",
                        type=str,
                        choices=['NYSE', 'NASDAQ', 'EURONEXT'],
                        default="NYSE",
                        help="The stock exchange to target.")
    
    parser.add_argument("--start",
                        type=int,
                        default=75,
                        help="Starting index for stock processing.")
    
    parser.add_argument("--end",
                        type=int,
                        help="Ending index for stock processing, if not set will go till the last.")
    
    parser.add_argument("--avg_years",
                        type=int,
                        default=5,
                        help="Years to average Earnings over")
    
    parser.add_argument("--max_pe",
                        type=int,
                        default=20,
                        help="Maximum PE")
    
    parser.add_argument("--load_stocks",
                        type=bool,
                        default=True,
                        help="Load stocks info")

    parser.add_argument("--save_stocks",
                        type=bool,
                        default=False,
                        help="Save stocks info")
        
    parser.add_argument("--output_name",
                        type=str,
                        help="Filename to save the DataFrame if it is not empty.")


    args = parser.parse_args()

    find_stocks_with_good_pe(args.exchange, 
                             args.start,
                             args.end, 
                             args.avg_years, 
                             args.max_pe, 
                             args.load_stocks, 
                             args.save_stocks, 
                             args.output_name)

if __name__ == "__main__":
    main()

