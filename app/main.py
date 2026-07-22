import argparse

from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.analysis.valuation import calculate_valuation_metrics
from app.visualization.plots import generate_all_charts
from app.reports.report_generator import generate_report
from app.analysis.dcf import run_dcf_scenarios, enter_assumption, get_dcf_scenary_result
from app.tools.competitor_analysis import get_default_peers, fetch_metrics, compare_against_peers
from app.analysis.scoring import generate_scorecard



def parse_args():
    """
    Read the ticker from the terminal.

    Example:
    python -m app.main --ticker NVDA
    """
    parser = argparse.ArgumentParser(description="AI Equity Research Analyst")

    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Stock ticker to analyze, for example NVDA",
    )

    return parser.parse_args()


def run_analysis(ticker: str):
    """
    Run the full analysis pipeline for one ticker.
    """

    ticker = ticker.upper()

    print(f"Starting analysis for {ticker}...")

    # 1. Fetch financial data
    print("Fetching financial data...")
    financial_data = fetch_all_financial_data(ticker)

    company_info = financial_data["company_info"]
    income_statement = financial_data["income_statement"]
    balance_sheet = financial_data["balance_sheet"]
    cash_flow = financial_data["cash_flow"]
    historical_prices = financial_data["historical_prices"]

    # 2. Calculate financial metrics
    print("Calculating financial metrics...")
    metrics = calculate_all_metrics(
        income_statement=income_statement,
        cash_flow=cash_flow,
        balance_sheet=balance_sheet
    )

    # 3. Calculate valuation metrics
    print("Calculating valuation metrics...")
    valuation_metrics = calculate_valuation_metrics(
        company_info=company_info,
        income_statement=income_statement,
        cash_flow=cash_flow,
    )


    # 4. Running DCF

    print("Running DCF...")

    market_data = {
        "current_price": company_info["currentPrice"],
        "market_cap": company_info["marketCap"],
        "enterprise_value": company_info["enterpriseValue"],
        "shares_outstanding": company_info["sharesOutstanding"],
    }

    financials = {
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
    }

    dcf_scenarios = run_dcf_scenarios(financials= financials, market_data= market_data)

    type_of_assumption = enter_assumption()
    
    dcf_results = get_dcf_scenary_result(type_of_assumption= type_of_assumption, dcf_scenarios= dcf_scenarios)

   # 5. Analysing competitors....

    print("Analysing competitors...")

    peers = get_default_peers(ticker= ticker)
    all_metrics = fetch_metrics(tickers= peers, target_ticker= ticker)
    comparison_with_peers = compare_against_peers(target_ticker= ticker, all_metrics= all_metrics)

    # 6. Scoring
    print("Scoring...")

    risks = None

    scorecard = generate_scorecard(risks= risks, target_ticker= ticker, all_metrics= all_metrics, fair_value_per_share= dcf_results.get("fair_value_per_share"), current_price= market_data.get("current_price"))
    peer_df = comparison_with_peers.get("peer_comparison_table")

    # 7. Generate charts
    print("Generating charts...")

    chart_paths = generate_all_charts(
        ticker=ticker,
        income_statement=income_statement,
        cash_flow=cash_flow,
        metrics=metrics,
        historical_prices=historical_prices,
        sensitivity_table= dcf_results["dcf_sensitivity_table"],
        peer_df= peer_df
    )

    # 8. Generate markdown report
    print("Generating report...")
    report_path = generate_report(
        ticker=ticker,
        company_info=company_info,
        metrics=metrics,
        valuation_metrics=valuation_metrics,
        chart_paths=chart_paths,
        output_path=f"outputs/markdown/{ticker}_investment_report.md",
        dcf_result=dcf_results,
        comparison_with_peers= comparison_with_peers,
        scorecard= scorecard
    )

    print(f"Done. Report saved to: {report_path}")


def main():
    """
    Main entry point.
    """
    args = parse_args()
    run_analysis(args.ticker)


if __name__ == "__main__":
    main()  