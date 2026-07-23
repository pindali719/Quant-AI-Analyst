import pandas as pd
import pytest

from app.reports.report_generator import (
    generate_markdown_report,
    save_markdown_report,
)

def generate_dcf_results():


    """Generates an example DCF_result"""

    dcf_sensitivity_table = pd.DataFrame(
        {
            "2.0%": [130.50, 115.20, 102.80],
            "3.0%": [145.70, 126.90, 111.40],
            "4.0%": [168.30, 143.60, 123.90],
        },
        index=["8.0%", "9.0%", "10.0%"],
    )

    result = {
        "fair_value_per_share": 126.90,
        "enterprise_value": 3_120_000_000_000.0,
        "equity_value": 3_080_000_000_000.0,

        "projected_revenue": [
            120_000_000_000.0,
            138_000_000_000.0,
            151_800_000_000.0,
            163_944_000_000.0,
            172_141_200_000.0,
        ],

        "projected_fcf": [
            36_000_000_000.0,
            41_400_000_000.0,
            45_540_000_000.0,
            49_183_200_000.0,
            51_642_360_000.0,
        ],

        "discounted_fcf": [
            32_727_272_727.27,
            34_214_876_033.06,
            34_214_876_033.06,
            33_596_986_325.28,
            32_071_670_329.19,
        ],

        "terminal_value": 760_966_451_428.57,
        "discounted_terminal_value": 472_522_315_091.42,

        "assumptions": {
            "growth_rates": [0.15, 0.12, 0.10, 0.08, 0.05],
            "fcf_margin": 0.30,
            "discount_rate": 0.10,
            "terminal_growth": 0.03,
        },

        "dcf_sensitivity_table": dcf_sensitivity_table,
    }

    return result

def generate_comparison_with_peers():

    """Generates an example peer-comparison result."""

    peer_comparison_table = pd.DataFrame(
        {
            "revenue_growth": [0.25, 0.12, 0.08],
            "gross_margin": [0.65, 0.50, 0.42],
            "operating_margin": [0.40, 0.20, 0.15],
            "net_margin": [0.30, 0.15, 0.10],
            "pe_ratio": [30.0, 25.0, 20.0],
            "ps_ratio": [10.0, 7.0, 5.0],
            "ev_to_ebitda": [22.0, 18.0, 15.0],
            "fcf_yield": [0.03, 0.04, 0.05],
        },
        index=["NVDA", "AMD", "INTC"],
    )


    comparison_with_peers = {
        "peer_comparison_table": peer_comparison_table,

        "valuation_comparison": {
            "multiple_results": {
                "pe_ratio": "above_peers",
                "ps_ratio": "above_peers",
                "ev_to_ebitda": "in_line",
            },
            "multiple_conclusion": "premium_valuation",
            "fcf_yield_result": "below_peers",
        },

        "growth_comparison": {
            "target_revenue_growth": 0.25,
            "peer_median_revenue_growth": 0.12,
            "growth_comparison": "above_peers",
        },

        "profitability_comparison": {
            "margin_comparisons": {
                "gross_margin": "above_peers",
                "operating_margin": "above_peers",
                "net_margin": "in_line",
            },
            "profitability_comparison": "above_peers",
        },

        "quality_adjusted_valuation":
            "premium_supported_by_quality_but_weak_fcf_yield",
    }

    return comparison_with_peers



def generate_scorecard():

    """Generates an example investment scorecard."""

    scorecard = {
        "scores": {
            "growth": 5,
            "profitability": 4,
            "balance_sheet": 4,
            "valuation": 3,
            "risk": 3,
        },

        "overall_score": 4.0,

        "recommendation": "Selective Buy",

        "weights": {
            "growth": 0.30,
            "profitability": 0.25,
            "balance_sheet": 0.15,
            "valuation": 0.20,
            "risk": 0.10,
        },
    }

    return scorecard




def test_generate_markdown_report_contains_required_sections():
    metrics = pd.DataFrame(
        {
            2024: [0.6, 0.2],
            2023: [0.5, 0.15],
        },
        index=["gross_margin", "net_margin"],
    )

    valuation_metrics = {
        "pe_ratio": 30,
        "price_to_sales": 10,
        "fcf_yield": 0.03,
    }

    company_info = {
        "longName": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD"
    }

    chart_paths = {
        "revenue": "outputs/charts/NVDA/revenue.png",
        "margins": "outputs/charts/NVDA/margins.png",
    }

    dcf_result = generate_dcf_results()

    comparison_with_peers = generate_comparison_with_peers()

    scorecard = generate_scorecard()

    report = generate_markdown_report(
        ticker="NVDA",
        company_info=company_info,
        metrics=metrics,
        valuation_metrics=valuation_metrics,
        chart_paths=chart_paths,
        dcf_result= dcf_result,
        comparison_with_peers= comparison_with_peers,
        scorecard= scorecard
    )

    assert "# NVDA Investment Report" in report
    assert "## Company Overview" in report
    assert "## Financial Metrics" in report
    assert "## Valuation Metrics" in report
    assert "## DCF Analysis" in report
    assert "## Peer Comparison" in report
    assert "## Scorecard" in report
    assert "## Charts" in report
    assert "## Preliminary Recommendation" in report
    assert "## Disclaimer" in report
    assert "Selective Buy" in report
    assert "4.0" in report
    assert "Selective Buy" in report
    assert "educational and research purposes" in report


def test_save_markdown_report_creates_file(tmp_path):

    #Creates a tmp_path (folder), and then join path parts
    output_path = tmp_path / "NVDA_report.md"

    saved_path = save_markdown_report(
        markdown_text="# Test Report",
        output_path=str(output_path),
    )

    assert saved_path == str(output_path)
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "# Test Report"