import pandas as pd

def latest_value(value):
    """
    If value is a pandas Series, return the latest non-missing value.
    If value is already a single number, return it unchanged.
    """

    # Check: is this a pandas Series?
    if isinstance(value, pd.Series):

        # Remove missing values like NaN or None
        value = value.dropna()

        # If after removing missing values there is nothing left, return None
        if value.empty:
            return None

        # Sort by date/year index and return the last value
        return value.sort_index().iloc[-1]

    # If it was not a Series, just return it as it is
    return value

def safe_division(numerator: float, denominator: float):

    """Divide two numbers while validating the denominator."""

    if denominator == 0:
        raise ZeroDivisionError("Denominator cannot be zero.")
    if denominator == None:
        raise ValueError("Denominator cannot be None")
    if numerator == None:
        raise ValueError("Numerator cannot be None")
    
    
    return numerator/denominator

def ttm_value(
    statement: pd.DataFrame,
    row_name: str,
) -> float | None:
    """
    Sum the latest four available quarterly values.

    Use this only for flow measures such as revenue,
    net income, EBITDA, and free cash flow.
    """

    if row_name not in statement.index:
        return None

    values = pd.to_numeric(
        statement.loc[row_name],
        errors="coerce",
    ).dropna()

    if len(values) < 4:
        return None

    # Statement columns contain reporting dates.
    values = values.sort_index(ascending=False)

    return float(values.iloc[:4].sum())

def is_missing(value) -> bool:
    """Return True when a scalar value is missing."""

    return value is None or pd.isna(value)


def ratio_or_none(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    """
    Divide two values when both are available and the denominator
    is positive.

    A negative numerator is allowed. This is important for margins,
    ROE, and ROIC when the company is loss-making.
    """

    if is_missing(numerator) or is_missing(denominator):
        return None

    if denominator <= 0:
        return None

    return float(numerator / denominator)


def latest_statement_value(
    statement: pd.DataFrame,
    row_name: str,
) -> float | None:
    """Return the latest available value from a statement row."""

    if row_name not in statement.index:
        return None

    return latest_value(statement.loc[row_name])