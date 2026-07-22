from pathlib import Path
import pandas as pd


def format_number(value):
    """
    Format numbers nicely for the markdown report.
    """
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return str(value)


def format_percentage(value):
    """Format decimal values as percentages."""

    if value is None:
        return "N/A"

    return f"{value:.1%}"


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """
    Convert a DataFrame into a basic markdown table without extra dependencies.
    """
    df = df.copy()

    # Keep the index visible in the report
    df = df.reset_index()

    headers = list(df.columns)

    header_row = "| " + " | ".join(str(col) for col in headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"

    body_rows = []
    for _, row in df.iterrows():
        body_row = "| " + " | ".join(format_number(value) for value in row) + " |"
        body_rows.append(body_row)

    return "\n".join([header_row, separator_row] + body_rows)

def make_dcf_assumptions_text(assumptions: dict) -> str:
    """
    Build the DCF assumptions subsection.
    """

    lines = []

    lines.append("### DCF Assumptions")
    lines.append("")
    lines.append(f"- **Discount rate:** {format_percentage(assumptions.get('discount_rate'))}")
    lines.append(f"- **Terminal growth rate:** {format_percentage(assumptions.get('terminal_growth'))}")
    lines.append(f"- **FCF margin:** {format_percentage(assumptions.get('fcf_margin'))}")

    growth_rates = assumptions.get("growth_rates")

    if growth_rates is not None:
        formatted_growth_rates = []

        for growth_rate in growth_rates:
            formatted_growth_rates.append(format_percentage(growth_rate))

        lines.append(f"- **Revenue growth assumptions:** {', '.join(formatted_growth_rates)}")

    return "\n".join(lines)


def make_projected_fcf_text(projected_fcf: list, currency: str) -> str:
    """
    Build the projected free cash flow subsection.
    """

    if projected_fcf is None:
        return ""

    lines = []

    lines.append(f"### Projected Free Cash Flow ({currency})")
    lines.append("")

    for year_number, fcf in enumerate(projected_fcf, start=1):
        lines.append(f"- **Year {year_number}:** {format_number(fcf)}")

    return "\n".join(lines)


def make_dcf_sensitivity_text(sensitivity_table) -> str:
    """
    Build the DCF sensitivity table subsection.
    """

    if sensitivity_table is None:
        return ""

    lines = []

    lines.append("### DCF Sensitivity Table")
    lines.append("")
    lines.append(dataframe_to_markdown(sensitivity_table))

    return "\n".join(lines)


def make_dcf_section(dcf_result: dict, currency: str) -> str:
    """
    Build the DCF Analysis section.

    This section only presents calculated DCF data.
    Later, the AI agent can replace or extend this with written interpretation.
    """

    if dcf_result is None:
        return "DCF analysis was not included in this report."

    lines = []

    fair_value_per_share = dcf_result.get("fair_value_per_share")
    enterprise_value = dcf_result.get("enterprise_value")
    equity_value = dcf_result.get("equity_value")
    assumptions = dcf_result.get("assumptions", {})
    projected_fcf = dcf_result.get("projected_fcf")
    sensitivity_table = dcf_result.get("sensitivity_table")



    lines.append(f"### DCF Valuation Output ({currency})")
    lines.append("")
    lines.append(f"- **Estimated fair value per share:** {format_number(fair_value_per_share)}")
    lines.append(f"- **Enterprise value:** {format_number(enterprise_value)}")
    lines.append(f"- **Equity value:** {format_number(equity_value)}")
    lines.append("")

    dcf_assumptions_text = make_dcf_assumptions_text(assumptions)

    if dcf_assumptions_text !="":
        lines.append(dcf_assumptions_text)
        lines.append("")

    projected_fcf_text = make_projected_fcf_text(projected_fcf= projected_fcf, currency= currency)

    if projected_fcf_text != "":
        lines.append(projected_fcf_text)
        lines.append("")

    sensitivity_text = make_dcf_sensitivity_text(sensitivity_table)

    if sensitivity_text != "":
        lines.append(sensitivity_text)
        lines.append("")

    return "\n".join(lines)

def make_peer_comparison_text(comparison_with_peers: dict, ticker):
    
    peer_comparison_table = comparison_with_peers.get("peer_comparison_table")

    #A list containing the indexes of the table (so it contains the tickers)
    peers = peer_comparison_table.index.tolist()
    peers = peers.remove(ticker)

    summary = peer_comparison_table.get("quality_adjusted_valuation")

    lines = []

    lines.append(f"{ticker} is compared against {peers}.")
    lines.append("")
    lines.append(f"{dataframe_to_markdown(peer_comparison_table)}")
    lines.append("")
    lines.append(f"Summary: {summary}")
    lines.append("")

    return "\n".join(lines)

def make_scorecard_text(scorecard: dict):

    lines = []

    scores = scorecard.get("scores")
    scores_df = pd.DataFrame.from_dict(scores, orient="index", columns=["score"],).rename_axis("Category")

    lines.append(f"{dataframe_to_markdown(scores_df)}")
    lines.append("")
    lines.append(f"Overall score: {scorecard.get("overall_score")}")
    lines.append(f"Recommendation: {scorecard.get("recommendation")}")
    lines.append("")

    return "\n".join(lines)

    


def make_preliminary_recommendation(metrics: pd.DataFrame, valuation_metrics: dict) -> str:
    """
    Very simple rule-based recommendation.

    This is intentionally basic for the MVP.
    """
    return (
        "Preliminary view: Hold / Selective Buy.\n\n"
        "Reason: the company shows strong financial performance, "
        "but the valuation should be reviewed carefully before making a decision."
    )

def make_valuation_text(valuation_metrics: dict):
    valuation_lines = []
    for metric_name, metric_value in valuation_metrics.items():
        valuation_lines.append(f"- **{metric_name}:** {format_number(metric_value)}")

    return "\n".join(valuation_lines)

def make_chart_text(chart_paths: dict):

    chart_lines = []
    for chart_name, chart_path in chart_paths.items():
        chart_lines.append(f"- **{chart_name}:** `{chart_path}`")
    
    return "\n".join(chart_lines)

def generate_markdown_report(
    ticker: str,
    company_info: dict,
    metrics: pd.DataFrame,
    valuation_metrics: dict,
    chart_paths: dict,
    dcf_result: dict,
    comparison_with_peers: dict,
    scorecard: dict
) -> str:
    """
    Build the markdown report as one large string.
    """

    company_name = company_info.get("longName", ticker)
    sector = company_info.get("sector", "N/A")
    industry = company_info.get("industry", "N/A")
    currency = company_info.get("currency")

    financial_metrics_table = dataframe_to_markdown(metrics)

    #Change the name of free_cash_flow to free_cash_flow (CURRENCY)

    financial_metrics_table = financial_metrics_table.replace("free_cash_flow", f"free_cash_flow ({currency})")

    valuation_text = make_valuation_text(valuation_metrics= valuation_metrics)
    chart_text = make_chart_text(chart_paths= chart_paths)
    dcf_text = make_dcf_section(dcf_result = dcf_result, currency= currency)
    peer_comparison_text = make_peer_comparison_text(comparison_with_peers= comparison_with_peers)
    scorecard_text = make_scorecard_text(scorecard= scorecard)

    recommendation = make_preliminary_recommendation(metrics, valuation_metrics)


    report = f"""# {ticker} Investment Report

## Company Overview

**Company:** {company_name}  
**Ticker:** {ticker}  
**Sector:** {sector}  
**Industry:** {industry}  

## Financial Metrics

{financial_metrics_table}

## Valuation Metrics

{valuation_text}

## DCF Analysis

{dcf_text}

## Peer comparison

{peer_comparison_text}

## Scorecard

{scorecard_text}

## Charts

{chart_text}

## Preliminary Recommendation

{recommendation}

## Disclaimer

This project is for educational and research purposes only. It does not provide financial advice.
"""

    return report


def save_markdown_report(markdown_text: str, output_path: str) -> str:
    """
    Save the markdown report to a file.
    """
    #Transforms the string into a path object
    output_path = Path(output_path)

    # Create the folder if it does not exist yet
    output_path.parent.mkdir(parents=True, exist_ok=True)

    #Writes the text in that file
    output_path.write_text(markdown_text, encoding="utf-8")

    return str(output_path)


def generate_report(
    ticker: str,
    company_info: dict,
    metrics: pd.DataFrame,
    valuation_metrics: dict,
    chart_paths: dict,
    output_path: str,
    dcf_result: dict,
    comparison_with_peers: dict,
    scorecard: dict

) -> str:
    
    """
    Main function used by main.py.

    It creates the markdown text and saves it.
    """
    markdown_text = generate_markdown_report(
        ticker=ticker,
        company_info=company_info,
        metrics=metrics,
        valuation_metrics=valuation_metrics,
        chart_paths=chart_paths,
        dcf_result=dcf_result,
        comparison_with_peers= comparison_with_peers,
        scorecard= scorecard
    )

    saved_path = save_markdown_report(markdown_text, output_path)

    return saved_path