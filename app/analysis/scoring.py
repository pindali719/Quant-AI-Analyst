
import pandas as pd

from app.tools.financial_data import fetch_all_financial_data
from app.helpers import latest_value, safe_division, is_missing
from app.constants import SCORING_WEIGHTS

def scoring(
    bounds: list[float],
    value: float | None,
    higher_better: bool = True,
) -> int:
    """
    Convert a metric into a score from 1 to 5.

    Missing data temporarily receives a neutral score of 3.
    """

    if value is None or pd.isna(value):
        return 3

    if higher_better:
        if value >= bounds[0]:
            return 5
        if value >= bounds[1]:
            return 4
        if value >= bounds[2]:
            return 3
        if value >= bounds[3]:
            return 2
        return 1

    if value <= bounds[0]:
        return 5
    if value <= bounds[1]:
        return 4
    if value <= bounds[2]:
        return 3
    if value <= bounds[3]:
        return 2

    return 1
        



def score_revenue_growth(metrics: pd.Series) -> int:

    revenue_growth = metrics.get("latest_fy_revenue_growth")

    bounds = [0.25, 0.15, 0.05, 0]

    score = scoring(bounds= bounds, value= revenue_growth)

    return score
    

def score_single_margin(metrics:pd.Series, margin_type: str) -> int:

    metric_names = {
        "gross_margin": "ttm_gross_margin",
        "operating_margin": "ttm_operating_margin",
        "net_margin": "ttm_net_margin",
    }

    bounds_by_margin = {
        "gross_margin": [0.60, 0.40, 0.25, 0.10],
        "operating_margin": [0.30, 0.20, 0.10, 0.00],
        "net_margin": [0.25, 0.15, 0.05, 0.00],
    }


    if margin_type not in metric_names:
        raise ValueError(f"Unsupported margin type: {margin_type}")

    #Get the key of the margin, to fetch it from metrics
    metric_name = metric_names[margin_type]
    margin = metrics.get(metric_name)

    
    bounds = bounds_by_margin.get(margin_type)

    score = scoring(bounds= bounds, value= margin)
    
    return score


def score_margin(metrics: pd.Series) -> float:

    gross_margin = score_single_margin(metrics= metrics, margin_type="gross_margin")
    operating_margin = score_single_margin(metrics = metrics, margin_type= "operating_margin")
    net_margin = score_single_margin(metrics= metrics, margin_type= "net_margin")

    score = gross_margin*0.3 + operating_margin*0.4 + net_margin*0.3
    score = round(score)

    return score


def score_ROE(metrics: pd.Series) -> int:

    roe = metrics.get("approx_ttm_roe")

    return scoring(
        bounds=[0.30, 0.20, 0.10, 0.00],
        value=roe,
    )


def score_ROIC(metrics: pd.Series) -> int:

    roic = metrics.get("approx_ttm_roic")

    return scoring(
        bounds=[0.20, 0.12, 0.08, 0.00],
        value=roic,
    )
    

def score_profitability(
    metrics: pd.Series,
) -> int:

    margin_score = score_margin(metrics)
    roe_score = score_ROE(metrics)
    roic_score = score_ROIC(metrics)

    final_score = (
        0.50 * margin_score
        + 0.30 * roic_score
        + 0.20 * roe_score
    )
  
    return round(final_score)



def score_leverage(
    metrics: pd.Series,
) -> int:

    cash = metrics.get("latest_q_cash")
    debt = metrics.get("latest_q_debt")
    equity = metrics.get("latest_q_equity")
    leverage = metrics.get("latest_q_leverage")

    # Strong net-cash position.
    if (
        cash is not None
        and debt is not None
        and not pd.isna(cash)
        and not pd.isna(debt)
        and cash > debt
    ):
        return 5

    # Debt-to-equity is not meaningful with negative equity.
    if (
        equity is not None
        and not pd.isna(equity)
        and equity < 0
    ):
        return 3

    return scoring(
        bounds=[0.30, 0.70, 1.50, 3.00],
        value=leverage,
        higher_better=False,
    )

def score_liquidity(
    metrics: pd.Series,
) -> int:

    current_ratio = metrics.get(
        "latest_q_current_ratio"
    )

    return scoring(
        bounds=[2.00, 1.50, 1.00, 0.70],
        value=current_ratio,
    )

