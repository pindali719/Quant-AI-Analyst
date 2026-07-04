import pandas as pd

def calculate_revenue_growth(income_statement: pd.DataFrame) -> pd.Series:

    revenue=income_statement.loc["TotalRevenue"]

    revenue=revenue.sort_index()

    revenue_growths=revenue.pct_change()*100

    return revenue_growths

def calculate_gross_margin(income_statement: pd.DataFrame) -> pd.Series:

    gross_margins=[]

    for col in income_statement.columns:
        gross_margin=income_statement[col]["GrossProfit"]/income_statement[col]["TotalRevenue"]

        gross_margins.append(gross_margin)

    gross_margins=pd.Series(gross_margins)

    return gross_margins

def calculate_operating_margin(income_statement: pd.DataFrame) -> pd.Series:

    operating_margins=[]

    for col in income_statement.columns:
        operating_margin=income_statement[col]["OperatingIncome"]/income_statement[col]["TotalRevenue"]

        operating_margins.append(operating_margin)

    operating_margins=pd.Series(operating_margins)


    return operating_margins

def calculate_net_margin(income_statement: pd.DataFrame) -> pd.Series:

    net_margins=[]

    for col in income_statement.columns:
        net_margin=income_statement[col]["NetIncome"]/income_statement[col]["TotalRevenue"]

        net_margins.append(net_margin)

    net_margins=pd.Series(net_margins)


    return net_margins

#You can directly get free_cash_flow from cash_flow. This function is only for consistency
def calculate_free_cash_flow(cash_flow: pd.DataFrame) -> pd.Series:

    free_cash_flows=cash_flow.loc["FreeCashFlow"]


    return free_cash_flows

def calculate_fcf_margin(cash_flow: pd.DataFrame, income_statement: pd.DataFrame) -> pd.Series:

    fcf_margins=[]

    for col in cash_flow.columns:
        free_cash_flow=cash_flow[col]["OperatingCashFlow"]-cash_flow[col]["CapitalExpenditure"]

        fcf_margin=free_cash_flow/income_statement[col]["TotalRevenue"]

        fcf_margins.append(fcf_margin)

    fcf_margins=pd.Series(fcf_margins)


    return fcf_margins

def calculate_all_metrics(income_statement: pd.DataFrame, cash_flow: pd.DataFrame, balance_sheet: pd.DataFrame) -> pd.DataFrame:

    index=[]

    for date in income_statement.columns:
        index.append(date)

    revenue_growth= calculate_revenue_growth(income_statement)

    gross_margin=calculate_gross_margin(income_statement)

    operating_margin=calculate_operating_margin(income_statement)

    net_margin=calculate_net_margin(income_statement)

    free_cash_flow=calculate_free_cash_flow(cash_flow)

    fcf_margin=calculate_fcf_margin(cash_flow, income_statement)

    all_metrics= pd.DataFrame({
        "revenue_growth":revenue_growth,
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "free_cash_flow": free_cash_flow,
        "fcf_margin": fcf_margin
    
    }, index=index)

    return  all_metrics