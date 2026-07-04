import yfinance as yf
import pandas as pd

def fetch_income_statement(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker("tickets")

    income_statement= (ticker.get_income_stmt(freq="yearly")).loc[["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome"]]

    return income_statement

def fetch_balance_sheet(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker("tickets")

    balance_sheet= (ticker.get_balance_sheet(freq="yearly")).loc[["TotalAssets", "TotalLiabilitiesNetMinorityInterest", "StockholdersEquity", "TotalDebt", "CashAndCashEquivalents", "CurrentAssets", "CurrentLiabilities"]]

    return balance_sheet

def fetch_cash_flow(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker("tickets")

    cash_flow= (ticker.get_cash_flow(freq="yearly")).loc[["OperatingCashFlow", "CapitalExpenditure", "FreeCashFlow", "CashDividendsPaid", "RepurchaseOfCapitalStock"]]

    return cash_flow

def fetch_historical_prices(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker("tickets")

    historical_data= (ticker.historical(period="5y", interval="1d"))

    return historical_data

def fetch_company_info(tickets: str) -> dict:

    ticker= yf.Ticker("tickets")

    fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency"]


    selected_info={}

    for field in fields:
        selected_info[field] = ticker.get_info()[field]

    return selected_info