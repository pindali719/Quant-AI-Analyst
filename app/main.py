import argparse

from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics
from app.analysis.valuation import calculate_valuation_metrics
from app.visualization.plots import generate_all_charts
from app.reports.report_generator import generate_report


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

    # 4. Generate charts
    print("Generating charts...")
    chart_paths = generate_all_charts(
        ticker=ticker,
        income_statement=income_statement,
        cash_flow=cash_flow,
        metrics=metrics,
        historical_prices=historical_prices,
    )

    # 5. Generate markdown report
    print("Generating report...")
    report_path = generate_report(
        ticker=ticker,
        company_info=company_info,
        metrics=metrics,
        valuation_metrics=valuation_metrics,
        chart_paths=chart_paths,
        output_path=f"outputs/markdown/{ticker}_investment_report.md",
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