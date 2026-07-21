
import pandas as pd

from app.tools.financial_data import fetch_all_financial_data
from constants import NONE_INPUT
from helpers import latest_value
from app.analysis.dcf import calculate_fair_value_per_share
from app.analysis.dcf import calculate_equity_value
from constants import SCORING_WEIGHTS

def scoring(bounds: list[float], value: float, higher_better = True) -> int:

    """set bounds, and depending on whether higher values is better or not, give a score between 1 and 5"""

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
        



def score_revenue_growth(metrics: pd.Series) -> int:

    revenue_growth = metrics.get("revenue_growth")

    bounds = [0.25, 0.15, 0.05, 0]

    score = scoring(bounds= bounds, value= revenue_growth)

    return score
    

def score_single_margin(metrics:pd.Series, type: str) -> int:

    margin = metrics.get(type)

    if type == "gross_margin":

        bounds = [0.6, 0.4, 0.25, 0.10]

    elif type == "operating_margin":

        bounds = [0.3, 0.2, 0.1, 0.0]
    
    elif type == "net_margin":

        bounds = [0.25, 0.15, 0.05, 0.0]

    score = scoring(bounds= bounds, value= margin)
    
    return score


def score_margin(metrics: pd.Series) -> float:

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

def score_ROE(metrics: pd.Series) -> int:

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


def score_ROIC(metrics: pd.Series) -> int:

    ticker = metrics.get("ticker")

    roic = get_ROIC(ticker= ticker)

    bounds = [0.20, 0.12, 0.08, 0.0]

    score = scoring(bounds= bounds, value= roic)

    return score
    

def score_profitability(metrics: pd.Series) -> int:

    margin_score = score_margin(metrics= metrics)

    roe_score = score_ROE(metrics= metrics)

    roic_score = score_ROIC(metrics= metrics)

    final_score = 0.5 * margin_score + 0.3 * roic_score + 0.2* roe_score

    final_score = round(final_score)

    return final_score



def score_leverage(metrics: pd.Series) -> int:
    
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

    bounds = [3.0, 1.5, 0.7, 0.3]

    score = scoring(bounds= bounds, value= leverage, higher_better = False)

    return score

def score_liquidity(metrics: pd.Series) -> int:

    ticker = metrics.get("ticker")

    all_financial_data = fetch_all_financial_data(ticker= ticker)

    balance_sheet = all_financial_data.get("balance_sheet")

    current_assets=latest_value(balance_sheet.loc["CurrentAssets"])
    current_liabilities = latest_value(balance_sheet.loc["CurrentLiabilities"])

    current_ratio = current_assets/current_liabilities

    bounds = [2.0, 1.5, 1.0, 0.7]

    score = scoring(bounds= bounds, value= current_ratio)

    return score

def score_balance_sheet(metrics: pd.Series) -> int:

    leverage_score = score_leverage(metrics= metrics)
    liquidity_score = score_liquidity(metrics= metrics)

    balance_sheet_score =   0.6*leverage_score + 0.4*liquidity_score

    balance_sheet_score = round(balance_sheet_score)

    return balance_sheet_score



def score_multiples(target_ticker: str, all_metrics: pd.DataFrame) -> int:

    target = all_metrics.loc[target_ticker]

    peers = all_metrics.drop(index= target_ticker)

    target_pe_ratio = target["pe_ratio"]
    target_ps_ratio = target["ps_ratio"]
    target_ev_to_ebitda = target["ev_to_ebitda"]

    peer_median_pe_ratio = peers["pe_ratio"].median()
    peer_median_ps_ratio = peers["ps_ratio"].median()
    peer_median_ev_to_ebitda = peers["ev_to_ebitda"].median()

    relative_pe_ratio = target_pe_ratio/peer_median_pe_ratio
    relative_ps_ratio = target_ps_ratio/peer_median_ps_ratio
    relative_ev_to_ebitda = target_ev_to_ebitda / peer_median_ev_to_ebitda

    bounds = [1.50, 1.10, 0.90, 0.75]

    score_relative_pe_ratio = scoring(bounds= bounds, value= relative_pe_ratio, higher_better= False)
    score_relative_ps_ratio = scoring(bounds= bounds, value= relative_ps_ratio, higher_better= False)
    score_relative_ev_to_ebitda = scoring(bounds= bounds, value= relative_ev_to_ebitda, higher_better= False)

    average_score = (score_relative_pe_ratio + score_relative_ps_ratio + score_relative_ev_to_ebitda)/3

    multiples_score = round(average_score)

    return multiples_score


