import pandas as pd
from app.helpers import ttm_value, is_valid_number


def calculate_pe_ratio(
    market_cap: float | None,
    net_income_ttm: float | None,
) -> float | None:
    """
    P/E is meaningful only when market cap and earnings are positive.
    """

    if not is_valid_number(market_cap):
        return None

    if not is_valid_number(net_income_ttm):
        return None

    if market_cap <= 0 or net_income_ttm <= 0:
        return None

    return float(market_cap / net_income_ttm)


def calculate_ps_ratio(
    market_cap: float | None,
    revenue_ttm: float | None,
) -> float | None:

    if not is_valid_number(market_cap):
        return None

    if not is_valid_number(revenue_ttm):
        return None

    if market_cap <= 0 or revenue_ttm <= 0:
        return None

    return float(market_cap / revenue_ttm)

def calculate_ev_to_ebitda(
    enterprise_value: float | None,
    ebitda_ttm: float | None,
) -> float | None:
    """
    Conventional EV/EBITDA is not meaningful with non-positive EBITDA.
    """

    if not is_valid_number(enterprise_value):
        return None

    if not is_valid_number(ebitda_ttm):
        return None

    if enterprise_value <= 0 or ebitda_ttm <= 0:
        return None

    return float(enterprise_value / ebitda_ttm)


def calculate_fcf_yield(
    free_cash_flow_ttm: float | None,
    market_cap: float | None,
) -> float | None:
    """
    Negative FCF yield is allowed because it carries useful information.
    Only the market-cap denominator must be positive.
    """

    if not is_valid_number(free_cash_flow_ttm):
        return None

    if not is_valid_number(market_cap):
        return None

    if market_cap <= 0:
        return None

    return float(free_cash_flow_ttm / market_cap)


#Valuation metrics from most recent year data
def calculate_valuation_metrics(
    company_info: dict,
    quarterly_income_statement: pd.DataFrame,
    quarterly_cash_flow: pd.DataFrame,
) -> dict:
    """
    Calculate current valuation multiples using TTM fundamentals.
    """

    market_cap = company_info.get("marketCap")

    net_income_ttm = ttm_value(
        quarterly_income_statement,
        "NetIncome",
    )

    revenue_ttm = ttm_value(
        quarterly_income_statement,
        "TotalRevenue",
    )

    free_cash_flow_ttm = ttm_value(
        quarterly_cash_flow,
        "FreeCashFlow",
    )

    ebitda_ttm = ttm_value(
        quarterly_income_statement,
        "EBITDA",
    )

    enterprise_value = company_info.get(
        "enterpriseValue"
    )

    ev_to_ebitda = calculate_ev_to_ebitda(
        enterprise_value=enterprise_value,
        ebitda_ttm=ebitda_ttm,
    )

    pe_ratio = calculate_pe_ratio(market_cap= market_cap, net_income_ttm= net_income_ttm)

    ps_ratio = calculate_ps_ratio(market_cap= market_cap, revenue_ttm= revenue_ttm)

    fcf_yield = calculate_fcf_yield(market_cap= market_cap, free_cash_flow_ttm= free_cash_flow_ttm)

    return {
        "pe_ratio": pe_ratio,
        "ps_ratio": ps_ratio,
        "ev_to_ebitda": ev_to_ebitda,
        "fcf_yield": fcf_yield,
        "net_income_ttm": net_income_ttm,
        "revenue_ttm": revenue_ttm,
        "free_cash_flow_ttm": free_cash_flow_ttm,
        "valuation_basis": "Current market value / TTM fundamentals",
    }