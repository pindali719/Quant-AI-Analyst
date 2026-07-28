import pandas as pd


from app.constants import DEFAULT_PEERS
from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.helpers import latest_value, convert_to_usd, ttm_value, is_missing, ratio_or_none, latest_statement_value
from app.analysis.valuation import calculate_ps_ratio, calculate_pe_ratio,  calculate_ev_to_ebitda

def get_default_peers(ticker: str) -> list[str]:

    peers= list(DEFAULT_PEERS[ticker])

    return peers

def calculate_multiples(
    market_cap: float | None,
    net_income_ttm: float | None,
    revenue_ttm: float | None,
    enterprise_value: float | None,
    ebitda_ttm: float | None,
) -> dict:

    pe_ratio = calculate_pe_ratio(
        market_cap=market_cap,
        net_income_ttm=net_income_ttm,
    )

    ps_ratio = calculate_ps_ratio(
        market_cap=market_cap,
        revenue_ttm=revenue_ttm,
    )

    ev_to_ebitda = calculate_ev_to_ebitda(
        enterprise_value=enterprise_value,
        ebitda_ttm=ebitda_ttm,
    )


    return {
        "pe_ratio": pe_ratio,
        "ps_ratio": ps_ratio,
        "ev_to_ebitda": ev_to_ebitda,
    }

def calculate_fcf_yield(free_cash_flow_ttm: float, market_cap: float) -> float:

    fcf_yield = ratio_or_none(
        numerator=free_cash_flow_ttm,
        denominator=market_cap,
    )

    return fcf_yield

def calculate_leverage(debt: float, stockholders_equity: float) -> float:

    if debt is not None and stockholders_equity is not None and stockholders_equity > 0:
        leverage = debt / stockholders_equity
    else:
        leverage = None

    return leverage


def get_enterprise_value(peer_profile: dict, market_cap: float, debt: float, cash: float) -> float:

    """
    Return Yahoo Finance's current enterprise value when available.

    Otherwise, approximate current enterprise value using:
    current market cap + latest-quarter debt - latest-quarter cash.
    """

    enterprise_value = peer_profile.get("enterpriseValue")

    if not is_missing(enterprise_value):
        return float(enterprise_value)

    if any(is_missing(value) for value in (market_cap, debt, cash)):
        return None

    return float(market_cap + debt - cash)

