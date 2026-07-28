# DCF Methodology

## Overview

The DCF module is a prototype implementation of a five-year discounted cash-flow model.

Its purpose is to demonstrate how the application can:

1. take a company's latest financial values;
2. apply bear, base, and bull assumptions;
3. project revenue and free cash flow;
4. discount future cash flows;
5. estimate terminal value;
6. convert enterprise value to equity value;
7. estimate fair value per share;
8. display sensitivity to discount-rate and terminal-growth assumptions.

The model is still under development. The formulas below describe the intended approach, followed by notes on how the current code behaves.

Related documentation:

- [Architecture](architecture.md)
- [Data sources](data_sources.md)
- [Current limitations](limitations.md)
- [Roadmap](roadmap.md)

---

## Current inputs

The DCF receives two dictionaries.

### Financial statements

```python
financials = {
    "income_statement": income_statement,
    "balance_sheet": balance_sheet,
    "cash_flow": cash_flow,
}
```

### Market data

```python
market_data = {
    "current_price": current_price,
    "market_cap": market_cap,
    "enterprise_value": enterprise_value,
    "shares_outstanding": shares_outstanding,
}
```

The current model uses:

- latest annual revenue;
- latest annual free cash flow;
- latest annual cash;
- latest annual debt;
- current shares outstanding;
- an enterprise-value estimate derived from current market capitalisation and annual balance-sheet data.

---

## Scenario assumptions

Three scenarios are defined in `app/analysis/dcf.py`.

| Scenario | Revenue growth: years 1–5 | FCF margin stored in assumptions | Discount rate | Terminal growth |
|---|---|---:|---:|---:|
| Bear | 8%, 6%, 5%, 4%, 3% | 22% | 12% | 2% |
| Base | 15%, 12%, 10%, 8%, 5% | 28% | 10% | 3% |
| Bull | 22%, 18%, 14%, 10%, 8% | 34% | 9% | 3.5% |

These assumptions are manually selected prototype values.

They are not:

- analyst-consensus forecasts;
- management guidance;
- automatically estimated from history;
- company-specific;
- sector-specific.

All three scenarios are calculated, after which the user selects one in the terminal.

---

## Intended valuation process

### 1. Revenue projection

For each forecast year:

\[
Revenue_t = Revenue_{t-1}(1+g_t)
\]

where \(g_t\) is the selected revenue-growth assumption.

### 2. Free-cash-flow projection

The intended scenario-based calculation is:

\[
FCF_t = Revenue_t \times FCFMargin
\]

### 3. Forecast cash-flow discounting

\[
PV(FCF_t) =
\frac{FCF_t}{(1+r)^t}
\]

where \(r\) is the discount rate.

### 4. Terminal value

The model uses the Gordon Growth formula:

\[
TerminalValue =
\frac{FCF_5(1+g)}{r-g}
\]

where:

- \(FCF_5\) is free cash flow in the fifth forecast year;
- \(g\) is terminal growth;
- \(r\) is the discount rate.

A valid model requires:

\[
r > g
\]

### 5. Discounted terminal value

\[
PV(TerminalValue) =
\frac{TerminalValue}{(1+r)^5}
\]

### 6. DCF enterprise value

\[
EnterpriseValue_{DCF} =
\sum_{t=1}^{5}PV(FCF_t)
+
PV(TerminalValue)
\]

### 7. Equity value

\[
EquityValue =
EnterpriseValue_{DCF} + Cash - Debt
\]

### 8. Fair value per share

\[
FairValuePerShare =
\frac{EquityValue}{SharesOutstanding}
\]

This is the intended end-to-end DCF calculation.

---

## Current prototype behaviour

The module already projects and discounts future cash flows, but two parts of the current integration are still being refined.

### Historical FCF margin is currently used

`run_dcf()` currently calculates:

\[
HistoricalFCFMargin =
\frac{LatestAnnualFCF}{LatestAnnualRevenue}
\]

Projected free cash flow is then:

