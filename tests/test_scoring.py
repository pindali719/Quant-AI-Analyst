import pandas as pd
import pytest

import app.analysis.scoring as scoring_module

from app.analysis.scoring import (
    calculate_overall_score,
    map_score_to_recommendation,
    score_balance_sheet,
    score_fcf_yield,
    score_leverage,
    score_liquidity,
    score_margin,
    score_multiples,
    score_revenue_growth,
    score_risk,
    score_single_margin,
    scoring,
)


def generate_target_metrics():

    """Generates an example metrics Series for one target company."""

    metrics = pd.Series(
        {
            "ticker": "NVDA",
            "revenue_growth": 0.18,
            "gross_margin": 0.65,
            "operating_margin": 0.25,
            "net_margin": 0.10,
            "leverage": 0.50,
        }
    )

    return metrics


def generate_peer_metrics():

    """Generates an example DataFrame containing a target and its peers."""

    all_metrics = pd.DataFrame(
        {
            "pe_ratio": [20.0, 25.0, 30.0],
            "ps_ratio": [5.0, 6.0, 8.0],
            "ev_to_ebitda": [12.0, 15.0, 18.0],
            "fcf_yield": [0.06, 0.04, 0.04],
        },
        index=["NVDA", "AMD", "INTC"],
    )

    return all_metrics


def generate_financial_data(
    cash=50.0,
    debt=100.0,
    equity=200.0,
    current_assets=150.0,
    current_liabilities=100.0,
):

    """Generates example annual financial statement data."""

    date = pd.Timestamp("2025-12-31")

    balance_sheet = pd.DataFrame(
        {
            date: {
                "CashAndCashEquivalents": cash,
                "TotalDebt": debt,
                "StockholdersEquity": equity,
                "CurrentAssets": current_assets,
                "CurrentLiabilities": current_liabilities,
            }
        }
    )

    income_statement = pd.DataFrame(
        {
            date: {
                "NetIncome": 60.0,
                "OperatingIncome": 100.0,
                "TaxProvision": 20.0,
                "PretaxIncome": 100.0,
            }
        }
    )

    result = {
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
    }

    return result


def test_scoring_higher_better_returns_correct_score():

    score = scoring(
        bounds=[0.25, 0.15, 0.05, 0.00],
        value=0.18,
        higher_better=True,
    )

    assert score == 4


def test_scoring_lower_better_returns_correct_score():

    score = scoring(
        bounds=[0.30, 0.70, 1.50, 3.00],
        value=0.50,
        higher_better=False,
    )

    assert score == 4


def test_scoring_returns_five_at_highest_boundary():

    score = scoring(
        bounds=[0.25, 0.15, 0.05, 0.00],
        value=0.25,
    )

    assert score == 5


def test_scoring_returns_one_below_lowest_boundary():

    score = scoring(
        bounds=[0.25, 0.15, 0.05, 0.00],
        value=-0.05,
    )

    assert score == 1


def test_score_revenue_growth():

    metrics = generate_target_metrics()

    score = score_revenue_growth(metrics)

    assert score == 4


def test_score_single_gross_margin():

    metrics = generate_target_metrics()

    score = score_single_margin(
        metrics=metrics,
        margin_type="gross_margin",
    )

    assert score == 5


def test_score_single_operating_margin():

    metrics = generate_target_metrics()

    score = score_single_margin(
        metrics=metrics,
        margin_type="operating_margin",
    )

    assert score == 4


def test_score_single_net_margin():

    metrics = generate_target_metrics()

    score = score_single_margin(
        metrics=metrics,
        margin_type="net_margin",
    )

    assert score == 3


def test_score_single_margin_raises_error_for_invalid_margin():

    metrics = generate_target_metrics()

    with pytest.raises(ValueError):
        score_single_margin(
            metrics=metrics,
            margin_type="invalid_margin",
        )


def test_score_margin_calculates_weighted_score():

    metrics = generate_target_metrics()

    score = score_margin(metrics)

    # Gross = 5, operating = 4, net = 3
    # 5 * 0.3 + 4 * 0.4 + 3 * 0.3 = 4
    assert score == 4


def test_score_leverage_returns_five_when_company_has_net_cash(monkeypatch):

    financial_data = generate_financial_data(
        cash=150.0,
        debt=100.0,
    )

    monkeypatch.setattr(
        scoring_module,
        "fetch_all_financial_data",
        lambda ticker: financial_data,
    )

    metrics = generate_target_metrics()

    score = score_leverage(metrics)

    assert score == 5


