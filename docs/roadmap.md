# Roadmap

## Overview

This roadmap describes the planned development of Quant AI Analyst as an engineering prototype.

It is not a commitment to implement every possible feature. The priority is to make the existing quantitative pipeline reliable, understandable, and presentable before adding a complex AI-agent layer.

Related documentation:

- [Architecture](architecture.md)
- [Data sources](data_sources.md)
- [DCF methodology](dcf_methodology.md)
- [Current limitations](limitations.md)

---

## Guiding principle

The project should continue in this order:

1. make the current deterministic pipeline reliable;
2. make its assumptions and outputs easy to inspect;
3. improve data quality and reproducibility;
4. add qualitative evidence;
5. add AI-generated explanations only after the evidence layer is stable.

The LLM should explain calculated and retrieved evidence. It should not generate financial numbers independently.

---

## Phase 1 — Repository presentation

### Goal

Make the repository clear enough that another person can understand the idea, current scope, and execution steps without reading every source file.

### Tasks

- [x] Add a complete README.
- [x] Add architecture documentation.
- [x] Add data-source documentation.
- [x] Add DCF methodology documentation.
- [x] Add limitations documentation.
- [x] Add this roadmap.
- [x] Add a complete generated NVDA sample report.
- [x] Add sample charts to `examples/assets/`.
- [ ] Embed selected output images in the README.
- [ ] Add a project licence.
- [ ] Add a repository description and topics on GitHub.
- [ ] Remove temporary and generated development files.
- [ ] Remove committed cache files.
- [ ] Stop tracking the local `.env` file.
- [ ] Populate `.env.example`.
- [ ] Populate `pyproject.toml`.

### Completion criterion

A visitor can understand what the prototype does, what currently works, how to run it, and what remains unfinished.

---

## Phase 2 — End-to-end reliability

### Goal

Make the current ticker-to-report pipeline run consistently for the supported companies.

### Tasks

- [ ] Fix peer handling so unavailable peers are skipped rather than re-raised.
- [ ] Avoid modifying the configured peer list in place.
- [ ] Fix peer-list generation in the report.
- [ ] Align DCF sensitivity-table dictionary keys between the analysis and report modules.
- [ ] Give the peer-valuation chart its own output filename.
- [ ] Retrieve the company name used by the report.
- [ ] Consolidate the hard-coded preliminary recommendation with the scorecard recommendation.
- [ ] Add clear errors when a ticker has no configured peer group.
- [ ] Create output directories consistently.
- [ ] Add graceful handling for missing financial rows.
- [ ] Validate that score inputs are numeric and available.
- [ ] Prevent invalid negative valuation multiples from being interpreted as attractive.
- [ ] Reuse fetched target data instead of requesting it repeatedly inside scoring functions.

### Completion criterion

The supported tickers can complete the full pipeline and produce a report and all expected charts without manual code changes.

---

## Phase 3 — DCF consistency

### Goal

Make all DCF outputs originate from one internally consistent valuation method.

### Tasks

- [ ] Use `assumptions["fcf_margin"]` in scenario projections.
- [ ] Calculate DCF enterprise value from discounted forecast FCF and discounted terminal value.
- [ ] Use DCF enterprise value in the equity-value bridge.
- [ ] Add cash and subtract debt in the sensitivity table.
- [ ] Generate the sensitivity table from the same selected scenario forecast.
- [ ] Prefer diluted shares when a reliable value is available.
- [ ] Validate `discount_rate > terminal_growth`.
- [ ] Validate positive share count.
- [ ] Label all periods and currencies.
- [ ] Add terminal-value contribution to the report.
- [ ] Add scenario comparison to the report.
- [ ] Add tests that verify scenario assumptions change fair value.

### Completion criterion

Bear, base, and bull scenarios produce different and internally reconcilable fair values, and every sensitivity-table cell follows the same enterprise-to-equity methodology.

---

## Phase 4 — Data quality and reproducibility

### Goal

Make each generated report traceable to its exact inputs.

### Tasks

- [ ] Standardise latest-period selection across modules.
- [ ] Add optional quarterly and TTM retrieval.
- [ ] Save retrieval timestamps.
- [ ] Save the exact statement dates used.
- [ ] Save DCF assumptions and peer groups with each report.
- [ ] Add a local cache for development.
- [ ] Add stored fixtures for integration tests.
- [ ] Add retry and timeout handling.
- [ ] Add provider error messages with context.
- [ ] Record the pipeline version or Git commit.
- [ ] Add a metadata JSON or YAML file beside each report.
- [ ] Document currency differences between peers.
- [ ] Consider a second provider or SEC data for cross-checking.

### Completion criterion

A report can be reproduced from a stored input snapshot and its assumptions can be inspected without rerunning the live provider.

---

## Phase 5 — Metrics and peer analysis

### Goal

Improve the financial quality of the comparison layer.

### Tasks

- [ ] Add TTM revenue, earnings, EBITDA, and FCF.
- [ ] Use average equity for ROE.
- [ ] Use average invested capital for ROIC.
- [ ] Add current ratio to the peer dataset.
- [ ] Handle negative earnings, EBITDA, and equity explicitly.
- [ ] Add a minimum number of valid peers.
- [ ] Validate peer currencies and reporting periods.
- [ ] Add configurable peer groups through the CLI or config file.
- [ ] Add optional automatic peer suggestions.
- [ ] Separate direct competitors from broader comparables.
- [ ] Report peer median and target difference for every metric.
- [ ] Add data-coverage indicators.

