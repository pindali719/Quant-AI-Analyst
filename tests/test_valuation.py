import pytest

from app.analysis.valuation import (
    calculate_pe_ratio,
    calculate_price_to_sales,
    calculate_fcf_yield,
)


def test_calculate_pe_ratio():
    market_cap = 1000
    net_income = 100

    result = calculate_pe_ratio(market_cap, net_income)

    assert result == 10


def test_calculate_price_to_sales():
    market_cap = 1000
    revenue = 250

    result = calculate_price_to_sales(market_cap, revenue)

    assert result == 4


def test_calculate_fcf_yield():
    free_cash_flow = 50
    market_cap = 1000

    result = calculate_fcf_yield(free_cash_flow, market_cap)

    assert result == pytest.approx(0.05)