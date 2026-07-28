import yfinance as yf
import pandas as pd
from app.helpers import latest_value

def get_yfinance_frequency(period: str) -> str:
    """
    Convert the project's period name into a yfinance frequency.
    """

    frequencies = {
        "annual": "yearly",
        "quarterly": "quarterly",
    }

    if period not in frequencies:
        raise ValueError(
            "period must be either 'annual' or 'quarterly'."
        )

    return frequencies[period]

def fetch_income_statement(ticker: str, period: str = "annual") -> pd.DataFrame:

    ticker_symbol = yf.Ticker(ticker)
    frequency = get_yfinance_frequency(period= period)

    income_statement= ticker_symbol.get_income_stmt(freq=frequency)

    if income_statement.empty:
        raise ValueError(f"Yahoo Finance returned no {period} Income Statement data.")

    rows_to_keep = ["TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome", "PretaxIncome", "TaxProvision", "EBITDA", "DilutedAverageShares"]

    income_statement = income_statement.reindex(rows_to_keep)

    return income_statement

def fetch_balance_sheet(ticker: str, period: str = "annual") -> pd.DataFrame:

    ticker_symbol= yf.Ticker(ticker)
    frequency = get_yfinance_frequency(period= period)

    balance_sheet= (ticker_symbol.get_balance_sheet(freq= frequency))

    if balance_sheet.empty:
        raise ValueError("Yahoo Finance returned no balance-sheet data.")

    rows_to_keep = ["TotalAssets", "TotalLiabilitiesNetMinorityInterest", "StockholdersEquity", "TotalDebt", "CashAndCashEquivalents", "CurrentAssets", "CurrentLiabilities"]

    balance_sheet = balance_sheet.reindex(rows_to_keep)

    return balance_sheet

def fetch_cash_flow(ticker, period: str = "annual") -> pd.DataFrame:

    ticker_symbol= yf.Ticker(ticker)
    frequency = get_yfinance_frequency(period= period)

    cash_flow = ticker_symbol.get_cash_flow(freq=frequency)

    if cash_flow.empty:
        raise ValueError("Yahoo Finance returned no cash-flow data.")

    rows_to_keep = [
        "OperatingCashFlow",
        "CapitalExpenditure",
        "FreeCashFlow",
        "CashDividendsPaid",
        "RepurchaseOfCapitalStock",
    ]

    return cash_flow.reindex(rows_to_keep)


def fetch_historical_prices(ticker: str) -> pd.DataFrame:

    ticker_symbol= yf.Ticker(ticker)

    historical_data= (ticker_symbol.history(period="5y", interval="1d"))

    if historical_data.empty:
        raise ValueError("Yahoo Finance returned no historical data.")

    return historical_data

def fetch_company_info(ticker: str) -> dict:


    ticker_symbol= yf.Ticker(ticker)
    info = ticker_symbol.get_info()

    fields=["longBusinessSummary", "sector", "industry", "marketCap", "exchange", "currency", "financialCurrency",  "currentPrice", "enterpriseValue", "sharesOutstanding", "trailingPE", "sector", "sectorKey", "industry", "industryKey"]


    return {
        field: info.get(field)
        for field in fields
    }

def fetch_all_financial_data(ticker: str) -> dict:

    return {
        "company_info": fetch_company_info(ticker),

        # Annual data for historical trends and charts.
        "income_statement": fetch_income_statement(
            ticker,
            period="annual",
        ),
        "balance_sheet": fetch_balance_sheet(
            ticker,
            period="annual",
        ),
        "cash_flow": fetch_cash_flow(
            ticker,
            period="annual",
        ),

        # Quarterly data for current valuation.
        "quarterly_income_statement": fetch_income_statement(
            ticker,
            period="quarterly",
        ),
        "quarterly_balance_sheet": fetch_balance_sheet(
            ticker,
            period="quarterly",
        ),
        "quarterly_cash_flow": fetch_cash_flow(
            ticker,
            period="quarterly",
        ),

        "historical_prices": fetch_historical_prices(ticker),
    }