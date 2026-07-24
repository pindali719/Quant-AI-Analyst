import pandas as pd


from app.constants import DEFAULT_PEERS
from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.helpers import latest_value, safe_division, ttm_value

def get_default_peers(ticker: str) -> list[str]:

    peers= DEFAULT_PEERS[ticker]

    return peers

def calculate_multiples(market_cap: float, net_income_ttm: float, revenue_ttm: float, enterprise_value: float, ebitda_ttm: float) -> dict:

    if market_cap is not None and net_income_ttm is not None and net_income_ttm > 0:
        pe_ratio = market_cap / net_income_ttm
    else:
        pe_ratio = None

    if market_cap is not None and revenue_ttm is not None and revenue_ttm > 0:
        ps_ratio = market_cap / revenue_ttm
    else:
        ps_ratio = None


    if enterprise_value is not None and ebitda_ttm is not None and ebitda_ttm > 0:
        ev_to_ebitda = enterprise_value / ebitda_ttm
    else:
        ev_to_ebitda = None

    return {
        "pe_ratio": pe_ratio,
        "ps_ratio": ps_ratio,
        "ev_to_ebida": ev_to_ebitda,
    }

def calculate_fcf_yield(free_cash_flow_ttm: float, market_cap: float) -> float:

    if free_cash_flow_ttm is not None and market_cap is not None and market_cap > 0:
        fcf_yield = free_cash_flow_ttm / market_cap
    else:
        fcf_yield = None

    return fcf_yield

def calculate_leverage(debt: float, stockholders_equity: float) -> float:

    if debt is not None and stockholders_equity is not None and stockholders_equity > 0:
        leverage = debt / stockholders_equity
    else:
        leverage = None

    return leverage


def get_enterprise_value(peer_profile: dict, market_cap: float, debt: float, cash: float) -> float:

    enterprise_value = peer_profile.get("enterpriseValue")

    if enterprise_value is None and None not in (market_cap, debt, cash):

        enterprise_value = market_cap + debt - cash

    return enterprise_value

def fetch_metrics(tickers: list[str], target_ticker: str) -> pd.DataFrame:

    all_metrics= []

    tickers.append(target_ticker)
    
    for ticker in tickers:
        try:

            peer_profile= all_financial_data.get("company_info")
            all_financial_data = fetch_all_financial_data(ticker= ticker)
            annual_income_statement = all_financial_data.get("income_statement")
            annual_cash_flow = all_financial_data.get("cash_flow")
            annual_balance_sheet = all_financial_data.get("balance_sheet")
            metrics_of_ticker = calculate_all_metrics(
                income_statement= annual_income_statement,
                cash_flow= annual_cash_flow,
                balance_sheet= annual_balance_sheet)

            
            revenue_growth = latest_value(metrics_of_ticker.loc["revenue_growth"])
            gross_margin = latest_value(metrics_of_ticker.loc["gross_margin"])
            operating_margin= latest_value(metrics_of_ticker.loc["operating_margin"])
            net_margin = latest_value(metrics_of_ticker.loc["net_margin"])

            quarterly_income_statement = all_financial_data["quarterly_income_statement"]

            quarterly_cash_flow = all_financial_data["quarterly_cash_flow"]

            quarterly_balance_sheet = all_financial_data["quarterly_balance_sheet"]


            net_income_ttm = ttm_value(quarterly_income_statement, "NetIncome")
            revenue_ttm = ttm_value(quarterly_income_statement, "TotalRevenue")
            ebitda_ttm = ttm_value(quarterly_income_statement,"EBITDA")
            free_cash_flow_ttm = ttm_value(quarterly_cash_flow, "FreeCashFlow")
            market_cap = peer_profile.get("marketCap")

            cash = latest_value(quarterly_balance_sheet.loc["CashAndCashEquivalents"])
            debt = latest_value(quarterly_balance_sheet.loc["TotalDebt"])
            stockholders_equity = latest_value(quarterly_balance_sheet.loc["StockholdersEquity"])

            enterprise_value = get_enterprise_value(peer_profile= peer_profile, market_cap= market_cap, debt= debt, cash= cash)

            multiples = calculate_multiples(
                market_cap= market_cap,
                net_income_ttm= net_income_ttm,
                revenue_ttm= revenue_ttm,
                enterprise_value= enterprise_value, 
                ebitda_ttm= ebitda_ttm,
                )
            
            pe_ratio = multiples.get("pe_ratio")
            ps_ratio = multiples.get("ps_ratio")
            ev_to_ebitda = multiples.get("ev_to_ebitda")


            fcf_yield = calculate_fcf_yield(free_cash_flow_ttm= free_cash_flow_ttm, market_cap= market_cap)

            leverage = calculate_leverage(debt= debt, stockholders_equity= stockholders_equity)

            metrics ={
                "ticker": ticker,
                "market_cap": market_cap,
                "revenue_growth": revenue_growth,
                "gross_margin": gross_margin,
                "operating_margin": operating_margin,
                "net_margin": net_margin,
                "pe_ratio": pe_ratio,
                "ps_ratio": ps_ratio,
                "ev_to_ebitda": ev_to_ebitda,
                "fcf_yield": fcf_yield,
                "leverage": leverage
            }

            all_metrics.append(metrics)


        except Exception as error:
            print(f"Skipping {ticker}: "f"{type(error).__name__}: {error}") 
            raise
    
    all_metrics= pd.DataFrame(all_metrics).set_index("ticker")
    
    return all_metrics


