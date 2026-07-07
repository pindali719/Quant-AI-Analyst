from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


CHARTS_DIR = Path("outputs/charts")

#Create outputs/charts folder if it does not exist.
def ensure_charts_dir():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)



def to_year_series(series: pd.Series) -> pd.Series:
    """
    Convert a yfinance Series indexed by dates into a Series indexed by years.
    Also sorts from oldest year to newest year.
    """
    series = series.dropna().copy()

    # yfinance columns are usually dates, so the Series index is dates
    series.index = pd.to_datetime(series.index).year

    # Sort years from oldest to newest
    series = series.sort_index()

    return series


def plot_revenue(income_statement: pd.DataFrame, ticker: str) -> str:
    """Save revenue trend chart."""

    ensure_charts_dir()

    revenue = income_statement.loc["TotalRevenue"]

    revenue = to_year_series(revenue)

    # Convert to billions to make the chart easier to read
    revenue_billions = revenue / 1e9

    plt.figure(figsize=(8, 5))
    plt.plot(revenue_billions.index, revenue_billions.values, marker="o")

    plt.title(f"{ticker} Revenue Trend")
    plt.xlabel("Year")
    plt.ylabel("Revenue ($ billions)")
    plt.grid(True)

    file_path = CHARTS_DIR / f"{ticker}_revenue.png"
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()

    return str(file_path)



def to_percentage(series: pd.Series) -> pd.Series:
    """
    Convert margin ratios to percentages.

    Example:
    0.45 becomes 45.0
    """
    series = series.dropna().copy()
    series = series.sort_index()

    if series.abs().max() <= 1.5:
        series = series * 100

    return series


def plot_margins(metrics: pd.DataFrame, ticker: str) -> str:
    """Save gross, operating, and net margin chart."""

    ensure_charts_dir()

    gross_margin = metrics.loc["gross_margin"]

    operating_margin = metrics.loc["operating_margin"]

    net_margin = metrics.loc["net_margin"]

    gross_margin = to_percentage(gross_margin)
    operating_margin = to_percentage(operating_margin)
    net_margin = to_percentage(net_margin)

    plt.figure(figsize=(8, 5))

    plt.plot(gross_margin.index, gross_margin.values, marker="o", label="Gross Margin")
    plt.plot(operating_margin.index, operating_margin.values, marker="o", label="Operating Margin")
    plt.plot(net_margin.index, net_margin.values, marker="o", label="Net Margin")

    plt.title(f"{ticker} Profit Margins")
    plt.xlabel("Year")
    plt.ylabel("Margin (%)")
    plt.grid(True)
    plt.legend()

    file_path = CHARTS_DIR / f"{ticker}_margins.png"
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()

    return str(file_path)


def plot_free_cash_flow(cash_flow: pd.DataFrame, ticker: str) -> str:
    """Save free cash flow chart."""

    ensure_charts_dir()

    free_cash_flow = cash_flow.loc["FreeCashFlow"]

    free_cash_flow = to_year_series(free_cash_flow)

    # Convert to billions
    free_cash_flow_billions = free_cash_flow / 1e9

    plt.figure(figsize=(8, 5))
    plt.bar(free_cash_flow_billions.index, free_cash_flow_billions.values)

    plt.title(f"{ticker} Free Cash Flow")
    plt.xlabel("Year")
    plt.ylabel("Free Cash Flow ($ billions)")
    plt.grid(axis="y")

    file_path = CHARTS_DIR / f"{ticker}_free_cash_flow.png"
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()

    return str(file_path)


def generate_all_charts(income_statement: pd.DataFrame, cash_flow: pd.DataFrame, metrics: pd.DataFrame, ticker: str, historical_prices: pd.DataFrame) -> dict:
    """Generate all charts and return file paths."""

    revenue_chart = plot_revenue(income_statement, ticker)
    margins_chart = plot_margins(metrics, ticker)
    free_cash_flow_chart = plot_free_cash_flow(cash_flow, ticker)

    return {
        "revenue_chart": revenue_chart,
        "margins_chart": margins_chart,
        "free_cash_flow_chart": free_cash_flow_chart
    }

