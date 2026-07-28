
import pandas as pd
from app.analysis.metrics import calculate_fcf_margin
from app.helpers import latest_value, ttm_value

def project_revenue(latest_revenue: float, growth_rates: list[float]) -> list[float]:

    projected_revenue=[]

    for i in range(len(growth_rates)):
        latest_revenue=latest_revenue*(1 + growth_rates[i])
        projected_revenue.append(latest_revenue)

    return projected_revenue

def project_fcf_from_margin(projected_revenue: list[float], fcf_margin: float) -> list[float]:

    projected_fcf=[]

    for revenue in projected_revenue:
        projected_fcf.append(revenue*fcf_margin)

    return projected_fcf

def discount_cash_flows(cash_flows: list[float], discount_rate: float) -> list[float]:

    list_of_discount_cash_flows=[]

    year=1

    for cash_flow in cash_flows:

        present_value = cash_flow/(1+discount_rate)**(year)

        list_of_discount_cash_flows.append(present_value)

        year+=1
    
    return list_of_discount_cash_flows

def calculate_terminal_value(final_year_fcf: float, discount_rate: float, terminal_growth: float) -> float:

    terminal_value = final_year_fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)

    return terminal_value

def calculate_enterprise_value(discounted_fcf: list[float], discounted_terminal_value: float) -> float:

    enterprise_value = sum(discounted_fcf) + discounted_terminal_value

    return enterprise_value

def calculate_equity_value(enterprise_value: float, cash: float, debt: float) -> float:

    equity_value =  enterprise_value + cash - debt

    return equity_value

def calculate_fair_value_per_share(equity_value: float, shares_outstanding: float, diluted_average_shares) -> float:

    if diluted_average_shares == None:
        return equity_value / shares_outstanding

    return equity_value / diluted_average_shares


def create_dcf_sensitivity_table(
    projected_fcf: list[float],
    cash: float,
    debt: float,
    shares_outstanding: float,
    diluted_average_shares: float | None,
    discount_rates: list[float],
    terminal_growth_rates: list[float],
) -> pd.DataFrame:
    """
    Create a DCF sensitivity table.

    Rows:
        Discount rates.

    Columns:
        Terminal growth rates.

    Values:
        Equity fair value per share.

    The operating forecast remains constant. Only the discount
    rate and terminal growth rate change between table cells.
    """

    if not projected_fcf:
        raise ValueError("projected_fcf cannot be empty.")

    projection_years = len(projected_fcf)

    row_labels = [
        f"{discount_rate:.1%}"
        for discount_rate in discount_rates
    ]

    column_labels = [
        f"{terminal_growth:.1%}"
        for terminal_growth in terminal_growth_rates
    ]

    table = pd.DataFrame(
        index=row_labels,
        columns=column_labels,
        dtype=float,
    )

    for discount_rate in discount_rates:
        for terminal_growth in terminal_growth_rates:

            row_label = f"{discount_rate:.1%}"
            column_label = f"{terminal_growth:.1%}"

            # Gordon Growth formula is invalid when r <= g.
            if discount_rate <= terminal_growth:
                table.loc[row_label, column_label] = float("nan")
                continue

            discounted_fcf = discount_cash_flows(
                cash_flows=projected_fcf,
                discount_rate=discount_rate,
            )

            terminal_value = calculate_terminal_value(
                final_year_fcf=projected_fcf[-1],
                discount_rate=discount_rate,
                terminal_growth=terminal_growth,
            )

            discounted_terminal_value = (
                terminal_value
                / ((1 + discount_rate) ** projection_years)
            )

            enterprise_value = calculate_enterprise_value(
                discounted_fcf=discounted_fcf,
                discounted_terminal_value=discounted_terminal_value,
            )

            equity_value = calculate_equity_value(
                enterprise_value=enterprise_value,
                cash=cash,
                debt=debt,
            )

            fair_value_per_share = calculate_fair_value_per_share(
                equity_value=equity_value,
                shares_outstanding=shares_outstanding,
                diluted_average_shares=diluted_average_shares,
            )

            table.loc[row_label, column_label] = fair_value_per_share

    return table