def compare_metric(target_value: float, peer_median: float, tolerance=0.10) -> str:
    """
    Compare a target metric against the peer median.

    Returns both:
    - relative_position: whether the metric is numerically above/below peers
    - interpretation: whether that is good/bad/in line
    """

    if pd.isna(target_value) or pd.isna(peer_median) or peer_median == 0:
        return "insufficient_data"

    upper_bound = peer_median * (1 + tolerance)
    lower_bound = peer_median * (1 - tolerance)

    if lower_bound <= target_value <= upper_bound:
        return "in_line"

    if target_value > peer_median:
        return "above_peers"

    return "below_peers"
    

def evaluate_growth(target: pd.Series, peers: pd.DataFrame) -> str:

    target_revenue_growth = target["revenue_growth"]
    peer_median_revenue_growth = peers["revenue_growth"].median()

    result = {
        "target_revenue_growth": target_revenue_growth,
        "peer_median_revenue_growth": peer_median_revenue_growth,
        "growth_comparison": compare_metric(target_value= target_revenue_growth, peer_median= peer_median_revenue_growth)
        }

    return result


def evaluate_profitability(target: pd.Series, peers: pd.DataFrame):
    margin_cols = ["gross_margin", "operating_margin", "net_margin"]

    details = {}

    for col in margin_cols:
        details[col] = compare_metric(
            target[col],
            peers[col].median()
        )

    above_count = sum(value == "above_peers" for value in details.values())
    below_count = sum(value == "below_peers" for value in details.values())

    if above_count >= 2:
        overall = "above_peers"
    elif below_count >= 2:
        overall = "below_peers"
    elif (above_count == below_count) and (above_count > 0):
        overall = "mixed"
    else:
        overall = "in_line"

    return {
        "margin_comparisons": details,
        "profitability_comparison": overall
    }

def evaluate_valuation(target, peers):
    multiple_cols = ["pe_ratio", "ps_ratio", "ev_to_ebitda"]

    multiple_results = {}

    for col in multiple_cols:
        multiple_results[col] = compare_metric(
            target[col],
            peers[col].median(),
        )

    fcf_yield_result= compare_metric(
        target["fcf_yield"],
        peers["fcf_yield"].median(),
    )

    expensive_count = sum(
        result == "above_peers"
        for result in multiple_results.values()
    )

    cheap_count = sum(
        result == "below_peers"
        for result in multiple_results.values()
    )

    if expensive_count >= 2:
        multiple_conclusion = "premium_valuation"
    elif cheap_count >= 2:
        multiple_conclusion = "discount_valuation"
    elif expensive_count > 0 and cheap_count > 0:
        multiple_conclusion = "mixed"
    elif expensive_count == 1:
        multiple_conclusion = "mostly_in_line_with_premium_signal"
    elif cheap_count == 1:
        multiple_conclusion = "mostly_in_line_with_discount_signal"
    else:
        multiple_conclusion = "in_line"

    return {
        "multiple_results": multiple_results,
        "multiple_conclusion": multiple_conclusion,
        "fcf_yield_result": fcf_yield_result,
    }

