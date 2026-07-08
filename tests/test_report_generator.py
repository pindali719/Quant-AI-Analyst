import pandas as pd

from app.reports.report_generator import (
    generate_markdown_report,
    save_markdown_report,
)


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
    }

    chart_paths = {
        "revenue": "outputs/charts/NVDA/revenue.png",
        "margins": "outputs/charts/NVDA/margins.png",
    }

    report = generate_markdown_report(
        ticker="NVDA",
        company_info=company_info,
        metrics=metrics,
        valuation_metrics=valuation_metrics,
        chart_paths=chart_paths,
    )

    assert "# NVDA Investment Report" in report
    assert "## Company Overview" in report
    assert "## Financial Metrics" in report
    assert "## Valuation Metrics" in report
    assert "## Charts" in report
    assert "## Preliminary Recommendation" in report
    assert "## Disclaimer" in report
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