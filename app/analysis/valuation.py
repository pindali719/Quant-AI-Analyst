import pandas as pd
from app.helpers import ttm_value


def calculate_pe_ratio(market_cap: float, net_income_ttm: float) -> float:

    if market_cap is not None and net_income_ttm is not None and net_income_ttm > 0:

        return market_cap / net_income_ttm
    else:
        return None


def calculate_price_to_sales(market_cap: float, revenue_ttm: float) -> float:

    if market_cap is not None and revenue_ttm is not None and revenue_ttm > 0:

        return market_cap/revenue_ttm
    else:
        return None


def calculate_fcf_yield(market_cap: float, free_cash_flow_ttm: float) -> float:
        
    if market_cap is not None and market_cap > 0 and free_cash_flow_ttm is not None:

        return free_cash_flow_ttm / market_cap
    else:
        return None


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

    pe_ratio = calculate_pe_ratio(market_cap= market_cap, net_income_ttm= net_income_ttm)

    price_to_sales = calculate_price_to_sales(market_cap= market_cap, revenue_ttm= revenue_ttm)

    fcf_yield = calculate_fcf_yield(market_cap= market_cap, free_cash_flow_ttm= free_cash_flow_ttm)

    return {
        "pe_ratio": pe_ratio,
        "price_to_sales": price_to_sales,
        "fcf_yield": fcf_yield,
        "net_income_ttm": net_income_ttm,
        "revenue_ttm": revenue_ttm,
        "free_cash_flow_ttm": free_cash_flow_ttm,
        "valuation_basis": "Current market value / TTM fundamentals",
    }