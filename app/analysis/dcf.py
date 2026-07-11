
import pandas as pd
from app.analysis.metrics import calculate_fcf_margin

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

def calculate_equity_value(enterprise_value: float, cash: float, debt: float) -> float:

    equity_value =  enterprise_value + cash - debt

    return equity_value

def calculate_fair_value_per_share(equity_value: float, shares_outstanding: float) -> float:

    fair_value_per_share = equity_value / shares_outstanding

    return fair_value_per_share


def create_dcf_sensitivity_table(
    base_fcf: float,
    shares_outstanding: float,
    discount_rates: list[float],
    terminal_growth_rates: list[float],
) -> pd.DataFrame:
    """
    Create a DCF sensitivity table.

    Rows = discount rates
    Columns = terminal growth rates
    Values = fair value per share
    """

    projection_years = 5
    fcf_growth_rate = 0.05

#############################################################
    #Creates sensitivity table

    row_labels = []

    for rate in discount_rates:
        percentage_value = rate * 100
        label = str(round(percentage_value, 1)) + "%"
        row_labels.append(label)


    column_labels = []

    for growth in terminal_growth_rates:
        percentage_value = growth * 100
        label = str(round(percentage_value, 1)) + "%"
        column_labels.append(label)


    table = pd.DataFrame(
        index=row_labels,
        columns=column_labels,
    )

    #########################################################

    #Fill the table
    
    for discount_rate in discount_rates:
        for terminal_growth in terminal_growth_rates:

            # Avoid invalid DCF formula
            if discount_rate <= terminal_growth:
                fair_value_per_share = None

            else:
                projected_fcf = []

                current_fcf = base_fcf


                for _ in range(projection_years):
                    current_fcf = current_fcf * (1 + fcf_growth_rate)
                    projected_fcf.append(current_fcf)

                discounted_fcf = discount_cash_flows(
                    cash_flows=projected_fcf,
                    discount_rate=discount_rate,
                )

                terminal_value = calculate_terminal_value(
                    final_year_fcf=projected_fcf[-1],
                    discount_rate=discount_rate,
                    terminal_growth=terminal_growth,
                )

                discounted_terminal_value = terminal_value / (
                    (1 + discount_rate) ** projection_years
                )

                enterprise_value = sum(discounted_fcf) + discounted_terminal_value

                fair_value_per_share = calculate_fair_value_per_share(
                    equity_value=enterprise_value,
                    shares_outstanding=shares_outstanding,
                )
            

            table.loc[f"{discount_rate:.1%}", f"{terminal_growth:.1%}"] = fair_value_per_share

    return table

def run_dcf(financials, market_data, assumptions) -> dict:

    income_statement = financials["income_statement"]
    cash_flow= financials["cash_flow"]
    balance_sheet= financials["balance_sheet"]

    growth_rates=assumptions["growth_rates"]
    discount_rate = assumptions["discount_rate"]
    terminal_growth = assumptions["terminal_growth"]

    enterprise_value= market_data["enterprise_value"]
    shares_outstanding = market_data["shares_outstanding"]
    

    latest_revenue = income_statement.loc["TotalRevenue"].dropna().iloc[0]
    latest_free_cash_flow = cash_flow.loc["FreeCashFlow"].dropna().iloc[0]
    cash=balance_sheet.loc["CashAndCashEquivalents"].dropna().iloc[0]
    debt=balance_sheet.loc["TotalDebt"].dropna().iloc[0]


    fcf_margin = latest_free_cash_flow/latest_revenue

    projected_revenue=project_revenue(latest_revenue=latest_revenue, growth_rates= growth_rates)

    projected_fcf= project_fcf_from_margin(projected_revenue=projected_revenue, fcf_margin= fcf_margin)

    discounted_fcf=discount_cash_flows(cash_flows= projected_fcf, discount_rate= discount_rate)

    terminal_value= calculate_terminal_value(final_year_fcf= projected_fcf[-1], discount_rate= discount_rate, terminal_growth= terminal_growth)

    number_of_year = len(projected_fcf)

    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** number_of_year)

    equity_value = calculate_equity_value(enterprise_value= enterprise_value, cash= cash, debt= debt)

    fair_value_per_share = calculate_fair_value_per_share(equity_value=equity_value, shares_outstanding=shares_outstanding)

    dcf_sensitivity_table = create_dcf_sensitivity_table(
        base_fcf=latest_free_cash_flow,
        shares_outstanding=shares_outstanding,
        discount_rates= [0.08, 0.09, 0.10, 0.11, 0.12],
        terminal_growth_rates= [0.02, 0.025, 0.03, 0.035, 0.04]
    )

    #We only want fair_value_per_share, but the rest are important for the AI Agent to explain the results
    result ={
        "fair_value_per_share": fair_value_per_share,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "projected_revenue": projected_revenue,
        "projected_fcf": projected_fcf,
        "discounted_fcf": discounted_fcf,
        "terminal_value": terminal_value,
        "discounted_terminal_value": discounted_terminal_value,
        "assumptions": assumptions,
        "dcf_sensitivity_table": dcf_sensitivity_table
    }

    return result


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



