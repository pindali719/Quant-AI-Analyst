import yfinance as yf
import pandas as pd

import app.analysis.metrics as metrics

ticker=yf.Ticker("NVDA")


fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", ""]

info = ticker.get_info()




print(info.keys())