\[
ProjectedFCF_t =
ProjectedRevenue_t \times HistoricalFCFMargin
\]

Although each scenario stores an `fcf_margin`, that assumption is not yet used by `run_dcf()`.

This means the bear, base, and bull FCF-margin values are currently descriptive rather than active model inputs.

### Headline enterprise value is not yet generated from discounted forecast cash flows

The module calculates:

- projected revenue;
- projected FCF;
- discounted FCF;
- terminal value;
- discounted terminal value.

However, the current headline equity value is calculated from the enterprise value already supplied through `market_data`:

\[
EquityValue_{current} =
MarketEnterpriseValue + Cash - Debt
\]

The intended calculation is:

\[
EnterpriseValue_{DCF} =
\sum DiscountedFCF + DiscountedTerminalValue
\]

followed by:

\[
EquityValue =
EnterpriseValue_{DCF} + Cash - Debt
\]

Connecting this final step is an immediate development priority.

---

## Sensitivity table

The current sensitivity function evaluates combinations of:

```python
discount_rates = [0.08, 0.09, 0.10, 0.11, 0.12]

terminal_growth_rates = [
    0.02,
    0.025,
    0.03,
    0.035,
    0.04,
]
```

Rows represent discount rates and columns represent terminal-growth rates.

### Current sensitivity calculation

For each valid pair \((r,g)\), the function:

1. starts with latest annual free cash flow;
2. grows FCF by a fixed 5% per year for five years;
3. discounts the five projected cash flows;
4. calculates terminal value;
5. discounts terminal value;
6. sums both components;
7. divides by shares outstanding.

The calculation is approximately:

\[
ValuePerShare =
\frac{
\sum_{t=1}^{5}
\frac{FCF_0(1.05)^t}{(1+r)^t}
+
\frac{FCF_5(1+g)}{(r-g)(1+r)^5}
}{
SharesOutstanding
}
\]

Cells where \(r \leq g\) are returned as unavailable.

### Sensitivity-table constraints

The current table:

- uses fixed 5% FCF growth rather than the selected scenario;
- does not add cash;
- does not subtract debt;
- treats the calculated enterprise value as equity value;
- is not generated from the same projected FCF values as the selected scenario.

It is therefore a useful prototype visualisation, but it is not yet fully consistent with the intended headline DCF methodology.

---

## Recommended implementation alignment

The main DCF should calculate:

```python
enterprise_value = (
    sum(discounted_fcf)
    + discounted_terminal_value
)

equity_value = (
    enterprise_value
    + cash
    - debt
)

fair_value_per_share = (
    equity_value
    / shares_outstanding
)
```

It should also read:

```python
fcf_margin = assumptions["fcf_margin"]
```

The sensitivity table should use the same:

- forecast structure;
- cash value;
- debt value;
- share count;
- equity-value bridge.

That will make the headline valuation, selected scenario, and sensitivity table methodologically consistent.

---

## Share-count convention

The current model uses:

```python
company_info["sharesOutstanding"]
```

This is a practical fallback for the prototype.

A later version should prefer a diluted share count when a reliable recent diluted value is available, because options, restricted shares, and other instruments can increase the effective share base.

The selected share-count date should be recorded with the report.

---

## Interpretation

The DCF output should be read as a **scenario estimate**, not as a precise target price.

The result is highly sensitive to:

- revenue growth;
- FCF margin;
- discount rate;
- terminal growth;
- cash and debt;
- share count.

The terminal value can represent a large portion of enterprise value. For that reason, the sensitivity table and explicit assumptions are as important as the headline fair-value estimate.

---

## Current model limitations

The DCF does not yet model:

- separate revenue segments;
- operating expenses independently;
- working-capital investment;
- depreciation;
- capital expenditure independently;
- stock-based compensation;
- acquisitions;
- changes in debt and cash during the forecast;
- probability-weighted scenarios;
- analyst estimates;
- a company-specific cost of capital;
- sector-specific terminal assumptions.

It is intentionally a transparent prototype rather than a complete institutional valuation model.