def test_score_leverage_returns_three_when_equity_is_negative(monkeypatch):

    financial_data = generate_financial_data(
        cash=50.0,
        debt=100.0,
        equity=-20.0,
    )

    monkeypatch.setattr(
        scoring_module,
        "fetch_all_financial_data",
        lambda ticker: financial_data,
    )

    metrics = generate_target_metrics()

    score = score_leverage(metrics)

    assert score == 3


def test_score_leverage_normal_case(monkeypatch):

    financial_data = generate_financial_data(
        cash=50.0,
        debt=100.0,
        equity=200.0,
    )

    monkeypatch.setattr(
        scoring_module,
        "fetch_all_financial_data",
        lambda ticker: financial_data,
    )

    metrics = generate_target_metrics()

    score = score_leverage(metrics)

    assert score == 4


def test_score_liquidity(monkeypatch):

    financial_data = generate_financial_data(
        current_assets=150.0,
        current_liabilities=100.0,
    )

    monkeypatch.setattr(
        scoring_module,
        "fetch_all_financial_data",
        lambda ticker: financial_data,
    )

    metrics = generate_target_metrics()

    score = score_liquidity(metrics)

    assert score == 4


def test_score_balance_sheet(monkeypatch):

    monkeypatch.setattr(
        scoring_module,
        "score_leverage",
        lambda metrics: 5,
    )

    monkeypatch.setattr(
        scoring_module,
        "score_liquidity",
        lambda metrics: 3,
    )

    metrics = generate_target_metrics()

    score = score_balance_sheet(metrics)

    # 5 * 0.6 + 3 * 0.4 = 4.2
    assert score == 4


def test_score_multiples():

    all_metrics = generate_peer_metrics()

    score = score_multiples(
        target_ticker="NVDA",
        all_metrics=all_metrics,
    )

    # NVDA is cheaper than the median peer valuation.
    assert score == 5


def test_score_fcf_yield():

    all_metrics = generate_peer_metrics()

    score = score_fcf_yield(
        target_ticker="NVDA",
        all_metrics=all_metrics,
    )

    # NVDA FCF yield is 1.5 times the peer median.
    assert score == 5


def test_score_risk_returns_neutral_when_risks_are_missing():

    score = score_risk(None)

    assert score == 3


def test_score_risk_returns_five_for_one_risk():

    risks = {
        "competition": "The company faces strong competition.",
    }

    score = score_risk(risks)

    assert score == 5


def test_score_risk_returns_one_for_many_risks():

    risks = {
        "risk_1": "Example",
        "risk_2": "Example",
        "risk_3": "Example",
        "risk_4": "Example",
        "risk_5": "Example",
        "risk_6": "Example",
        "risk_7": "Example",
        "risk_8": "Example",
    }

    score = score_risk(risks)

    assert score == 1


def test_calculate_overall_score(monkeypatch):

    weights = {
        "growth": 0.30,
        "profitability": 0.25,
        "balance_sheet": 0.15,
        "valuation": 0.20,
        "risk": 0.10,
    }

    monkeypatch.setattr(
        scoring_module,
        "SCORING_WEIGHTS",
        weights,
    )

    scores = {
        "growth": 5,
        "profitability": 4,
        "balance_sheet": 3,
        "valuation": 2,
        "risk": 1,
    }

    overall_score = calculate_overall_score(scores)

    assert overall_score == 3.45


def test_map_score_to_recommendation_returns_buy():

    recommendation = map_score_to_recommendation(4.2)

    assert recommendation == "Buy"


def test_map_score_to_recommendation_returns_selective_buy():

    recommendation = map_score_to_recommendation(3.5)

    assert recommendation == "Selective Buy"


def test_map_score_to_recommendation_returns_hold():

    recommendation = map_score_to_recommendation(2.8)

    assert recommendation == "Hold"


def test_map_score_to_recommendation_returns_weak_hold():

    recommendation = map_score_to_recommendation(2.0)

    assert recommendation == "Weak Hold / Watchlist"


def test_map_score_to_recommendation_returns_avoid():

    recommendation = map_score_to_recommendation(1.5)

    assert recommendation == "Avoid"
