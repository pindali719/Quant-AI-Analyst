import pytest
import pandas as pd

import app.analysis.dcf as dcf


def test_discount_cash_flows():

    cash_flows= [3.0, 2.0, 5.0, 3.0]
    discount_rate=0.15

    discounted_cash_flows = dcf.discount_cash_flows(cash_flows=cash_flows, discount_rate= discount_rate)

    assert discounted_cash_flows == [
        pytest.approx(expected= 2.6, abs= 0.01),
        pytest.approx(expected= 1.5, abs= 0.02),
        pytest.approx(expected=3.2, abs= 0.09),
        pytest.approx(expected=1.7, abs= 0.02)]
    
def test_calculate_terminal_value():

    final_year_fcf = 5.0
    discount_rate = 0.1
    terminal_growth = 0.05

    terminal_value = dcf.calculate_terminal_value(final_year_fcf= final_year_fcf, discount_rate= discount_rate, terminal_growth= terminal_growth)

    assert terminal_value == pytest.approx(105)

def test_fair_value_per_share():

    equity_value = 1000
    shares_outstanding = 100

    result = dcf.calculate_fair_value_per_share(
        equity_value=equity_value,
        shares_outstanding=shares_outstanding,
    )

    assert result == pytest.approx(10.0)


def test_dcf_sensitivity_table_shape():
    """
    Checks that the sensitivity table has the correct rows and columns.

    Rows should be discount rates.
    Columns should be terminal growth rates.
    """

    base_fcf = 100
    shares_outstanding = 10
    discount_rates = [0.08, 0.09, 0.10]
    terminal_growth_rates = [0.02, 0.03]

    result = dcf.create_dcf_sensitivity_table(
        base_fcf=base_fcf,
        shares_outstanding=shares_outstanding,
        discount_rates=discount_rates,
        terminal_growth_rates=terminal_growth_rates,
    )

    assert isinstance(result, pd.DataFrame)

    assert result.shape == (3, 2)

    assert list(result.index) == ["8.0%", "9.0%", "10.0%"]
    assert list(result.columns) == ["2.0%", "3.0%"]