def fetch_metrics(
    tickers: list[str],
    target_ticker: str,
    target_financial_data: dict | None = None,
) -> pd.DataFrame:
    """
    Calculate period-consistent metrics for the target and peers.

    Period conventions:
    - Revenue growth: latest fiscal year
    - Margins: trailing twelve months
    - ROE and ROIC: TTM numerator / latest-quarter capital
    - Cash, debt, equity and liquidity: latest quarter
    - Valuation: current market values / TTM fundamentals
    """

    target_ticker = target_ticker.upper()

    tickers_to_fetch = [target_ticker]

    for ticker in tickers:
        ticker = ticker.upper()

        if ticker not in tickers_to_fetch:
            tickers_to_fetch.append(ticker)

    all_metrics = []

    for ticker in tickers_to_fetch:
        try:
            # Reuse the target data already fetched in main.py.
            if (
                ticker == target_ticker
                and target_financial_data is not None
            ):
                financial_data = target_financial_data
            else:
                financial_data = fetch_all_financial_data(
                    ticker=ticker
                )

            peer_profile = financial_data["company_info"]

            quote_currency = peer_profile.get("currency")

            financial_currency = peer_profile.get("financialCurrency")

            annual_income_statement = financial_data[
                "income_statement"
            ]
            annual_cash_flow = financial_data["cash_flow"]
            annual_balance_sheet = financial_data[
                "balance_sheet"
            ]

            quarterly_income_statement = financial_data[
                "quarterly_income_statement"
            ]
            quarterly_cash_flow = financial_data[
                "quarterly_cash_flow"
            ]
            quarterly_balance_sheet = financial_data[
                "quarterly_balance_sheet"
            ]

            # -------------------------------------------------
            # Latest fiscal-year growth
            # -------------------------------------------------

            annual_metrics = calculate_all_metrics(
                income_statement=annual_income_statement,
                cash_flow=annual_cash_flow,
                balance_sheet=annual_balance_sheet,
            )

            latest_fy_revenue_growth = latest_value(
                annual_metrics.loc["revenue_growth"]
            )

            # -------------------------------------------------
            # TTM income-statement and cash-flow values
            # -------------------------------------------------

            revenue_ttm = ttm_value(
                quarterly_income_statement,
                "TotalRevenue",
            )

            revenue_ttm = convert_to_usd(
                revenue_ttm,
                financial_currency)

            gross_profit_ttm = ttm_value(
                quarterly_income_statement,
                "GrossProfit",
            )

            operating_income_ttm = ttm_value(
                quarterly_income_statement,
                "OperatingIncome",
            )

            net_income_ttm = ttm_value(
                quarterly_income_statement,
                "NetIncome",
            )

            net_income_ttm = convert_to_usd(
                net_income_ttm,
                financial_currency)

            pretax_income_ttm = ttm_value(
                quarterly_income_statement,
                "PretaxIncome",
            )

            tax_provision_ttm = ttm_value(
                quarterly_income_statement,
                "TaxProvision",
            )

            ebitda_ttm = ttm_value(
                quarterly_income_statement,
                "EBITDA",
            )

            ebitda_ttm = convert_to_usd(
                ebitda_ttm,
                financial_currency)

            free_cash_flow_ttm = ttm_value(
                quarterly_cash_flow,
                "FreeCashFlow",
            )

            free_cash_flow_ttm = convert_to_usd(
                free_cash_flow_ttm,
                financial_currency)

            # -------------------------------------------------
            # TTM margins
            # -------------------------------------------------

            ttm_gross_margin = ratio_or_none(
                numerator=gross_profit_ttm,
                denominator=revenue_ttm,
            )

            ttm_operating_margin = ratio_or_none(
                numerator=operating_income_ttm,
                denominator=revenue_ttm,
            )

            ttm_net_margin = ratio_or_none(
                numerator=net_income_ttm,
                denominator=revenue_ttm,
            )

            # -------------------------------------------------
            # Latest-quarter balance-sheet values
            # -------------------------------------------------

            cash = latest_statement_value(
                quarterly_balance_sheet,
                "CashAndCashEquivalents",
            )

            debt = latest_statement_value(
                quarterly_balance_sheet,
                "TotalDebt",
            )

            stockholders_equity = latest_statement_value(
                quarterly_balance_sheet,
                "StockholdersEquity",
            )

            current_assets = latest_statement_value(
                quarterly_balance_sheet,
                "CurrentAssets",
            )

            current_liabilities = latest_statement_value(
                quarterly_balance_sheet,
                "CurrentLiabilities",
            )

            latest_q_leverage = ratio_or_none(
                numerator=debt,
                denominator=stockholders_equity,
            )

            latest_q_current_ratio = ratio_or_none(
                numerator=current_assets,
                denominator=current_liabilities,
            )

            # -------------------------------------------------
            # Approximate TTM ROE
            #
            # -------------------------------------------------

            approx_ttm_roe = ratio_or_none(
                numerator=net_income_ttm,
                denominator=stockholders_equity,
            )

            # -------------------------------------------------
            # Approximate TTM ROIC
            #
            # NOPAT = TTM operating income × (1 - tax rate)
            # Invested capital = latest equity + debt - cash
            # -------------------------------------------------

            effective_tax_rate = ratio_or_none(
                numerator=tax_provision_ttm,
                denominator=pretax_income_ttm,
            )

            #Tax rate between 0 and 0.50, since any other value is suspicious, and likely wrong
            if (
                not is_missing(effective_tax_rate)
                and 0 <= effective_tax_rate <= 0.50
                and not is_missing(operating_income_ttm)
            ):
                nopat_ttm = (
                    operating_income_ttm
                    * (1 - effective_tax_rate)
                )
            else:
                nopat_ttm = None

            if not any(
                is_missing(value)
                for value in (
                    stockholders_equity,
                    debt,
                    cash,
                )
            ):
                invested_capital = (
                    stockholders_equity
                    + debt
                    - cash
                )
            else:
                invested_capital = None

            approx_ttm_roic = ratio_or_none(
                numerator=nopat_ttm,
                denominator=invested_capital,
            )

            # -------------------------------------------------
            # Current valuation
            # -------------------------------------------------

            market_cap = peer_profile.get("marketCap")

            enterprise_value = get_enterprise_value(
                peer_profile=peer_profile,
                market_cap=market_cap,
                debt=debt,
                cash=cash,
            )

            #Convert the currency to USD if not already USD
            market_cap = convert_to_usd(market_cap, quote_currency)

            enterprise_value = convert_to_usd(enterprise_value, quote_currency)

            multiples = calculate_multiples(
                market_cap=market_cap,
                net_income_ttm=net_income_ttm,
                revenue_ttm=revenue_ttm,
                enterprise_value=enterprise_value,
                ebitda_ttm=ebitda_ttm,
            )

            fcf_yield = calculate_fcf_yield(
                free_cash_flow_ttm=free_cash_flow_ttm,
                market_cap=market_cap,
            )

            all_metrics.append(
                {
                    "ticker": ticker,
                    "market_cap": market_cap,

                    # Latest fiscal year.
                    "latest_fy_revenue_growth":
                        latest_fy_revenue_growth,

                    # Trailing twelve months.
                    "ttm_gross_margin":
                        ttm_gross_margin,
                    "ttm_operating_margin":
                        ttm_operating_margin,
                    "ttm_net_margin":
                        ttm_net_margin,
                    "ttm_net_income":
                        net_income_ttm,
                    "latest_q_equity":
                        stockholders_equity,
                    "approx_ttm_roe":
                        approx_ttm_roe,
                    "approx_ttm_roic":
                        approx_ttm_roic,

                    # Latest reported quarter.
                    "latest_q_cash": cash,
                    "latest_q_debt": debt,
                    "latest_q_equity":
                        stockholders_equity,
                    "latest_q_leverage":
                        latest_q_leverage,
                    "latest_q_current_ratio":
                        latest_q_current_ratio,

                    # Current valuation.
                    "pe_ratio":
                        multiples["pe_ratio"],
                    "ps_ratio":
                        multiples["ps_ratio"],
                    "ev_to_ebitda":
                        multiples["ev_to_ebitda"],
                    "fcf_yield":
                        fcf_yield,
                }
            )

        except Exception as error:
            # The target company is required.
            if ticker == target_ticker:
                raise RuntimeError(
                    f"Could not calculate metrics for "
                    f"{target_ticker}: {error}"
                ) from error

            # An unavailable peer should not abort the analysis.
            print(
                f"Skipping {ticker}: "
                f"{type(error).__name__}: {error}"
            )
            continue

    metrics_df = pd.DataFrame(all_metrics)

    if metrics_df.empty:
        raise ValueError(
            "No valid company metrics were calculated."
        )

    metrics_df = metrics_df.set_index("ticker")

    if target_ticker not in metrics_df.index:
        raise ValueError(
            f"Target ticker {target_ticker} is missing "
            "from the metrics table."
        )

    return metrics_df