### Completion criterion

Peer comparisons are period-consistent, robust to missing values, and clearly explain why a company is above or below the peer group.

---

## Phase 6 — Scorecard refinement

### Goal

Keep the scorecard interpretable while making its limitations more explicit.

### Tasks

- [ ] Move score thresholds into configuration.
- [ ] Document every threshold and weight.
- [ ] Add sector-specific scoring profiles.
- [ ] Avoid neutral imputation when too much data is missing.
- [ ] Add a data-confidence or coverage score.
- [ ] Separate risk severity from risk count.
- [ ] Show score contributions in the report.
- [ ] Add sensitivity analysis for category weights.
- [ ] Validate score boundaries with tests.
- [ ] Avoid investment-performance claims until backtesting exists.

### Completion criterion

Every score can be traced to a metric, threshold, and weight, and the report communicates when evidence is incomplete.

---

## Phase 7 — SEC filings and qualitative risks

### Goal

Add source-grounded qualitative evidence to complement the numerical pipeline.

### Tasks

- [ ] Resolve ticker to SEC CIK.
- [ ] Retrieve recent 10-K and 10-Q metadata.
- [ ] Download filing documents.
- [ ] Extract business description.
- [ ] Extract risk factors.
- [ ] Extract management discussion and analysis.
- [ ] Preserve filing URLs and dates.
- [ ] Identify repeated risk themes.
- [ ] Connect filing risks to the risk-analysis module.
- [ ] Include evidence links in the report.

### Completion criterion

The report can support qualitative claims with identifiable filing sections and source links.

---

## Phase 8 — Recent news

### Goal

Add recent external context without allowing news noise to dominate the financial analysis.

### Tasks

- [ ] Retrieve company-specific news.
- [ ] Store title, publisher, date, and URL.
- [ ] Remove duplicate or near-duplicate articles.
- [ ] Rank items by relevance and recency.
- [ ] Group articles into themes.
- [ ] Distinguish risks, catalysts, and neutral updates.
- [ ] Include only source-linked claims in the report.
- [ ] Add a configurable time window.

### Completion criterion

The report includes a concise, source-linked summary of recent developments.

---

## Phase 9 — AI explanation layer

### Goal

Use an LLM to improve communication while keeping the numerical pipeline authoritative.

### Tasks

- [ ] Isolate all LLM calls in `app/tools/llm_client.py`.
- [ ] Pass structured facts rather than raw DataFrames when possible.
- [ ] Require the model to preserve source links.
- [ ] Generate a business overview from filing evidence.
- [ ] Explain financial trends from calculated metrics.
- [ ] Explain DCF assumptions and sensitivity.
- [ ] Summarise peer strengths and weaknesses.
- [ ] Generate a risk summary from retrieved evidence.
- [ ] Prohibit unsupported numerical claims.
- [ ] Add numeric-consistency checks.
- [ ] Add citation checks.
- [ ] Add overconfidence-language checks.

### Completion criterion

Generated prose remains consistent with the deterministic outputs and every important qualitative claim has supporting evidence.

---

## Phase 10 — Interface and distribution

### Goal

Make the prototype easier to demonstrate.

### Tasks

- [ ] Add CLI arguments for scenario and output format.
- [ ] Add `--include-sec`, `--include-news`, and `--include-dcf`.
- [ ] Implement the Streamlit interface.
- [ ] Display metric cards and charts.
- [ ] Add report preview.
- [ ] Add Markdown download.
- [ ] Add PDF export.
- [ ] Add loading states and clear error messages.
- [ ] Consider a small hosted demo after the pipeline is stable.

### Completion criterion

A user can enter a supported ticker, review the evidence, and download the generated report without using the source code directly.

---

## Phase 11 — Engineering quality

### Goal

Make the repository easier to maintain and safer to extend.

### Tasks

- [ ] Populate `pyproject.toml`.
- [ ] Pin or constrain dependency versions.
- [ ] Add formatting and linting.
- [ ] Add type hints consistently.
- [ ] Introduce dataclasses or Pydantic schemas.
- [ ] Add a shared application logger.
- [ ] Separate unit, integration, and optional live-data tests.
- [ ] Add GitHub Actions.
- [ ] Add coverage reporting.
- [ ] Add pre-commit checks.
- [ ] Refactor repeated financial-data requests.
- [ ] Add clearer module and function documentation.

### Completion criterion

Tests run automatically, interfaces are explicit, and new features can be added without increasing hidden coupling.

---

## Near-term priority order

The recommended immediate order is:

1. repository cleanup and sample output;
2. fix report and chart integration issues;
3. fix peer error handling;
4. complete the DCF enterprise-to-equity calculation;
5. make scenario selection non-interactive through the CLI;
6. add run metadata and caching;
7. improve period consistency;
8. add SEC filings;
9. add the LLM explanation layer;
10. add Streamlit and PDF export.

This keeps the project focused on a reliable prototype rather than expanding prematurely into a complex autonomous agent.
