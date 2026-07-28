# Data Sources

## Overview

The current Quant AI Analyst prototype uses **Yahoo Finance through the `yfinance` Python package** as its active external data source.

The repository includes placeholders for SEC filing retrieval and recent-news analysis, but those integrations are not yet implemented.

Related documentation:

- [Architecture](architecture.md)
- [DCF methodology](dcf_methodology.md)
- [Current limitations](limitations.md)
- [Roadmap](roadmap.md)

---

## Active provider

### Yahoo Finance through `yfinance`

The application creates a `yfinance.Ticker` object for the requested symbol and retrieves financial statements, company metadata, and historical prices.

Current dependency:

```text
yfinance
```

No API key is currently required.

---

## Retrieved data

### Annual income statement

Retrieved with:

```python
ticker.get_income_stmt(freq="yearly")
```

The prototype keeps the following rows:

| Yahoo Finance field | Current use |
|---|---|
| `TotalRevenue` | Revenue growth, margins, P/S, and DCF starting revenue |
| `GrossProfit` | Gross margin |
| `OperatingIncome` | Operating margin and approximate NOPAT |
| `NetIncome` | Net margin, P/E, and ROE |
| `PretaxIncome` | Effective tax-rate estimate |
| `TaxProvision` | Effective tax-rate estimate |
| `EBITDA` | EV/EBITDA |

### Annual balance sheet

Retrieved with:

```python
ticker.get_balance_sheet(freq="yearly")
```

The prototype keeps:

| Yahoo Finance field | Current use |
|---|---|
| `TotalAssets` | Retrieved for possible future analysis |
| `TotalLiabilitiesNetMinorityInterest` | Retrieved for possible future analysis |
| `StockholdersEquity` | Leverage and ROE |
| `TotalDebt` | Enterprise value, leverage, ROIC, and DCF equity bridge |
| `CashAndCashEquivalents` | Enterprise value, ROIC, and DCF equity bridge |
| `CurrentAssets` | Current ratio |
| `CurrentLiabilities` | Current ratio |

### Annual cash-flow statement

Retrieved with:

```python
ticker.get_cash_flow(freq="yearly")
```

The prototype keeps:

| Yahoo Finance field | Current use |
|---|---|
| `OperatingCashFlow` | Available for cash-flow analysis |
| `CapitalExpenditure` | Available for cash-flow analysis |
| `FreeCashFlow` | FCF trend, FCF margin, FCF yield, and DCF input |
| `CashDividendsPaid` | Retrieved but not yet analysed |
| `RepurchaseOfCapitalStock` | Retrieved but not yet analysed |

### Company and market information

Retrieved with:

```python
ticker.get_info()
```

Selected fields include:

| Field | Current use |
|---|---|
| `longBusinessSummary` | Retrieved for a future business overview |
| `sector` | Report metadata |
| `industry` | Report metadata |
| `marketCap` | Valuation and peer comparison |
| `exchange` | Company metadata |
| `currency` | Report labels |
| `currentPrice` | DCF-upside score |
| `sharesOutstanding` | Fair value per share |
| `trailingPE` | Retrieved but not used by the current valuation functions |

The provider's `enterpriseValue` field is requested but replaced with an internally derived approximation.

### Historical prices

Retrieved with:

```python
ticker.history(period="5y", interval="1d")
```

The current pipeline validates that price history is available. It does not yet use the series in a stock-price chart or valuation calculation.

---

## Derived enterprise value

The current company-information function calculates:

\[
EnterpriseValue =
MarketCapitalisation + TotalDebt - Cash
\]

where debt and cash come from the latest available annual balance sheet.

This is a practical prototype approximation. It combines a current market value with annual accounting values, so the inputs are not perfectly date-aligned.

---

## Period convention

The current implementation is based mainly on **annual financial statements**.