def compare_metric(target_value: float, peer_median: float, tolerance: float=0.10) -> str:

    """
    Compare a target metric with its peer median.

    Returns:
    - "above_peers"
    - "below_peers"
    - "in_line"
    - "insufficient_data"

    The tolerance is based on absolute relative distance, so it
    works correctly with both positive and negative medians.
    """

    if (
        is_missing(target_value)
        or is_missing(peer_median)
    ):
        return "insufficient_data"

    # Relative comparison is not meaningful when the median is zero.
    if peer_median == 0:
        if target_value == 0:
            return "in_line"

        return (
            "above_peers"
            if target_value > 0
            else "below_peers"
        )

    relative_distance = (
        abs(target_value - peer_median)
        / abs(peer_median)
    )

    if relative_distance <= tolerance:
        return "in_line"

    if target_value > peer_median:
        return "above_peers"

    return "below_peers"


def evaluate_growth(
    target: pd.Series,
    peers: pd.DataFrame,
) -> dict:

    metric_name = "latest_fy_revenue_growth"

    target_growth = target.get(metric_name)
    peer_median_growth = peers[metric_name].median()

    return {
        "target_revenue_growth": target_growth,
        "peer_median_revenue_growth":
            peer_median_growth,
        "growth_comparison": compare_metric(
            target_value=target_growth,
            peer_median=peer_median_growth,
        ),
    }


def evaluate_profitability(
    target: pd.Series,
    peers: pd.DataFrame,
) -> dict:

    margin_columns = [
        "ttm_gross_margin",
        "ttm_operating_margin",
        "ttm_net_margin",
    ]

    details = {}

    for column in margin_columns:
        details[column] = compare_metric(
            target_value=target.get(column),
            peer_median=peers[column].median(),
        )

    above_count = sum(
        result == "above_peers"
        for result in details.values()
    )

    below_count = sum(
        result == "below_peers"
        for result in details.values()
    )

    if above_count >= 2:
        overall = "above_peers"
    elif below_count >= 2:
        overall = "below_peers"
    elif above_count > 0 and below_count > 0:
        overall = "mixed"
    else:
        overall = "in_line"

    return {
        "margin_comparisons": details,
        "profitability_comparison": overall,
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

def create_peer_comparison_table(
    target_metrics: pd.Series,
    peers_metrics: pd.DataFrame,
) -> pd.DataFrame:

    comparison_table = pd.concat(
        [
            target_metrics.to_frame().T,
            peers_metrics,
        ]
    )

    columns = [
        "market_cap",
        "latest_fy_revenue_growth",
        "ttm_gross_margin",
        "ttm_operating_margin",
        "ttm_net_margin",
        "approx_ttm_roe",
        "approx_ttm_roic",
        "pe_ratio",
        "ps_ratio",
        "ev_to_ebitda",
        "fcf_yield",
        "latest_q_leverage",
        "latest_q_current_ratio",
    ]

    return comparison_table.loc[:, columns]

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


