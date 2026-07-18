import yfinance as yf
import pandas as pd

from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.helpers import latest_value

ticker=yf.Ticker("NVDA")


fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", ""]

info = ticker.get_info()

print(info.get("debtToEquity"))

all_financial_data = fetch_all_financial_data("NVDA")
balance_sheet = all_financial_data.get("balance_sheet")
debt = latest_value(balance_sheet.loc["TotalDebt"])
stockholders_equity = latest_value(balance_sheet.loc["StockholdersEquity"])

debt_to_equity = debt/stockholders_equity

print(debt_to_equity)

sheet = ticker.get_balance_sheet()

#print(sheet.index)

"""if "TaxProvision" in info.keys():
    print("yes")
else:
    print("no")"""