def score_balance_sheet(metrics: pd.Series) -> int:

    leverage_score = score_leverage(metrics= metrics)
    liquidity_score = score_liquidity(metrics= metrics)

    balance_sheet_score =   0.6*leverage_score + 0.4*liquidity_score

    balance_sheet_score = round(balance_sheet_score)

    return balance_sheet_score



def score_multiples(
    target_ticker: str,
    all_metrics: pd.DataFrame,
) -> int:

    target = all_metrics.loc[target_ticker]
    peers = all_metrics.drop(index=target_ticker)

    multiple_columns = [
        "pe_ratio",
        "ps_ratio",
        "ev_to_ebitda",
    ]

    bounds = [0.75, 0.90, 1.10, 1.50]

    individual_scores = []

    for column in multiple_columns:
        target_value = target.get(column)

        #A pd.Series with only peers with a valid value
        valid_peer_values = pd.to_numeric(
            peers[column],
            errors="coerce",
        ).dropna()

        if is_missing(target_value):
            continue

        if valid_peer_values.empty:
            continue

        peer_median = valid_peer_values.median()

        if peer_median <= 0:
            continue

        relative_multiple = target_value / peer_median

        individual_scores.append(
            scoring(
                bounds=bounds,
                value=relative_multiple,
                higher_better=False,
            )
        )

    if not individual_scores:
        return 3

    return round(
        sum(individual_scores)
        / len(individual_scores)
    )


def score_fcf_yield(
    target_ticker: str,
    all_metrics: pd.DataFrame,
) -> int:

    target = all_metrics.loc[target_ticker]
    peers = all_metrics.drop(index=target_ticker)

    target_fcf_yield = target.get("fcf_yield")

    peer_fcf_yields = pd.to_numeric(
        peers["fcf_yield"],
        errors="coerce",
    ).dropna()

    if (
        is_missing(target_fcf_yield)
        or peer_fcf_yields.empty
    ):
        return 3

    peer_median_fcf_yield = peer_fcf_yields.median()

    if peer_median_fcf_yield <= 0:
        return 3

    relative_fcf_yield = (
        target_fcf_yield
        / peer_median_fcf_yield
    )

    return scoring(
        bounds=[1.50, 1.10, 0.90, 0.50],
        value=relative_fcf_yield,
    )

def score_dcf_upside(
    fair_value_per_share: float,
    current_price: float,
) -> int:

    if (
        is_missing(fair_value_per_share)
        or is_missing(current_price)
        or current_price <= 0
    ):
        return 3

    dcf_upside = (
        fair_value_per_share - current_price
    ) / current_price

    return scoring(
        bounds=[0.30, 0.10, -0.10, -0.30],
        value=dcf_upside,
    )

def score_valuation(target_ticker: str, all_metrics: pd.DataFrame, fair_value_per_share: float, current_price: float) -> int:

    
    multiples_score = score_multiples(target_ticker= target_ticker, all_metrics= all_metrics)
    fcf_yield_score = score_fcf_yield(target_ticker= target_ticker, all_metrics= all_metrics)
    dcf_upside_score = score_dcf_upside(fair_value_per_share= fair_value_per_share, current_price= current_price)

    score = 0.5* multiples_score + 0.3* fcf_yield_score + 0.2*dcf_upside_score


    return round(score) 

def score_risk(risks: dict) -> int:
    """
    Score risk from 1 to 5.

    Higher score = lower risk.
    Lower score = higher risk.
    """

    if risks is None:
        return 3  # neutral if risk analysis was not available

    risk_count = len(risks)

    bounds = [1, 3, 5, 7]

    score = scoring(bounds= bounds, value= risk_count, higher_better= False)

    return score

def calculate_overall_score(scores: dict) -> float:

    weights = SCORING_WEIGHTS

    final_score = 0 

    for category, weight in weights.items():

        category_score = scores.get(category) * weight
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
    
def generate_scorecard(risks: dict, target_ticker: str, all_metrics: pd.DataFrame, fair_value_per_share: float, current_price: float) -> dict:

    metrics = all_metrics.loc[target_ticker]

    growth_score = score_revenue_growth(metrics= metrics)
    profitability_score = score_profitability(metrics= metrics)
    balance_sheet_score = score_balance_sheet(metrics= metrics)
    valuation_score = score_valuation(target_ticker=target_ticker, all_metrics= all_metrics, fair_value_per_share= fair_value_per_share, current_price= current_price)
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
    


    