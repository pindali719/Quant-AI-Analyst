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