def interpret_quality_adjusted_valuation(
    growth_comparison: str,
    profitability_comparison: str,
    multiple_conclusion: str,
    fcf_yield_result,
) -> str:
    """
    Combine:
    - growth comparison
    - profitability comparison
    - valuation multiple conclusion
    - FCF yield interpretation

    into one quality-adjusted valuation view.
    """

    strong_quality = (
        growth_comparison == "above_peers"
        and profitability_comparison == "above_peers"
    )

    weak_quality = (
        growth_comparison == "below_peers"
        and profitability_comparison == "below_peers"
    )

    strong_fcf_yield = fcf_yield_result == "above_peers"
    weak_fcf_yield = fcf_yield_result == "below_peers"

    if multiple_conclusion == "premium_valuation":
        if strong_quality and strong_fcf_yield:
            return "premium_supported_by_quality_and_cash_flow"

        if strong_quality and weak_fcf_yield:
            return "premium_supported_by_quality_but_weak_fcf_yield"

        if weak_quality and weak_fcf_yield:
            return "premium_and_risky"

        if strong_quality:
            return "premium_potentially_justified_by_quality"

        return "premium_valuation_requires_caution"

    if multiple_conclusion == "discount_valuation":
        if strong_quality and strong_fcf_yield:
            return "potentially_attractive_valuation"

        if strong_quality and weak_fcf_yield:
            return "cheap_on_multiples_but_cash_flow_yield_is_weak"

        if weak_quality:
            return "cheap_but_possible_value_trap"

        return "discount_valuation_with_mixed_quality"

    if multiple_conclusion == "mixed":
        if strong_quality and strong_fcf_yield:
            return "mixed_multiples_but_quality_and_cash_flow_are_strong"

        if strong_quality and weak_fcf_yield:
            return "mixed_multiples_with_quality_but_weak_fcf_yield"

        if weak_quality:
            return "mixed_multiples_with_weak_fundamentals"

        return "mixed_valuation_signals"

    if multiple_conclusion == "mostly_in_line_with_premium_signal":
        if strong_quality:
            return "mostly_fair_valuation_with_some_premium_signal"

        return "mostly_fair_valuation_but_premium_signal_requires_caution"

    if multiple_conclusion == "mostly_in_line_with_discount_signal":
        if strong_quality or strong_fcf_yield:
            return "mostly_fair_valuation_with_some_discount_signal"

        return "mostly_fair_valuation_with_limited_discount_support"

    if multiple_conclusion == "in_line":
        if strong_quality and strong_fcf_yield:
            return "fair_valuation_with_strong_quality_and_cash_flow"

        if strong_quality:
            return "fair_valuation_with_strong_quality"

        if weak_quality and weak_fcf_yield:
            return "fair_multiples_but_weak_fundamentals"

        return "valuation_in_line"

    return "insufficient_data"

def create_peer_comparison_table(target_metrics: pd.Series, peers_metrics: pd.DataFrame) -> pd.DataFrame:

    """Create a table where target is being compared with peers. Specifically, the following metrics: market_cap, revenue_growth"""

    comparison_table = pd.concat([target_metrics.to_frame().T, peers_metrics])
    
    comparison_table = comparison_table.loc[:, ["market_cap", "revenue_growth", "pe_ratio", "ps_ratio", "ev_to_ebitda", "fcf_yield"]]

    return comparison_table

def compare_against_peers(target_ticker: str, all_metrics: pd.DataFrame) -> dict:

    target = all_metrics.loc[target_ticker]

    peers = all_metrics.drop(index=target_ticker)

    growth_comparison = evaluate_growth(target=target, peers= peers)
    profitability_comparison = evaluate_profitability(target= target, peers= peers)
    valuation_comparison = evaluate_valuation(target=target, peers= peers)
    quality_adjusted_valuation = interpret_quality_adjusted_valuation(growth_comparison= growth_comparison.get("growth_comparison"),
                                                                    profitability_comparison= profitability_comparison.get("profitability_comparison"),
                                                                    multiple_conclusion= valuation_comparison.get("multiple_conclusion"),
                                                                    fcf_yield_result= valuation_comparison.get("fcf_yield_result"))

    peer_comparison_table = create_peer_comparison_table(target_metrics= target, peers_metrics= peers)

    return {
        "valuation_comparison": valuation_comparison,
        "growth_comparison": growth_comparison,
        "profitability_comparison": profitability_comparison,
        "quality_adjusted_valuation": quality_adjusted_valuation,
        "peer_comparison_table" : peer_comparison_table
    }