| Output | Current period basis |
|---|---|
| Revenue growth | Annual |
| Gross, operating, and net margins | Annual |
| Free cash flow and FCF margin | Annual |
| P/E | Current market capitalisation / latest annual net income |
| P/S | Current market capitalisation / latest annual revenue |
| FCF yield | Latest annual FCF / current market capitalisation |
| Peer comparison | Current market data and latest annual fundamentals |
| ROE and ROIC | Latest available annual values |
| DCF starting revenue and FCF | Latest available annual values |
| DCF cash and debt | Latest available annual balance-sheet values |
| Historical price data | Five years of daily observations |

The prototype does not currently calculate trailing-twelve-month values.

---

## Data preparation

### Row selection

Each financial statement is reindexed to a fixed list of expected rows.

This gives downstream modules a predictable structure, but rows not returned by Yahoo Finance remain missing.

### Latest-value selection

The helper `latest_value()`:

1. removes missing observations;
2. sorts a pandas Series by its index;
3. returns the final value.

For statement rows indexed by reporting dates, this is intended to return the most recent observation.

Some functions instead use `.iloc[0]` and rely on Yahoo Finance returning the newest period first. Standardising all modules on one explicit date-selection method is part of the roadmap.

### Year conversion

For reporting and charts, financial statement dates are converted into fiscal-year labels.

### Missing data

Current behaviour depends on the module:

- an entirely empty statement raises `ValueError`;
- unavailable rows remain `NaN`;
- some formulas propagate missing values;
- `safe_division()` rejects `None` and zero denominators;
- peer-data errors can currently stop the full peer-comparison stage.

A consistent missing-data policy has not yet been implemented.

---

## Currency handling

The application retrieves the company's reported `currency` and displays it in the generated report.

It does not currently:

- convert currencies;
- validate that peers use the same currency;
- distinguish trading currency from financial-statement currency;
- adjust historical amounts for foreign-exchange movements.

Ratios may still be useful, but absolute values should not be assumed to be directly comparable across companies reporting in different currencies.

---

## Data freshness and reproducibility

A run uses the data Yahoo Finance returns at execution time.

The prototype does not yet save:

- retrieval timestamps;
- raw API responses;
- provider-version information;
- source URLs;
- the exact statement dates used;
- a Git commit hash for the run;
- cached financial snapshots.

This means that results can change between runs even when the source code is unchanged.

A future metadata file could record:

```yaml
ticker: NVDA
retrieved_at: 2026-07-28T17:00:00Z
provider: Yahoo Finance via yfinance
pipeline_commit: <commit-hash>
statement_dates:
  income_statement: [...]
  balance_sheet: [...]
  cash_flow: [...]
peer_group: [...]
dcf_scenario: base
```

---

## Error behaviour

The retrieval layer raises an error if Yahoo Finance returns no:

- income statement;
- balance sheet;
- cash-flow statement;
- historical price data.

In peer analysis, the current code prints an error for an unavailable company and then re-raises the exception. Therefore, one failed peer can currently stop the complete peer-analysis stage.

---

## Planned data sources

### SEC EDGAR

Planned uses:

- retrieve company submissions;
- retrieve recent 10-K and 10-Q filings;
- extract business descriptions;
- extract risk factors;
- extract management discussion and analysis;
- attach filing links to report claims.

Status: **not implemented**.

### Recent news

Planned uses:

- retrieve company-specific news;
- remove duplicate articles;
- group articles into themes;
- identify possible risks and catalysts;
- preserve titles, dates, publishers, and links.

Status: **not implemented**.

### Company investor-relations pages

Possible future uses:

- annual reports;
- earnings releases;
- investor presentations;
- management guidance.

Status: **not implemented**.

### Alternative financial-data providers

Possible reasons to add a second provider:

- more stable field definitions;
- stronger international coverage;
- point-in-time fundamentals;
- analyst estimates;
- more reliable corporate-action handling;
- provider cross-checks.

Status: **not implemented**.

---

## Data-use statement

The current data layer is suitable for a prototype and portfolio demonstration. It should not be treated as an audited, point-in-time, or institution-grade financial database.

Important figures should be checked against company filings or another authoritative source before they are used outside the prototype.