def score_fcf_yield(target_ticker: str, all_metrics: pd.DataFrame) -> int:

    target = all_metrics.loc[target_ticker]

    peers = all_metrics.drop(index= target_ticker)

    target_fcf_yield = target["fcf_yield"]
    peer_median_fcf_yield = peers["fcf_yield"].median()
    
    relative_fcf_yield = target_fcf_yield/peer_median_fcf_yield

    bounds = [1.50, 1.10, 0.90, 0.50]

    score = scoring(bounds= bounds, value= relative_fcf_yield)

    return score

def score_dcf_upside(metrics: pd.Series) -> int:

    ticker = metrics.get(ticker)

    all_financial_data = fetch_all_financial_data(ticker= ticker)
    company_info = all_financial_data.get("company_info")
    balance_sheet = all_financial_data.get("balance_sheet")

    enterprise_value = company_info.get("enterprise_value")
    shares_outstanding = company_info.get("shares_outstanding")
    current_price = company_info.get("currentPrice")
    cash = latest_value(balance_sheet.loc["CashAndCashEquivalents"])
    debt = latest_value(balance_sheet.loc["TotalDebt"])

    equity_value = calculate_equity_value(enterprise_value= enterprise_value, cash= cash, debt= debt)

    fair_value_per_share = calculate_fair_value_per_share(equity_value= equity_value, shares_outstanding= shares_outstanding)

    dcf_upside = (fair_value_per_share - current_price) / current_price

    bounds = [0.30, 0.10, -0.10, -0.30]

    score = scoring(bounds= bounds, value= dcf_upside)

    return score

def score_valuation(target_ticker: str, all_metrics: pd.DataFrame) -> int:
    
    multiples_score = score_multiples(target_ticker= target_ticker, all_metrics= all_metrics)
    fcf_yield_score = score_fcf_yield(target_ticker= target_ticker, all_metrics= all_metrics)
    dcf_upside_score = score_dcf_upside(metrics= all_metrics)

    score = 0.5* multiples_score + 0.3* fcf_yield_score + 0.2*dcf_upside_score

    return score

def score_risk(risks: dict) -> int:
    """
    Score risk from 1 to 5.

    Higher score = lower risk.
    Lower score = higher risk.
    """

    if risks is None:
        return 3  # neutral if risk analysis was not available

    risk_count = len(risks)

    bounds = [7, 5, 3, 1]

    score = scoring(bounds= bounds, value= risk_count, higher_better= False)

    return score

def calculate_overall_score(scores: dict) -> float:

    weights = SCORING_WEIGHTS
    

    final_score = 0 

    for category, weight in weights:

        category_score = scores.get(category) * weight(category)
        final_score+=category_score

    final_score = round(final_score, 2)

    return final_score
    
def map_score_to_recommendation(score: float) -> str:

    """
    Map the final weighted score to an investment recommendation.

    Score range:
    5 = strongest
    1 = weakest
    """

    if score >= 4.2:
        return "Buy"
    if score >= 3.5:
        return "Selective Buy"
    if score >= 2.8:
        return "Hold"
    if score >= 2.0:
        return "Weak Hold / Watchlist"
    if score <2.0:
        return "Avoid"
    
def generate_scorecard(risks: dict, target_ticker: str, all_metrics: pd.DataFrame) -> dict:

    metrics = all_metrics

    growth_score = score_revenue_growth(metrics= metrics)
    profitability_score = score_profitability(metrics= metrics)
    balance_sheet_score = score_balance_sheet(metrics= metrics)
    valuation_score = score_valuation(target_ticker=target_ticker, all_metrics= all_metrics)
    risk_score = score_risk(risks=risks)

    scores={
        "growth": growth_score,
        "profitability": profitability_score,
        "balance_sheet": balance_sheet_score,
        "valuation": valuation_score,
        "risk": risk_score
    }

    overall_score = calculate_overall_score(scores= scores)

    recommendation = map_score_to_recommendation(overall_score)

    weights = SCORING_WEIGHTS

    return {
        "scores": scores,
        "overall_score": overall_score,
        "recommendation": recommendation,
        "weights": weights
    }
    


    