def run_dcf(
    financials,
    market_data,
    assumptions,
) -> dict:
    """
    Run a scenario-based discounted cash-flow valuation.

    Revenue is projected using the scenario growth rates.
    Free cash flow is projected using the scenario FCF margin.
    """

    quarterly_income_statement = financials["quarterly_income_statement"]
    quarterly_balance_sheet = financials["quarterly_balance_sheet"]

    growth_rates = assumptions["growth_rates"]
    discount_rate = assumptions["discount_rate"]
    terminal_growth = assumptions["terminal_growth"]
    fcf_margin = assumptions["fcf_margin"]

    if discount_rate <= terminal_growth:
        raise ValueError(
            "discount_rate must be greater than terminal_growth."
        )

    # Starting operating base: latest twelve months.
    latest_revenue = ttm_value(
        quarterly_income_statement,
        "TotalRevenue",
    )  

    if latest_revenue is None or latest_revenue <= 0:
        raise ValueError(
            "At least four valid quarterly revenue values are required."
        )

    # Equity-value bridge: latest balance-sheet snapshot.
    cash = latest_value(
        quarterly_balance_sheet.loc[
            "CashAndCashEquivalents"
        ]
    )

    debt = latest_value(
        quarterly_balance_sheet.loc["TotalDebt"]
    )

    shares_outstanding = market_data["shares_outstanding"]

    diluted_average_shares = latest_value(
        quarterly_income_statement.loc[
            "DilutedAverageShares"
        ]
    )

    projected_revenue = project_revenue(
        latest_revenue=latest_revenue,
        growth_rates=growth_rates,
    )

    projected_fcf = project_fcf_from_margin(
        projected_revenue=projected_revenue,
        fcf_margin=fcf_margin,
    )

    discounted_fcf = discount_cash_flows(
        cash_flows=projected_fcf,
        discount_rate=discount_rate,
    )

    terminal_value = calculate_terminal_value(
        final_year_fcf=projected_fcf[-1],
        discount_rate=discount_rate,
        terminal_growth=terminal_growth,
    )

    projection_years = len(projected_fcf)

    discounted_terminal_value = (
        terminal_value
        / ((1 + discount_rate) ** projection_years)
    )

    enterprise_value = calculate_enterprise_value(
        discounted_fcf=discounted_fcf,
        discounted_terminal_value=discounted_terminal_value,
    )

    equity_value = calculate_equity_value(
        enterprise_value=enterprise_value,
        cash=cash,
        debt=debt,
    )

    fair_value_per_share = calculate_fair_value_per_share(
        equity_value=equity_value,
        shares_outstanding=shares_outstanding,
        diluted_average_shares=diluted_average_shares,
    )

    dcf_sensitivity_table = create_dcf_sensitivity_table(
        projected_fcf=projected_fcf,
        cash=cash,
        debt=debt,
        shares_outstanding=shares_outstanding,
        diluted_average_shares=diluted_average_shares,
        discount_rates=[0.08, 0.09, 0.10, 0.11, 0.12],
        terminal_growth_rates=[0.02, 0.025, 0.03, 0.035, 0.04]
    )

    return {
        "fair_value_per_share": fair_value_per_share,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "projected_revenue": projected_revenue,
        "projected_fcf": projected_fcf,
        "discounted_fcf": discounted_fcf,
        "terminal_value": terminal_value,
        "discounted_terminal_value": discounted_terminal_value,
        "assumptions": assumptions,
        "dcf_sensitivity_table": dcf_sensitivity_table,
    }

def run_dcf_scenarios(financials: dict, market_data: dict) -> dict:
    """
    Run bear, base, and bull DCF scenarios.

    Each scenario uses different assumptions.
    The function returns a dictionary with one DCF result per scenario.
    """

    scenarios = {
        "bear": {
            "growth_rates": [0.08, 0.06, 0.05, 0.04, 0.03],
            "fcf_margin": 0.22,
            "discount_rate": 0.12,
            "terminal_growth": 0.02,
        },
        "base": {
            "growth_rates": [0.15, 0.12, 0.10, 0.08, 0.05],
            "fcf_margin": 0.28,
            "discount_rate": 0.10,
            "terminal_growth": 0.03,
        },
        "bull": {
            "growth_rates": [0.22, 0.18, 0.14, 0.10, 0.08],
            "fcf_margin": 0.34,
            "discount_rate": 0.09,
            "terminal_growth": 0.035,
        },
    }

    results = {}

    for scenario_name, assumptions in scenarios.items():
        results[scenario_name] = run_dcf(
            financials=financials,
            market_data=market_data,
            assumptions=assumptions,
        )

    return results

def enter_assumption():

    while True:
        try:
            print("--ASSUMPTIONS--\n1.bear\n2.base\n3.bull")
            type_of_assumption = int(input("\nWhat kind of assumption are you making?\nAnswer: "))
            if ( (type_of_assumption < 1) or (3 < type_of_assumption)):
                print("\nOut of range!!!")
            else:
                break

        except:
            print("Not valid input!!!")

    return type_of_assumption

def get_dcf_scenary_result(type_of_assumption: int, dcf_scenarios: dict) -> dict:

    #Convert from number to its name
    if type_of_assumption == 1:
        type_of_assumption = "bear"
    elif type_of_assumption == 2:
        type_of_assumption = "base"
    else:
        type_of_assumption = "bull"

    dcf_results= dcf_scenarios[type_of_assumption]

    return dcf_results






