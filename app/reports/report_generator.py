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


def make_preliminary_recommendation(metrics: pd.DataFrame, valuation_metrics: dict) -> str:
    """
    Very simple rule-based recommendation.

    This is intentionally basic for the MVP.
    Later, you can replace it with a scoring system.
    """
    return (
        "Preliminary view: Hold / Selective Buy.\n\n"
        "Reason: the company shows strong financial performance, "
        "but the valuation should be reviewed carefully before making a decision."
    )


def generate_markdown_report(
    ticker: str,
    company_info: dict,
    metrics: pd.DataFrame,
    valuation_metrics: dict,
    chart_paths: dict,
) -> str:
    """
    Build the markdown report as one large string.
    """

    company_name = company_info.get("longName", ticker)
    sector = company_info.get("sector", "N/A")
    industry = company_info.get("industry", "N/A")

    financial_metrics_table = dataframe_to_markdown(metrics)

    valuation_lines = []
    for metric_name, metric_value in valuation_metrics.items():
        valuation_lines.append(f"- **{metric_name}:** {format_number(metric_value)}")

    chart_lines = []
    for chart_name, chart_path in chart_paths.items():
        chart_lines.append(f"- **{chart_name}:** `{chart_path}`")

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

{"\n".join(valuation_lines)}

## Charts

{"\n".join(chart_lines)}

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
    )

    saved_path = save_markdown_report(markdown_text, output_path)

    return saved_path