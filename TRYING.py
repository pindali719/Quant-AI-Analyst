import yfinance as yf
import pandas as pd

import app.analysis.metrics as metrics

ticker=yf.Ticker("NVDA")


fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", ""]

info = ticker.get_info()


if "debtToEquity" in info.keys():
    print("yes")
else:
    print("no")


