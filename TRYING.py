import yfinance as yf
import pandas as pd

from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.helpers import latest_value

ticker=yf.Ticker("NVDA")


fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", ""]

info = ticker.get_income_stmt()


if "EBITDA" in info.index:
    print("yes")
else:
    print("no")
