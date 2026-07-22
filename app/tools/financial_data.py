import yfinance as yf
import pandas as pd
from app.helpers import latest_value

def fetch_income_statement(ticker: str) -> pd.DataFrame:

    ticker= yf.Ticker(ticker)

    income_statement= (ticker.get_income_stmt(freq="yearly")).loc[["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome", "PretaxIncome", "TaxProvision", "EBITDA"]]

    return income_statement

def fetch_balance_sheet(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker(tickets)

    balance_sheet= (ticker.get_balance_sheet(freq="yearly")).loc[["TotalAssets", "TotalLiabilitiesNetMinorityInterest", "StockholdersEquity", "TotalDebt", "CashAndCashEquivalents", "CurrentAssets", "CurrentLiabilities"]]

    return balance_sheet

def fetch_cash_flow(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker(tickets)

    cash_flow= (ticker.get_cash_flow(freq="yearly")).loc[["OperatingCashFlow", "CapitalExpenditure", "FreeCashFlow", "CashDividendsPaid", "RepurchaseOfCapitalStock"]]

    return cash_flow

def fetch_historical_prices(tickets: str) -> pd.DataFrame:

    ticker= yf.Ticker(tickets)

    historical_data= (ticker.history(period="5y", interval="1d"))

    return historical_data

def fetch_company_info(tickets: str) -> dict:


    ticker= yf.Ticker(tickets)

    fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", "currentPrice", "enterpriseValue", "sharesOutstanding", "trailingPE"]

    info = ticker.get_info()

    selected_info={}

    balance_sheet = fetch_balance_sheet(tickets= tickets)

    market_cap = info.get("marketCap")
    debt = latest_value(balance_sheet.loc["TotalDebt"])
    cash = latest_value(balance_sheet.loc["CashAndCashEquivalents"])

    #To get last financial year's enterprise_value, not the current. To keep consistency
    enterprise_value = (
    market_cap + debt - cash
    if None not in (market_cap, debt, cash)
    else None
    )

    for field in fields:
        selected_info[field] = info.get(field)

    selected_info["enterpriseValue"] = enterprise_value

    return selected_info

def fetch_all_financial_data(ticker: str) -> dict:
    company_info = fetch_company_info(ticker)
    income_statement = fetch_income_statement(ticker)
    balance_sheet = fetch_balance_sheet(ticker)
    cash_flow = fetch_cash_flow(ticker)
    historical_prices = fetch_historical_prices(ticker)

    return {
        "company_info": company_info,
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
        "historical_prices": historical_prices,
    }