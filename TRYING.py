import yfinance as yf
import pandas as pd

import app.analysis.metrics as metrics

ticker=yf.Ticker("MSFT")


income_statement= (ticker.get_income_stmt(freq="yearly")).loc[["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome"]]



revenue=income_statement.loc["TotalRevenue"]

revenue=revenue.sort_index()

#revenue_growths=revenue.pct_change()*100

print(revenue)
print("\n")
print(revenue.iloc[0])

