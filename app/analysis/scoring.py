
import pandas as pd

from app.tools.financial_data import fetch_all_financial_data
from constants import NONE_INPUT
from helpers import latest_value


def scoring(bounds: list[float], value: float, higher_better = True) -> int:

    if higher_better == True:
        if value >= bounds[0]:
            return 5
        if value >= bounds[1]:
            return 4
        if value >= bounds[2]:
            return 3
        if value >= bounds[3]:
            return 2
        if value < bounds[3]:
            return 1
    else:
        if value <= bounds[0]:
            return 5
        if value <= bounds[1]:
            return 4
        if value <= bounds[2]:
            return 3
        if value <= bounds[3]:
            return 2
        if value > bounds[3]:
            return 1
        



def score_revenue_growth(metrics: dict) -> int:

    revenue_growth = metrics.get("revenue_growth")

    bounds = [0.25, 0.15, 0.05, 0]

    score = scoring(bounds= bounds, value= revenue_growth)

    return score
    

def score_single_margin(metrics:dict, type: str) -> int:

    margin = metrics.get(type)

    if type == "gross_margin":

        bounds = [0.6, 0.4, 0.25, 0.10]

    elif type == "operating_margin":

        bounds = [0.3, 0.2, 0.1, 0.0]
    
    elif type == "net_margin":

        bounds = [0.25, 0.15, 0.05, 0.0]

    score = scoring(bounds= bounds, value= margin)
    
    return score


def score_margin(metrics: dict) -> float:

    gross_margin = score_single_margin(metrics= metrics, type="gross_margin")
    operating_margin = score_single_margin(metrics = metrics, type= "operating_margin")
    net_margin = score_single_margin(metrics= metrics, type= "net_margin")

    score = gross_margin*0.3 + operating_margin*0.4 + net_margin*0.3
    score = round(score)

    return score

def get_ROE(ticker: str) -> float:


    all_financial_data = fetch_all_financial_data(tickets= ticker)

    balance_sheet = all_financial_data.get("balance_sheet")

    stockholder_equity = latest_value(balance_sheet.get("StockholdersEquity"))

    if stockholder_equity < 0:

        #Neutral value, since negative Stock-holder Equity can be missleading
        return 3

    income_statement = all_financial_data.get("income_statement")

    net_income = latest_value(income_statement.get("NetIncome"))

    roe = net_income/stockholder_equity

    return roe

def score_ROE(metrics: dict) -> int:

    ticker = metrics.get("ticker")

    roe = get_ROE(ticker= ticker)

    bounds = [0.3, 0.2, 0.1, 0]

    score = scoring(bounds= bounds, value= roe)

    return score

def get_ROIC(ticker: str) -> float:

    
    all_financial_data = fetch_all_financial_data(ticker= ticker)

    income_statement = all_financial_data("income_statement")
    balance_sheet = all_financial_data("balance_sheet")

    #Computing NOPAT
    operating_income = latest_value(income_statement("OperatingIncome"))
    tax_provision = latest_value(income_statement("TaxProvision"))
    pretax_income = latest_value(income_statement("PretaxIncome"))

    effective_tax_rate = tax_provision/pretax_income
    
    nopat = operating_income * (1-effective_tax_rate)

    #Computing Invested Capital

    stockholder_equity = latest_value(balance_sheet.get("StockholdersEquity"))
    debt = latest_value(balance_sheet.get("TotalDebt"))
    cash = latest_value(balance_sheet("CashAndCashEquivalents"))

    invested_capital = stockholder_equity + debt - cash

    roic = nopat/invested_capital

    return roic


def score_ROIC(metrics: dict) -> int:

    ticker = metrics.get("ticker")

    roic = get_ROIC(ticker= ticker)

    bounds = [0.20, 0.12, 0.08, 0.0]

    score = scoring(bounds= bounds, value= roic)

    return score
    

def score_profitability(metrics: dict) -> int:

    margin_score = score_margin(metrics= metrics)

    roe_score = score_ROE(metrics= metrics)

    roic_score = score_ROIC(metrics= metrics)

    final_score = 0.5 * margin_score + 0.3 * roic_score + 0.2* roe_score

    final_score = round(final_score)

    return final_score



def score_leverage(metrics: dict) -> int:
    
    #Edge case: if net cash is greater than debt
    ticker = metrics.get(ticker)

    all_financial_data = fetch_all_financial_data(ticker= ticker)

    balance_sheet = all_financial_data.get("balance_sheet")

    cash = latest_value(balance_sheet.loc["CashAndCashEquivalents"])
    debt = latest_value(balance_sheet.loc["TotalDebt"])

    if cash > debt:
        return 5
    #Edge case: if Stockholder's equity is negative. It can be missleading, so return 3 (neutral)

    stockholders_equity = latest_value(balance_sheet.loc["StockholdersEquity"])

    if stockholders_equity < 0:
        return 3

    #Other cases

    leverage = metrics.get("leverage")

    bounds = [0.3, 0.7, 1.5, 3.0]

    score = scoring(bounds= bounds, value= leverage, higher_better = False)

    return score

def score_liquidity(metrics: dict) -> int:

    ticker = metrics.get("ticker")

    all_financial_data = fetch_all_financial_data(ticker= ticker)

    balance_sheet = all_financial_data.get("balance_sheet")

    current_assets=latest_value(balance_sheet.loc["CurrentAssets"])
    current_liabilities = latest_value(balance_sheet.loc["CurrentLiabilities"])

    current_ratio = current_assets/current_liabilities

    bounds = [2.0, 1.5, 1.0, 0.7]

    score = scoring(bounds= bounds, value= current_ratio)

    return score

def score_balance_sheet(metrics: dict) -> int:

    leverage_score = score_leverage(metrics= metrics)
    liquidity_score = score_liquidity(metrics= metrics)

    balance_sheet_score =   0.6*leverage_score + 0.4*liquidity_score

    balance_sheet_score = round(balance_sheet_score)

    return balance_sheet_score


