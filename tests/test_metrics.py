import pytest
import pandas as pd

from app.analysis.metrics import calculate_all_metrics

def make_income_statement():
    years = pd.to_datetime(["2024-01-31", "2023-01-31", "2022-01-31"])

    return pd.DataFrame(
        {
            years[0]: {
                "TotalRevenue": 300,
                "GrossProfit": 180,
                "OperatingIncome": 90,
                "NetIncome": 60,
            },
            years[1]: {
                "TotalRevenue": 200,
                "GrossProfit": 100,
                "OperatingIncome": 50,
                "NetIncome": 40,
            },
            years[2]: {
                "TotalRevenue": 100,
                "GrossProfit": 40,
                "OperatingIncome": 20,
                "NetIncome": 10,
            },
        }
    )


def make_cash_flow():
    years = pd.to_datetime(["2024-01-31", "2023-01-31", "2022-01-31"])

    return pd.DataFrame(
        {
            years[0]: {
                "FreeCashFlow": 80,
                "OperatingCashFlow": 100,
                "CapitalExpenditure": -20,
            },
            years[1]: {
                "FreeCashFlow": 50,
                "OperatingCashFlow": 70,
                "CapitalExpenditure": -20,
            },
            years[2]: {
                "FreeCashFlow": 20,
                "OperatingCashFlow": 30,
                "CapitalExpenditure": -10,
            },
        }
    )

def test_calculate_all_metrics():

    income_statement= make_income_statement()
    cash_flow = make_cash_flow()
    balance_sheet=pd.DataFrame()

    result = calculate_all_metrics(income_statement=income_statement, cash_flow=cash_flow, balance_sheet= balance_sheet)

    years= pd.to_datetime(["2024-01-31", "2023-01-31", "2022-01-31"])

    # Revenue growth:
    # 2022 has no previous year, so it should be NaN.
    # 2023: (200 - 100) / 100 = 1.0
    # 2024: (300 - 200) / 200 = 0.5
    assert pd.isna(result.loc["revenue_growth", 2022])
    assert result.loc["revenue_growth", 2023] == pytest.approx(1)
    assert result.loc["revenue_growth", 2024] == pytest.approx(0.5)

    # Gross margin = GrossProfit / TotalRevenue
    assert result.loc["gross_margin", 2022] == pytest.approx(0.4)
    assert result.loc["gross_margin", 2023] == pytest.approx(0.5)
    assert result.loc["gross_margin", 2024] == pytest.approx(0.6)

    # Operating margin = OperatingIncome / TotalRevenue
    assert result.loc["operating_margin", 2022] == pytest.approx(0.2)
    assert result.loc["operating_margin", 2023] == pytest.approx(0.25)
    assert result.loc["operating_margin", 2024] == pytest.approx(0.3)

    # Net margin = NetIncome / TotalRevenue
    assert result.loc["net_margin", 2022] == pytest.approx(0.1)
    assert result.loc["net_margin", 2023] == pytest.approx(0.2)
    assert result.loc["net_margin", 2024] == pytest.approx(0.2)

    # Free cash flow
    assert result.loc["free_cash_flow", 2022] == pytest.approx(20)
    assert result.loc["free_cash_flow", 2023] == pytest.approx(50)
    assert result.loc["free_cash_flow", 2024] == pytest.approx(80)

    # FCF margin = FreeCashFlow / TotalRevenue
    assert result.loc["fcf_margin", 2022] == pytest.approx(0.2)
    assert result.loc["fcf_margin", 2023] == pytest.approx(0.25)
    assert result.loc["fcf_margin", 2024] == pytest.approx(80/300)


def test_calculate_all_metrics_shape():
    income_statement = make_income_statement()
    cash_flow = make_cash_flow()
    balance_sheet = pd.DataFrame()

    result = calculate_all_metrics(income_statement, cash_flow, balance_sheet)

    assert result.index.name == "metric"
    assert result.columns.name == "year"

    assert "gross_margin" in result.index
    assert "free_cash_flow" in result.index

    assert 2024 in result.columns
    assert 2023 in result.columns
    assert 2022 in result.columns