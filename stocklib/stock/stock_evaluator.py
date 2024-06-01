from .stock_api import Stock
from typing import Tuple, Dict

class StockEvaluator:
    def evaluate(self, stock:Stock) -> Tuple[int, Dict]:
        """ returns (score, info).
        score is a float between 0 and 1, or nan if 
        it couldn't be evaluated """
        raise NotImplementedError
    


class PEEvaluator:
    def __init__(self, num_of_years=1):
        self.num_of_years = num_of_years

    def evaluate(self, stock):
        key = "PE" + str(self.num_of_years) + "y"
        try:
            last_net_incomes = stock.income_statement().head(self.num_of_years)["netIncome"]
            market_cap = stock.market_cap().iloc[0]["marketCap"]
            
            if last_net_incomes.shape[0] != self.num_of_years:
                return float("nan"), {key:"None"}
            else:
                pe = market_cap / last_net_incomes.mean()
                return 20/(pe + 20), {key:pe}
        except:
            return float("nan"), {key:"None"}

    def __str__(self):
        return "PE"+str(self.num_of_years)+"y_evaluation"