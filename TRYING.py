import yfinance as yf
import pandas as pd

import app.analysis.metrics as metrics

ticker=yf.Ticker("NVDA")


income_statement= (ticker.get_income_stmt(freq="yearly")).loc[["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome"]]


print(income_statement)
