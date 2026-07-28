# Current Limitations

## Overview

Quant AI Analyst is an unfinished engineering prototype. It demonstrates an end-to-end equity-analysis workflow, but it is not yet a production application or a complete investment-research system.

This file documents the main constraints of the current version so that the scope of the repository is clear.

Related documentation:

- [Architecture](architecture.md)
- [Data sources](data_sources.md)
- [DCF methodology](dcf_methodology.md)
- [Roadmap](roadmap.md)

---

## Data limitations

### Single active provider

The prototype currently depends entirely on Yahoo Finance through `yfinance`.

Provider fields can be:

- unavailable;
- delayed;
- restated;
- inconsistent between companies;
- named differently from expected rows.

The project does not yet cross-check values against SEC filings, company reports, or a second financial-data provider.

### Annual data only

The active pipeline uses annual financial statements.

It does not currently calculate:

- trailing-twelve-month values;
- last-quarter analysis;
- point-in-time historical fundamentals.

Current market values are therefore combined with latest annual statement values.

### No raw-data snapshots

The application does not save the raw provider response or retrieval timestamp.

A report may change when rerun later, even when the source code and ticker are unchanged.

### Currency alignment

The report displays the provider's currency, but the peer-comparison layer does not convert or validate currencies.

Absolute peer values may not be directly comparable when companies report in different currencies.

---

## Financial-calculation limitations

### DCF integration remains incomplete

The DCF module projects and discounts cash flows, but the current headline fair-value calculation is not yet fully connected to the forecast enterprise value.

The stored scenario FCF margins are also not yet used in the projection.

See [dcf_methodology.md](dcf_methodology.md) for details.

### Generic assumptions

Bear, base, and bull assumptions are fixed prototype values.

They are not automatically calibrated to:

- the target company's history;
- management guidance;
- analyst forecasts;
- sector conditions;
- macroeconomic conditions.

### Simplified terminal-value model

The DCF uses a perpetual-growth terminal value.

It does not currently compare the result with:

- an exit-multiple approach;
- historical valuation ranges;
- peer terminal multiples.

### Basic valuation rules

P/E, P/S, EV/EBITDA, and FCF yield use simple formulas.

The implementation does not yet handle every financial edge case, including:

- negative earnings;
- negative equity;
- negative EBITDA;
- non-operating assets;
- minority interests;
- lease liabilities;
- unusual one-off items.

### Approximate ROE and ROIC

ROE and ROIC use the latest available annual income and balance-sheet values.

They do not use average beginning-and-ending capital balances.

---

## Peer-comparison limitations

### Manually configured peers

Peer groups are stored in `app/constants.py`.

Only `NVDA` and `AAPL` currently have predefined groups.

The application does not yet:

- infer peers automatically;
- validate peers by business model;
- weight peers;
- filter peers by geography or currency;
- distinguish direct competitors from broader comparable companies.

### One failed peer can stop the analysis

The current peer loop prints a “Skipping” message but re-raises the exception.

As a result, an unavailable company can stop the full peer-comparison stage rather than being excluded.

### Median comparison is simplified

The comparison uses a fixed 10% tolerance around the peer median.

It does not account for:

- distribution width;
- outliers beyond the median;
- company size;
- expected growth;
- capital intensity;
- accounting differences.

### Negative multiples

The current formulas do not consistently classify negative earnings or EBITDA as unavailable.

A negative multiple can be mathematically valid but economically difficult to interpret.

---

## Scorecard limitations

### Heuristic thresholds

The score thresholds and category weights were selected to create a transparent prototype.

They have not been:

- statistically calibrated;
- backtested;
- validated across sectors;
- shown to predict future returns.

### General framework

The same profitability, balance-sheet, and valuation thresholds are used across companies.

This is not suitable for all sectors. Banks, insurers, REITs, utilities, and early-stage companies require different metrics.

### Neutral risk score

The risk-analysis module is not yet active.

When no risk data is available, the scorecard returns a neutral risk score of 3.

The overall recommendation therefore does not yet include company-specific filing or news risks.

### Repeated external-data calls

Some scoring functions fetch the target company's financial data again rather than reusing the data already collected by the main pipeline.

This increases runtime and creates the possibility that different parts of one run receive slightly different provider responses.

---

## Report limitations

### Rule-based text

The current report is mainly a formatted presentation of calculated data.

It does not yet provide detailed written interpretation of:

- business performance;
- valuation;
- DCF sensitivity;
- peer differences;
- risks;
- catalysts.

### Preliminary recommendation duplication

The report contains both a scorecard recommendation and a separate hard-coded preliminary recommendation.

These can disagree and should be consolidated.

### Source citations

The generated report does not currently include source links, retrieval dates, or filing citations.

### Markdown only

PDF export and the Streamlit interface are not currently implemented.

---

## Known integration constraints

The current prototype still has several code-level integration issues to resolve, including:

- the peer-comparison report helper does not yet construct the peer list correctly;
- the report expects a DCF sensitivity key that differs from the key returned by the DCF module;
- the peer-valuation chart currently uses the same output filename as the DCF sensitivity chart;
- the company name requested by the report is not among the selected company-information fields;
- historical price data is fetched but not visualised;
- typed schemas are not yet used between modules.

These are implementation tasks rather than conceptual limitations and are prioritised in the roadmap.

---

## Engineering limitations

### No caching

Every run requests live data again.

### No retry or rate-limit strategy

The application does not currently implement:

- exponential backoff;
- retries;
- timeouts;
- provider-rate-limit handling.

### Loose data contracts

Modules communicate mainly through dictionaries and DataFrames.

The prototype does not yet use Pydantic models or dataclasses to validate required fields and types.

### Limited CLI

The command currently supports only:

```bash
--ticker
```

The user cannot yet specify:

- DCF scenario directly;
- output format;
- peer group;
- data period;
- whether to include individual modules.

### No continuous integration

The repository contains tests, but automated GitHub Actions execution is not yet configured.

### No stable package configuration

`pyproject.toml` is not yet populated.

### Environment hygiene

The repository still needs final cleanup of temporary files, cached Python files, and environment-file handling.

---

## Appropriate use

The current project is appropriate for:

- demonstrating a software prototype;
- showing modular Python development;
- practising financial-data handling;
- testing financial formulas;
- generating example equity-analysis reports;
- serving as a foundation for later AI-assisted reporting.

It is not appropriate for:

- making investment decisions without independent verification;
- automated trading;
- regulated investment research;
- historical backtesting without point-in-time data;
- comparing all industries with one scorecard;
- treating the generated recommendation as financial advice.
