import pandas as pd


def calculate_pe_ratio(market_cap: float, net_income: float) -> float:

    pe_ratio=market_cap/net_income

    return pe_ratio

def calculate_price_to_sales(market_cap: float, revenue: float) -> float:

    price_to_sales=market_cap/revenue

    return price_to_sales

def calculate_fcf_yield(free_cash_flow: float, market_cap: float) -> float:

    fcf_yield=free_cash_flow/market_cap

    return fcf_yield

#Valuation metrics from most recent year data
def calculate_valuation_metrics(company_info: dict, income_statement: pd.DataFrame, cash_flow: pd.DataFrame) -> dict:

    market_cap= company_info["marketCap"]
    net_income= income_statement.loc["NetIncome"].iloc[0]
    revenue= income_statement.loc["TotalRevenue"].iloc[0]
    free_cash_flow= cash_flow.loc["FreeCashFlow"].iloc[0]

    pe_ratio= calculate_pe_ratio(market_cap, net_income)

    price_to_sales= calculate_price_to_sales(market_cap, revenue)

    fcf_yield= calculate_fcf_yield(free_cash_flow, market_cap)
    
    valuation_metrics={
        "pe_ratio": pe_ratio,
        "price_to_sales": price_to_sales,
        "fcf_yield": fcf_yield
    }

    return valuation_metrics


