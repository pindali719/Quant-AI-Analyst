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
    diluted_average_shares = 500


    result_1 = dcf.calculate_fair_value_per_share(
        equity_value=equity_value,
        shares_outstanding=shares_outstanding,
        diluted_average_shares= None
    )

    result_2 = dcf.calculate_fair_value_per_share(
        equity_value=equity_value,
        shares_outstanding=shares_outstanding,
        diluted_average_shares= diluted_average_shares
    )

    assert result_1 == pytest.approx(10.0)
    assert result_2 == pytest.approx(2.0)

def generate_dcf_sensitivity_table_content_arguments():
        
    projected_fcf = [
        105.0,
        110.25,
        115.7625,
        121.550625,
        127.62815625,
    ]

    cash = 20.0
    debt = 10.0

    shares_outstanding = 10.0
    diluted_average_shares = 12.0

    discount_rates = [0.10]
    terminal_growth_rates = [0.03]

    return {
        "projected_fcf": projected_fcf,
        "cash": cash,
        "debt": debt,
        "shares_outstanding": shares_outstanding,
        "diluted_average_shares": diluted_average_shares,
        "discount_rates": discount_rates,
        "terminal_growth_rates": terminal_growth_rates,
    }

def test_dcf_sensitivity_table_content():
    """
    Check that the DCF sensitivity table calculates the correct
    equity fair value per diluted share for one discount rate and
    one terminal growth rate.
    """

    arguments = generate_dcf_sensitivity_table_content_arguments()

    projected_fcf = arguments.get("projected_fcf")
    cash = arguments.get("cash")
    debt = arguments.get("debt")
    shares_outstanding = arguments.get("shares_outstanding")
    diluted_average_shares = arguments.get("diluted_average_shares")
    discount_rates = arguments.get("discount_rates")
    terminal_growth_rates = arguments.get("terminal_growth_rates")

    result = dcf.create_dcf_sensitivity_table(
        projected_fcf=projected_fcf,
        cash=cash,
        debt=debt,
        shares_outstanding=shares_outstanding,
        diluted_average_shares=diluted_average_shares,
        discount_rates=discount_rates,
        terminal_growth_rates=terminal_growth_rates,
    )

    # Present value of the five projected cash flows.
    expected_discounted_fcf = sum(
        cash_flow / ((1 + 0.10) ** year)
        for year, cash_flow in enumerate(
            projected_fcf,
            start=1,
        )
    )

    # Gordon Growth terminal value at the end of year 5.
    expected_terminal_value = (
        projected_fcf[-1]
        * (1 + 0.03)
        / (0.10 - 0.03)
    )

    expected_discounted_terminal_value = (
        expected_terminal_value
        / ((1 + 0.10) ** len(projected_fcf))
    )

    expected_enterprise_value = (
        expected_discounted_fcf
        + expected_discounted_terminal_value
    )

    expected_equity_value = (
        expected_enterprise_value
        + cash
        - debt
    )

    # Diluted average shares should be preferred over ordinary
    # shares outstanding when available.
    expected_fair_value_per_share = (
        expected_equity_value
        / diluted_average_shares
    )

    assert result.loc[
        "10.0%",
        "3.0%",
    ] == pytest.approx(
        expected_fair_value_per_share
    )





def test_dcf_sensitivity_table_shape():
    """
    Check that each discount rate creates one row and each
    terminal growth rate creates one column.
    """

    arguments = generate_dcf_sensitivity_table_content_arguments()

    arguments["discount_rates"] = [
        0.08,
        0.09,
        0.10,
    ]

    arguments["terminal_growth_rates"] = [
        0.02,
        0.03,
    ]

    result = dcf.create_dcf_sensitivity_table(
        projected_fcf=arguments["projected_fcf"],
        cash=arguments["cash"],
        debt=arguments["debt"],
        shares_outstanding=arguments["shares_outstanding"],
        diluted_average_shares=arguments[
            "diluted_average_shares"
        ],
        discount_rates=arguments["discount_rates"],
        terminal_growth_rates=arguments[
            "terminal_growth_rates"
        ],
    )

    assert isinstance(result, pd.DataFrame)

    assert result.shape == (3, 2)

    assert result.index.tolist() == [
        "8.0%",
        "9.0%",
        "10.0%",
    ]

    assert result.columns.tolist() == [
        "2.0%",
        "3.0%",
    ]