

# Quant AI Analyst

[![Status](https://img.shields.io/badge/status-work%20in%20progress-orange)](#project-status)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#installation)

**Quant AI Analyst** is a research-oriented Python pipeline for equity analysis. It retrieves public-company financial data, calculates financial and valuation metrics, compares a company with selected peers, runs scenario-based discounted cash-flow valuations, generates charts, and produces a structured Markdown investment report.

The project is being built around a simple principle:

> Financial values should be calculated deterministically in Python.  
> Future AI components should explain and summarize evidence rather than invent numbers.

This repository is an active research prototype and is not intended to provide financial advice.

---

## Project status

The current version implements the core quantitative pipeline. Qualitative research components—such as SEC filing analysis, recent-news retrieval, and an LLM explanation layer—remain planned work.

| Component | Status |
|---|---|
| Annual and quarterly financial-data retrieval | Implemented |
| Historical financial metrics | Implemented |
| TTM valuation metrics | Implemented |
| Bear, base, and bull DCF scenarios | Implemented |
| DCF sensitivity analysis | Implemented |
| Peer comparison | Implemented for configured peer groups |
| Transparent weighted scorecard | Implemented |
| Financial charts | Implemented |
| Markdown investment report | Implemented |
| SEC filing retrieval and analysis | Planned |
| News retrieval and thematic analysis | Planned |
| LLM-supported explanations | Planned |
| Streamlit interface | Planned |
| PDF export | Planned |


Most implemented functionalities are also planned to be further improved.

---

## Research objective

Equity research combines data collection, financial modelling, comparison, interpretation, and reporting. This project explores how that workflow can be represented as a transparent and reproducible software pipeline.

The current implementation focuses on:

- separating data retrieval from financial calculations;
- aligning annual, trailing-twelve-month, and latest-quarter data appropriately;
- making DCF assumptions explicit;
- comparing companies using consistent metrics;
- handling missing or financially invalid values;
- generating outputs that can later be explained by an AI layer;
- testing the numerical components independently from live API calls.

The long-term goal is a source-grounded analyst workflow in which Python produces the evidence and an LLM helps communicate it.

---

## Current capabilities

### Financial-data retrieval

The pipeline uses `yfinance` to retrieve:

- company profile, sector, industry, exchange, currency, and market information;
- annual income statements, balance sheets, and cash-flow statements;
- quarterly statements for current and trailing-twelve-month calculations;
- five years of historical daily price data.

### Financial analysis

Historical annual metrics currently include:

- revenue growth;
- gross margin;
- operating margin;
- net margin;
- free cash flow;
- free-cash-flow margin;
- current ratio;
- debt-to-equity ratio.

### Valuation

Current market values are combined with trailing-twelve-month fundamentals to calculate:

- price-to-earnings ratio;
- price-to-sales ratio;
- EV/EBITDA;
- free-cash-flow yield.

Invalid or economically misleading ratios—such as a conventional P/E ratio for a loss-making company—are returned as unavailable rather than treated as meaningful values.

### Discounted cash-flow model

The DCF module:

- starts from the latest four quarters of revenue;
- projects five annual periods;
- converts projected revenue into free cash flow using a scenario-specific FCF margin;
- discounts forecast free cash flow;
- calculates terminal value using the Gordon Growth model;
- bridges enterprise value to equity value using cash and debt;
- uses diluted average shares when available, with shares outstanding as a fallback;
- produces a fair-value-per-share sensitivity table.

Three predefined scenarios are available:

| Scenario | Purpose |
|---|---|
| Bear | Lower growth and margins with a higher discount rate |
| Base | Central operating and valuation assumptions |
| Bull | Higher growth and margins with a lower discount rate |

These assumptions are illustrative research inputs, not forecasts or analyst consensus estimates.

### Peer comparison

The peer-analysis module compares the target company with a configured peer group using:

- latest fiscal-year revenue growth;
- TTM gross, operating, and net margins;
- approximate TTM ROE and ROIC;
- latest-quarter liquidity and leverage;
- P/E, P/S, EV/EBITDA, and FCF yield.

Peer medians are used to classify metrics as above peers, below peers, or broadly in line. Unavailable peer data is skipped without terminating the entire target-company analysis.

The current default peer groups are configured for:

- `NVDA`
- `AAPL`

Other companies can be fetched by the data layer, but a peer group must currently be added to `app/constants.py` before the complete end-to-end pipeline can run.

### Scorecard

The current scorecard evaluates five categories on a one-to-five scale:

| Category | Weight |
|---|---:|
| Growth | 30% |
| Profitability | 25% |
| Valuation | 20% |
| Balance sheet | 15% |
| Risk | 10% |

The scorecard combines absolute thresholds, peer-relative valuation, and DCF upside. Missing values currently receive a neutral treatment. Because the qualitative risk-analysis module has not yet been implemented, the risk component also defaults to a neutral score.

The general scorecard is not applied to financial-services companies because banks and insurers require a sector-specific framework.

### Visualisation and report generation

The pipeline currently generates:

- revenue trend;
- profitability-margin trends;
- free-cash-flow trend;
- DCF sensitivity heatmap;
- peer valuation comparison.

It then creates a Markdown report containing:

- company overview;
- financial metrics;
- valuation metrics;
- DCF assumptions and output;
- peer comparison;
- scorecard;
- chart paths;
- investment view;
- data-period methodology;
- disclaimer.
