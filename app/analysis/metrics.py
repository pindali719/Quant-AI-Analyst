import pandas as pd

from numbers import Integral



def _period_to_year(period) -> int:
    """
    Convert a statement column into an integer fiscal year.

    Supports:
    - pandas timestamps;
    - date strings;
    - integer years.
    """

    if isinstance(period, Integral):
        return int(period)

    parsed_period = pd.to_datetime(
        period,
        errors="raise",
    )

    return int(parsed_period.year)


def _normalize_annual_statement(
    statement: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return a copy of an annual statement with fiscal-year columns
    ordered from oldest to newest.
    """

    if statement is None or statement.empty:
        return pd.DataFrame()

    normalized = statement.copy()

    normalized.columns = [
        _period_to_year(column)
        for column in normalized.columns
    ]

    if normalized.columns.duplicated().any():
        raise ValueError(
            "The annual statement contains more than one "
            "column for the same fiscal year."
        )

    return normalized.sort_index(
        axis=1,
        ascending=True,
    )


def _numeric_row(
    statement: pd.DataFrame,
    row_name: str,
) -> pd.Series:
    """
    Read one statement row as numeric values while preserving years.
    """

    if row_name not in statement.index:
        return pd.Series(
            dtype=float,
            name=row_name,
        )

    row = pd.to_numeric(
        statement.loc[row_name],
        errors="coerce",
    )

    row.name = row_name

    return row.sort_index()


def _divide_series(
    numerator: pd.Series,
    denominator: pd.Series,
    require_positive_denominator: bool = True,
) -> pd.Series:
    """
    Align and divide two financial Series.

    Invalid denominators become NaN.
    """

    numerator, denominator = numerator.align(
        denominator,
        join="inner",
    )

    if require_positive_denominator:
        denominator = denominator.where(
            denominator > 0
        )
    else:
        denominator = denominator.where(
            denominator != 0
        )

    return numerator / denominator



def calculate_revenue_growth(
    income_statement: pd.DataFrame,
) -> pd.Series:

    income_statement = _normalize_annual_statement(
        income_statement
    )

    revenue = _numeric_row(
        income_statement,
        "TotalRevenue",
    )

    return revenue.pct_change()

def calculate_gross_margin(
    income_statement: pd.DataFrame,
) -> pd.Series:

    income_statement = _normalize_annual_statement(
        income_statement
    )

    return _divide_series(
        numerator=_numeric_row(
            income_statement,
            "GrossProfit",
        ),
        denominator=_numeric_row(
            income_statement,
            "TotalRevenue",
        ),
    )

def calculate_operating_margin(
    income_statement: pd.DataFrame,
) -> pd.Series:

    income_statement = _normalize_annual_statement(
        income_statement
    )

    return _divide_series(
        numerator=_numeric_row(
            income_statement,
            "OperatingIncome",
        ),
        denominator=_numeric_row(
            income_statement,
            "TotalRevenue",
        ),
    )


def calculate_net_margin(
    income_statement: pd.DataFrame,
) -> pd.Series:

    income_statement = _normalize_annual_statement(
        income_statement
    )

    return _divide_series(
        numerator=_numeric_row(
            income_statement,
            "NetIncome",
        ),
        denominator=_numeric_row(
            income_statement,
            "TotalRevenue",
        ),
    )

#You can directly get free_cash_flow from cash_flow. This function is only for consistency
def calculate_free_cash_flow(
    cash_flow: pd.DataFrame,
) -> pd.Series:
    """
    Calculate free cash flow independently.

    Yahoo normally represents capital expenditure as a negative
    cash outflow, so:

        FCF = Operating Cash Flow + Capital Expenditure
    """

    cash_flow = _normalize_annual_statement(
        cash_flow
    )

    operating_cash_flow = _numeric_row(
        cash_flow,
        "OperatingCashFlow",
    )

    capital_expenditure = _numeric_row(
        cash_flow,
        "CapitalExpenditure",
    )

    operating_cash_flow, capital_expenditure = (
        operating_cash_flow.align(
            capital_expenditure,
            join="inner",
        )
    )

    return (
        operating_cash_flow
        + capital_expenditure
    )

def calculate_fcf_margin(
    cash_flow: pd.DataFrame,
    income_statement: pd.DataFrame,
) -> pd.Series:

    free_cash_flow = calculate_free_cash_flow(
        cash_flow
    )

    income_statement = _normalize_annual_statement(
        income_statement
    )

    revenue = _numeric_row(
        income_statement,
        "TotalRevenue",
    )

    return _divide_series(
        numerator=free_cash_flow,
        denominator=revenue,
    )

def calculate_current_ratio(
    balance_sheet: pd.DataFrame,
) -> pd.Series:

    balance_sheet = _normalize_annual_statement(
        balance_sheet
    )

    return _divide_series(
        numerator=_numeric_row(
            balance_sheet,
            "CurrentAssets",
        ),
        denominator=_numeric_row(
            balance_sheet,
            "CurrentLiabilities",
        ),
    )

def calculate_debt_to_equity(
    balance_sheet: pd.DataFrame,
) -> pd.Series:

    balance_sheet = _normalize_annual_statement(
        balance_sheet
    )

    return _divide_series(
        numerator=_numeric_row(
            balance_sheet,
            "TotalDebt",
        ),
        denominator=_numeric_row(
            balance_sheet,
            "StockholdersEquity",
        ),
    )

def calculate_all_metrics(income_statement: pd.DataFrame, cash_flow: pd.DataFrame, balance_sheet: pd.DataFrame) -> pd.DataFrame:

    revenue_growth= calculate_revenue_growth(income_statement)
    gross_margin=calculate_gross_margin(income_statement)
    operating_margin=calculate_operating_margin(income_statement)
    net_margin=calculate_net_margin(income_statement)

    free_cash_flow=calculate_free_cash_flow(cash_flow)

    fcf_margin=calculate_fcf_margin(cash_flow, income_statement)

    metric_series = {
        "revenue_growth": revenue_growth,
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "free_cash_flow": free_cash_flow,
        "fcf_margin": fcf_margin
        }
    if (
        balance_sheet is not None
        and not balance_sheet.empty
    ):
        metric_series.update(
            {
                "current_ratio":
                    calculate_current_ratio(
                        balance_sheet
                    ),
                "debt_to_equity":
                    calculate_debt_to_equity(
                        balance_sheet
                    ),

            }
        )

    all_metrics = pd.DataFrame(
        metric_series
    ).T

    all_metrics = all_metrics.sort_index(
        axis=1,
        ascending=False,
    )

    all_metrics.index.name = "metric"
    all_metrics.columns.name = "year"


    return  all_metrics