""" TODO """

# IDEA
- Stock returns the reports as dataframes, which it makes sense someone does
but, for the most part, what we want is a specific metric per time, such as calling a function
stock.operating_margin() and receive a pair (time, operating_margin).

Maybe stock should return the report and the have the stock analysis return the simplified
values. The stock analysis should also return other rations like P/E and moving averages.
Maybe we can have a stock analysis and an advanced stock analysis which is just a subclass
that can calculate metrics and ratios

Lastly, we should have a visualizer, which takes a stock analysis and displays graphs


# FUTURE IDEA
We can then try to have some predictive models for stocks. Although I haven't thought much about this.
Should this be a model for all stocks, for specific markets, for specific companies?
I am not interested in complicated models for short term trading, I'm just interested in capturing a couple metrics 
for assessing financial health.
Ahhh, if this is the case, I want either the market or the entire stock market. I want a model
that tells me whether a company, given its financials is likely to succeed. This is just to help select companies
that are financially good, to then evaluate them more specifically.


""" How well does 5 years p/e predict the next ones? """

# predict the next

# predict two years from now

# predict three years from now

# predict four years from now

# predict five years from now

# predict the average of the next five years



""" How much last year metrics predict the next ones? """

# p/e
# operating margin
# current_assets/current_liabilities
# quick assets / current_liabilities
# assets/liabilities
# cashflow/marketcap
# cashflow/revenue
