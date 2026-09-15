# Nifty 100 Financial Intelligence Platform

> **Document ID:** DAD-PROJ-001 | Version 1.0  
> **Classification:** Confidential — Internal Use Only  
> **Status:** Approved for Distribution  
> **Duration:** 45 Calendar Days | 6 Weekly Sprints | 3 Buffer Days  
> **Effective Date:** June 2026  
> **Owner:** Data Analytics Division — Project Lead

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview & Objectives](#2-project-overview--objectives)
3. [Dataset Catalogue](#3-dataset-catalogue)
4. [Supplementary Datasets](#4-supplementary-datasets)
5. [Data Relationships & Entity Map](#5-data-relationships--entity-map)
6. [System Architecture](#6-system-architecture)
7. [Module Specifications](#7-module-specifications)
8. [45-Day Sprint Plan](#8-45-day-sprint-plan)
9. [KPI Reference (50+ Metrics)](#9-kpi-reference-50-metrics)
10. [Data Quality Rules](#10-data-quality-rules)
11. [API Specification](#11-api-specification)
12. [Risk Register](#12-risk-register)
13. [Deliverables Checklist](#13-deliverables-checklist)
14. [Acceptance Criteria](#14-acceptance-criteria)
15. [Project Directory Structure](#15-project-directory-structure)
16. [Environment Setup & Quick-Start](#16-environment-setup--quick-start)
17. [Coding Standards & Best Practices](#17-coding-standards--best-practices)
18. [ETL Edge Cases](#18-etl-edge-cases)
19. [Sample SQL Queries](#19-sample-sql-queries)
20. [Screener Configuration Reference](#20-screener-configuration-reference)
21. [Dashboard Screen Specifications](#21-dashboard-screen-specifications)
22. [Testing Framework](#22-testing-framework)
23. [Sector Benchmarks](#23-sector-benchmarks)
24. [Communication & Review Plan](#24-communication--review-plan)
25. [Glossary](#25-glossary)

---

## 1. Executive Summary

| Attribute | Detail |
|---|---|
| **Platform Name** | Nifty 100 Financial Intelligence Platform |
| **Core Purpose** | Transform raw financial statement data into structured analytics intelligence for 92 Nifty 100 companies |
| **Data Foundation** | 7 core + 5 supplementary datasets covering P&L, Balance Sheet, Cash Flow, Sectors, Market Cap, Pricing |
| **Analytical Scope** | 10–13 years of annual financial history per company; 50+ computed KPIs; 12 analytics modules |
| **Primary Outputs** | Investment screener, financial health scores, sector benchmarks, automated PDF/Excel reports, Streamlit dashboard |
| **Target Users** | Data Analysts — individually assigned to specific modules per this project document |
| **Build Timeline** | 45 calendar days \| 6 weekly sprints \| 3 buffer days |
| **Quality Standard** | Production-grade: ≥80% test coverage, full documentation, zero critical bugs at handoff |
| **Currency Standard** | All monetary values in Indian Rupees — Crore (₹ Cr) unless explicitly stated otherwise |
| **Index Universe** | Nifty 100 — 92 companies after data availability filter applied |

### Platform Metrics

| Category | Metric | Value | Category | Metric | Value |
|---|---|---|---|---|---|
| Data | Core Datasets | 7 | Platform | Analytics Modules | 12 |
| Data | Supplementary Datasets | 5 | Platform | Total Features | 120+ |
| Data | Total Companies | 92 | Platform | Financial KPIs | 50+ |
| Data | P&L Records | 1,276 | Platform | Screener Filters | 18 |
| Data | Balance Sheet Records | 1,312 | Platform | Pre-built Screens | 6 |
| Data | Cash Flow Records | 1,187 | Platform | Peer Groups | 11 |
| Data | Annual Report Links | 1,585 | Platform | Sector Categories | 11 |
| Data | Stock Price Records | 5,520 | Quality | Test Coverage Target | ≥80% |
| Data | Computed Ratio Records | 1,184 | Quality | DQ Validation Rules | 14 |
| Time | Total Duration | 45 Days | Quality | Acceptance Criteria | 20 |

### Key Outcomes

| # | Key Outcome | Business Value | Owner Module |
|---|---|---|---|
| 01 | Unified financial data warehouse for 92 companies | Single source of truth; eliminates manual data gathering | ETL Pipeline |
| 02 | 50+ computed KPIs per company per year | Instant quantitative assessment without manual calculation | Ratio Engine |
| 03 | Multi-parameter investment screener (18 filters) | Reduces analyst time-to-insight from hours to seconds | Screener |
| 04 | Composite Financial Health Score (0–100) | Standardised risk triage across the full universe | Health Score |
| 05 | Sector benchmarks across 11 broad sectors | Sector rotation analysis and relative positioning | Sector Analytics |
| 06 | Peer comparison engine for 11 peer groups | Identifies best-in-class within comparable peer universes | Peer Comparison |
| 07 | Automated PDF and Excel report generation | Reproducible, consistent output; eliminates manual writing | Reporting |
| 08 | Streamlit dashboard — analyst-facing interface | Zero-code interface for non-programmer stakeholders | Dashboard |
| 09 | Annual report repository — 1,585 links | Direct access to primary source documents | Document Repo |
| 10 | Rule-based alert system and company watchlist | Proactive KPI deterioration monitoring | Alerts |

---

## 2. Project Overview & Objectives

### Mission & Vision

| Attribute | Statement |
|---|---|
| **Mission** | Build a self-contained, production-grade financial intelligence system enabling analysts to query, screen, score, and compare all 92 Nifty 100 companies using structured fundamental data — without relying on third-party paid platforms. |
| **Vision** | Become the definitive internal reference for Nifty 100 fundamental analysis — reproducible, auditable, and version-controlled from public financial filings. |
| **Principle** | Every insight must be traceable to a formula, every formula to a source column, every column to a dataset file. No black-box numbers. |

### Objectives Matrix

| ID | Objective | Success Metric | Priority | Sprint |
|---|---|---|---|---|
| O-01 | Data Engineering | All 12 datasets loaded; 0 critical DQ violations | Critical | 1 |
| O-02 | KPI Computation | 50+ KPIs for all company-year combinations | Critical | 2 |
| O-03 | Investment Screener | 18 filter types; 6 pre-built templates return results | Critical | 3 |
| O-04 | Financial Health Scoring | 0–100 score for all 92 companies; correct bands | Critical | 3 |
| O-05 | Sector Analytics | Median KPIs for all 11 sectors; sector ranking | High | 3 |
| O-06 | Peer Comparison | Percentile ranks for all 11 peer groups | High | 4 |
| O-07 | Trend & Growth Analytics | 1Y/3Y/5Y/10Y CAGR for revenue, profit, EPS | High | 4 |
| O-08 | Cash Flow Intelligence | Capital allocation matrix for all 92 companies | High | 4 |
| O-09 | Dashboard | Streamlit app — 5 pages functional; no crash | High | 5 |
| O-10 | PDF Report Generation | Company + sector PDFs for all 92 + 11 sectors | High | 5 |
| O-11 | Excel Exports | Screener export, full universe, comparison exports | Medium | 5 |
| O-12 | Alerts & Watchlist | Threshold alerts; YoY deterioration detection | Medium | 6 |
| O-13 | Test Coverage | ≥80% unit test coverage across `src/` | Critical | 6 |
| O-14 | Documentation | README: fresh setup in <30 min; docstrings on all functions | High | 6 |

### Scope Boundaries

| # | In Scope | # | Out of Scope |
|---|---|---|---|
| S01 | Fundamental analysis — P&L, Balance Sheet, Cash Flow | X01 | Real-time price feeds or live market data |
| S02 | Historical trend analysis — 10–13 years per company | X02 | Technical analysis (RSI, MACD, Bollinger Bands) |
| S03 | 50+ financial KPI computation from raw data | X03 | Machine learning price prediction models |
| S04 | Investment screener with 18 configurable filters | X04 | Options, derivatives, or futures analytics |
| S05 | Financial Health Score (0–100) composite model | X05 | User authentication or multi-tenancy |
| S06 | Sector benchmarking across 11 sectors | X06 | Cloud deployment or CI/CD infrastructure |
| S07 | Peer comparison for 11 defined peer groups | X07 | Insider trading or shareholding pattern data |
| S08 | Automated PDF and Excel report generation | X08 | ESG scoring or sustainability metrics |
| S09 | Streamlit dashboard — analyst interface | X09 | International or cross-market comparison |
| S10 | Annual report repository — 1,585 links | X10 | Portfolio construction or optimisation models |
| S11 | Simulated stock price & market cap datasets | X11 | Earnings call transcripts or news sentiment |
| S12 | Rule-based alert system and watchlist | X12 | Regulatory filing alerts or SEBI announcements |

### Stakeholder RACI Matrix

| Module | ETL Analyst | Analytics Analyst | Frontend Analyst | Reporting Analyst | QA Analyst |
|---|---|---|---|---|---|
| ETL Pipeline | R/A | C | I | I | C |
| Financial Ratio Engine | C | R/A | I | I | C |
| Investment Screener | I | R/A | C | I | C |
| Health Scoring | I | R/A | C | I | C |
| Sector Analytics | I | R/A | C | I | C |
| Peer Comparison | I | R/A | C | I | C |
| Trend & Growth | I | R/A | C | I | C |
| Cash Flow Intelligence | I | R/A | C | I | C |
| Dashboard | I | C | R/A | C | C |
| PDF / Excel Reports | I | C | C | R/A | C |
| Alerts & Watchlist | I | R | C | I | A |
| Full Test Suite | C | C | C | C | R/A |

> R = Responsible | A = Accountable | C = Consulted | I = Informed

---

## 3. Dataset Catalogue

> **Load note:** Core files use `pd.read_excel(path, header=1)` — Row 0 is metadata; Row 1 is actual headers. Supplementary files use `header=0`. Normalise `company_id` to uppercase stripped NSE ticker on every load.

| Dataset | Sheet | Records | Cols | Time Coverage | Primary Key | Currency |
|---|---|---|---|---|---|---|
| companies.xlsx | Companies | 92 | 12 | Current snapshot | id (NSE ticker) | N/A |
| profitandloss.xlsx | Profit & Loss | 1,276 | 15 | FY 2010–2024 | (company_id, year) | ₹ Crore |
| balancesheet.xlsx | Balance Sheet | 1,312 | 13 | FY 2010–2024 | (company_id, year) | ₹ Crore |
| cashflow.xlsx | Cash Flow | 1,187 | 7 | FY 2010–2024 | (company_id, year) | ₹ Crore |
| analysis.xlsx | Analysis | 20 | 6 | Multi-period text | company_id | % strings |
| documents.xlsx | Documents | 1,585 | 4 | Calendar 2010–2024 | (company_id, Year) | N/A — URLs |
| prosandcons.xlsx | Pros & Cons | 16 | 4 | Current | id (auto) | N/A — text |

### 3.1 companies.xlsx — Master Company Reference

| Column | Type | Nullable | Sample Value | Description & Notes |
|---|---|---|---|---|
| id | VARCHAR | No | TCS | NSE ticker — Primary Key. Strip whitespace; uppercase. |
| company_logo | TEXT | Yes | https://.../TCS.png | URL to company logo image. Some may return 404 — handle gracefully. |
| company_name | VARCHAR | No | Tata Consultancy Services Ltd | Full legal name. Some entries contain embedded `\n` — strip on load. |
| chart_link | TEXT | Yes | https://in.tradingview.com/... | TradingView chart URL. Display only; not used in computation. |
| about_company | TEXT | Yes | TCS is a leading IT... | Business description. Length: 50–600 chars. Display in company card. |
| website | TEXT | Yes | https://www.tcs.com/ | Official corporate website URL. |
| nse_profile | TEXT | Yes | https://nseindia.com/... | NSE India equity profile page URL. |
| bse_profile | TEXT | Yes | https://bseindia.com/... | BSE India stock page URL. |
| face_value | NUMERIC | No | 1 | Share face value in ₹. Common: 1, 2, 5, 10. Used in book value calculation. |
| book_value | NUMERIC | Yes | 157.40 | Book value per share in ₹ (latest). Display only; compute from BS for analytics. |
| roce_percentage | NUMERIC | Yes | 64.30 | ROCE % (pre-computed). Use for display; Ratio Engine values for analytics. |
| roe_percentage | NUMERIC | Yes | 0.52 | ROE % (pre-computed). Note: TCS shows 0.52 — anomaly; use Ratio Engine value. |

### 3.2 profitandloss.xlsx — Annual Profit & Loss Statements

| Column | Type | Nullable | Sample (TCS FY23) | Formula / Notes |
|---|---|---|---|---|
| id | INTEGER | No | 61 | Row ID — not analytically meaningful. Use composite key. |
| company_id | VARCHAR | No | TCS | FK → companies.id. Normalise to uppercase stripped ticker. |
| year | VARCHAR | No | Mar-23 | Financial year label. Standardise to 'YYYY-MM' via `normalize_year()`. |
| sales | NUMERIC | No | 225,458 | Net revenue / total income. Must be > 0. ₹ Crore. |
| expenses | NUMERIC | No | 176,924 | Total operating expenses. ₹ Crore. |
| operating_profit | NUMERIC | No | 48,534 | EBITDA. Cross-validate: must equal sales − expenses within ±1%. |
| opm_percentage | NUMERIC | No | 21.5 | OPM %. Validate: = operating_profit/sales×100 ±1%. Flag if diff >1%. |
| other_income | NUMERIC | Yes | 3,800 | Non-operating income (dividends received, interest). ₹ Crore. |
| interest | NUMERIC | Yes | 0 | Finance costs. 0 for debt-free companies. ₹ Crore. |
| depreciation | NUMERIC | Yes | 5,800 | D&A. ₹ Crore. EBIT = operating_profit − depreciation. |
| profit_before_tax | NUMERIC | Yes | 46,534 | PBT = EBITDA + other_income − interest − D&A. ₹ Crore. |
| tax_percentage | NUMERIC | Yes | 25.0 | Effective tax rate %. Verify: (PBT − PAT) / PBT × 100. |
| net_profit | NUMERIC | Yes | 34,990 | PAT. Can be negative. ₹ Crore. |
| eps | NUMERIC | Yes | 95.30 | Earnings Per Share in ₹. Must be > 0 if net_profit > 0. |
| dividend_payout | NUMERIC | Yes | 45.0 | Dividend payout ratio %. Can exceed 100% in low-profit years. |

### 3.3 balancesheet.xlsx — Annual Balance Sheet

| Column | Type | Nullable | Sample (ABB 2024) | Formula / Notes |
|---|---|---|---|---|
| id | INTEGER | No | 136 | Row ID. |
| company_id | VARCHAR | No | ABB | FK → companies.id. |
| year | VARCHAR | No | Mar-24 | Standardise to YYYY-MM. |
| equity_capital | NUMERIC | No | 21 | Paid-up share capital. ₹ Crore. |
| reserves | NUMERIC | Yes | 626 | Reserves & surplus. Total Equity = equity_capital + reserves. |
| borrowings | NUMERIC | Yes | 0 | Total debt (short + long term). 0 = debt-free. ₹ Crore. |
| other_liabilities | NUMERIC | Yes | 260 | Trade payables + other current liabilities. Proxy for CL in ROCE. ₹ Crore. |
| total_liabilities | NUMERIC | No | 907 | Sum of equity + all liabilities. Must equal total_assets ±1%. |
| fixed_assets | NUMERIC | Yes | 109 | Net fixed assets (after D&A). ₹ Crore. |
| cwip | NUMERIC | Yes | 1 | Capital Work In Progress. Add to fixed_assets for gross block proxy. |
| investments | NUMERIC | Yes | 0 | Long-term investments and securities. Used as liquid proxy for net debt. |
| other_asset | NUMERIC | Yes | 798 | Current assets + other assets. Catch-all non-fixed. |
| total_assets | NUMERIC | No | 907 | Sum of all asset-side items. Must equal total_liabilities ±tolerance. |

### 3.4 cashflow.xlsx — Annual Cash Flow Statements

| Column | Sign Convention | Healthy Signal | Notes |
|---|---|---|---|
| company_id | — | — | FK → companies.id. |
| year | — | — | Standardise to YYYY-MM. |
| operating_activity | Positive = good | CFO > 0 consistently | Cash generated from core operations. Primary health indicator. ₹ Crore. |
| investing_activity | Negative = normal | Negative = investing in growth | Cash used for CapEx, acquisitions, investments. ₹ Crore. |
| financing_activity | Variable | Negative = debt repayment / dividends | Debt raise/repay, equity issuance, dividends paid. ₹ Crore. |
| net_cash_flow | Pos = cash grew | Positive preferred | = CFO + CFI + CFF. Validate: matches sum ±10 Crore. ₹ Crore. |

### 3.5 analysis.xlsx — Pre-Computed Growth Metrics (Partial Coverage)

| Column | Type | Sample Value | Parsing Logic |
|---|---|---|---|
| company_id | VARCHAR | HDFCBANK | Normalise ticker FK → companies.id. |
| compounded_sales_growth | TEXT | 10 Years: 21% | Regex: `r'(\d+)\s*Years?:?\s*([\d.]+)%'` |
| compounded_profit_growth | TEXT | 5 Years: 6% | Same pattern |
| stock_price_cagr | TEXT | 10 Years: 15% | Same pattern — display only |
| roe | TEXT | 10 Years: 17% | Same pattern — use Ratio Engine ROE for analytics |

> **Coverage gap:** Only ~8 companies have entries. Compute growth metrics for all 92 via the Ratio Engine (Sprint 2). Use `analysis.xlsx` values only for display cross-check.

### 3.6 documents.xlsx — Annual Report Repository

| Column | Type | Nullable | Sample Value | Notes |
|---|---|---|---|---|
| id | INTEGER | No | 1 | Row ID. |
| company_id | VARCHAR | No | ABB | FK → companies.id. |
| Year | INTEGER | No | 2024 | Calendar year of annual report. Cast to int. |
| Annual_Report | TEXT | Yes | https://bseindia.com/...pdf | Direct PDF URL on BSE India. Validate with `requests.head()`. Some return 404. |

### 3.7 prosandcons.xlsx — Qualitative Investment Insights

| Column | Type | Nullable | Sample Value | Notes |
|---|---|---|---|---|
| id | INTEGER | No | 1 | Row ID. |
| company_id | VARCHAR | No | HDFCBANK | FK → companies.id. |
| pros | TEXT | Yes | Company is expected to give good quarter | Positive observation. One per row. Multiple rows per company allowed. |
| cons | TEXT | Yes | Stock trading at 2.76× book value | Risk observation. One per row. |

> **Coverage gap:** Only 16 records covering ~8 companies. Sprint 3 task: auto-generate pros/cons for all 92 companies using KPI threshold rules.

---

## 4. Supplementary Datasets

> Location: `supporting_datasets/`

| File | Rows | Created From | Analytical Purpose |
|---|---|---|---|
| sectors.xlsx | 92 | Manual GICS-style mapping | Sector/sub-sector aggregation, relative scoring, sector filter in screener |
| stock_prices.xlsx | 5,520 | Simulated monthly OHLCV — Jan 2020 to Dec 2024 | Price trend charts, monthly return calculation, FCF yield denominator |
| market_cap.xlsx | 552 | Simulated annual P/E, P/B, EV/EBITDA, Mkt Cap | Valuation screening (P/E, P/B), EV/EBITDA comp, dividend yield display |
| financial_ratios.xlsx | 1,184 | Computed from P&L + Balance Sheet + Cash Flow | Pre-computed KPI table; screener backbone; health score inputs |
| peer_groups.xlsx | 56 | Manually defined 11 peer groups + benchmark flags | Peer comparison engine; relative percentile ranking |

### 4.1 sectors.xlsx — Company Sector Mapping

| Broad Sector | Sub-Sectors Included | Companies |
|---|---|---|
| Financials | Private Banks, Public Sector Banks, Life Insurance, General Insurance, Consumer Finance, Holding Cos, Speciality Finance | 19 |
| Energy | Oil & Gas Refining, Oil & Gas Exploration, Power & Utilities, Renewable Energy, Gas Distribution, Power Transmission | 15 |
| Information Technology | IT Services, Internet & Platforms | 6 |
| Consumer Discretionary | Automobiles, Two Wheelers, Auto Ancillaries, Retail, Gems & Jewellery, Airlines, Travel & Tourism | 12 |
| Consumer Staples | FMCG, Food Products, Food & Beverages, Personal Products | 8 |
| Healthcare | Pharmaceuticals | 5 |
| Materials | Steel, Metals & Mining, Cement, Specialty Chemicals, Paints & Coatings | 8 |
| Industrials | Capital Goods, Defence Electronics, Defence & Aerospace, Engineering & Construction, Consumer Electricals | 9 |
| Communication Services | Telecommunications, Internet & Platforms | 2 |
| Real Estate | Real Estate, Infrastructure | 3 |
| Conglomerates / Other | Diversified Conglomerates, Holding Companies | 5 |

### 4.2 stock_prices.xlsx — Monthly OHLCV Price History (Simulated)

| Column | Type | Range / Format | Notes |
|---|---|---|---|
| company_id | VARCHAR | NSE Ticker | FK → companies.id. |
| date | VARCHAR | YYYY-MM-DD | First calendar day of each month. Covers Jan 2020 – Dec 2024 (60 months). |
| open_price | NUMERIC | ₹5 – ₹18,000 | Simulated monthly opening price. |
| high_price | NUMERIC | ₹5 – ₹19,000 | Monthly high. Always ≥ open and ≥ close. |
| low_price | NUMERIC | ₹4 – ₹17,500 | Monthly low. Always ≤ open and ≤ close. |
| close_price | NUMERIC | ₹5 – ₹18,000 | Monthly closing price. Primary field for return calculations. |
| volume | INTEGER | 100K – 50M | Simulated monthly traded volume in shares. |
| adjusted_close | NUMERIC | ₹5 – ₹18,000 | Same as close_price (no dividend adjustment in simulation). |

### 4.3 market_cap.xlsx — Annual Valuation Multiples

| Column | Type | Range | Notes |
|---|---|---|---|
| company_id | VARCHAR | NSE Ticker | FK → companies.id. |
| year | INTEGER | 2019–2024 | Calendar year. One row per company per year. |
| market_cap_crore | NUMERIC | ₹5K–₹15L Cr | Market capitalisation. Simulated. |
| enterprise_value_crore | NUMERIC | ₹4K–₹17L Cr | EV = Mkt Cap + Net Debt (proxy). Simulated. |
| pe_ratio | NUMERIC | 8–80× | Price-to-Earnings. Simulated around sector norms. |
| pb_ratio | NUMERIC | 0.5–15× | Price-to-Book. Cross-check vs `book_value` in companies.xlsx. |
| ev_ebitda | NUMERIC | 5–40× | EV / EBITDA multiple. Use for sector valuation comparison. |
| dividend_yield_pct | NUMERIC | 0–4.5% | Annual dividend yield. Simulated. |

### 4.4 financial_ratios.xlsx — Pre-Computed KPI Table

| Column | Formula / Notes |
|---|---|
| net_profit_margin_pct | net_profit / sales × 100. Negative allowed. |
| operating_profit_margin_pct | From `opm_percentage` source field. Cross-validate vs computed. |
| return_on_equity_pct | net_profit / (equity_cap + reserves) × 100. |
| debt_to_equity | borrowings / (equity_cap + reserves). 0 = debt-free. |
| interest_coverage | (op_profit + other_income) / interest. None if interest = 0. |
| asset_turnover | sales / total_assets. |
| free_cash_flow_cr | operating_activity + investing_activity (₹ Cr). |
| capex_cr | abs(investing_activity) — CapEx proxy (₹ Cr). |
| earnings_per_share | eps source field (₹). |
| book_value_per_share | (equity + reserves) / (equity_cap / face_value) (₹). |
| dividend_payout_ratio_pct | dividend_payout source field (%). |
| total_debt_cr | borrowings (₹ Cr). |
| cash_from_operations_cr | operating_activity (₹ Cr). |

### 4.5 peer_groups.xlsx — Peer Comparison Groups

| Peer Group | Members | Benchmark |
|---|---|---|
| Private Banks | HDFCBANK, ICICIBANK, AXISBANK, KOTAKBANK, INDUSINDBK | HDFCBANK |
| Public Banks | SBIN, BANKBARODA, CANBK, PNB | SBIN |
| IT Services | TCS, INFY, HCLTECH, TECHM, LTIM | TCS |
| Pharmaceuticals | SUNPHARMA, CIPLA, DRREDDY, DIVISLAB, TORNTPHARM | SUNPHARMA |
| Automobiles | MARUTI, TATAMOTORS, M&M, BAJAJ-AUTO, EICHERMOT, HEROMOTOCO, TVSMOTOR | MARUTI |
| Life Insurance | LICI, HDFCLIFE, SBILIFE, ICICIPRULI | LICI |
| Oil & Gas | RELIANCE, ONGC, BPCL, IOC, GAIL | RELIANCE |
| Power & Utilities | NTPC, POWERGRID, TATAPOWER, ADANIPOWER, NHPC, JSWENERGY, ADANIGREEN | NTPC |
| Steel & Metals | TATASTEEL, JSWSTEEL, JINDALSTEL, HINDALCO | TATASTEEL |
| FMCG | HINDUNILVR, ITC, BRITANNIA, DABUR, NESTLEIND, GODREJCP, TATACONSUM | HINDUNILVR |
| Consumer Finance | BAJFINANCE, CHOLAFIN, SHRIRAMFIN | BAJFINANCE |

---

## 5. Data Relationships & Entity Map

### 5.1 Entity-Relationship Summary

| Parent Table | Parent Key | Child Table | Child Key | Cardinality | Join Note |
|---|---|---|---|---|---|
| companies | id (NSE ticker) | profitandloss | company_id | 1 : N | Up to 15 annual rows per company |
| companies | id | balancesheet | company_id | 1 : N | Up to 15 annual rows per company |
| companies | id | cashflow | company_id | 1 : N | Up to 14 annual rows per company |
| companies | id | analysis | company_id | 1 : 1 | Partial — ~8 companies have entries |
| companies | id | documents | company_id | 1 : N | 1–20 annual report links per company |
| companies | id | prosandcons | company_id | 1 : N | Partial — ~8 companies with entries |
| companies | id | sectors | company_id | 1 : 1 | All 92 companies covered |
| companies | id | stock_prices | company_id | 1 : N | 60 monthly rows per company |
| companies | id | market_cap | company_id | 1 : N | 6 annual rows (2019–2024) |
| companies | id | financial_ratios | company_id | 1 : N | Up to 14 annual rows per company |
| companies | id | peer_groups | company_id | M : N | A company can be in multiple groups |

### 5.2 Dataset Coverage Matrix

| Dataset | Companies Covered | Years Available | Completeness | Data Source |
|---|---|---|---|---|
| companies | 92 / 92 (100%) | Snapshot only | Complete | Screener.in scrape |
| profitandloss | 92 / 92 | FY 2010–2024 | ~95% | Screener.in / BSE filings |
| balancesheet | 92 / 92 | FY 2010–2024 | ~97% | Screener.in / BSE filings |
| cashflow | 92 / 92 | FY 2010–2024 | ~91% | Screener.in / BSE filings |
| analysis | ~8 / 92 (9%) | Multi-period | Partial | Screener.in pre-computed metrics |
| documents | ~75 / 92 (82%) | Calendar 2010–24 | Partial | BSE India Annual Reports portal |
| prosandcons | ~8 / 92 (9%) | Snapshot only | Partial | Screener.in qualitative section |
| sectors | 92 / 92 | Snapshot | Complete | Created — GICS-style manual mapping |
| stock_prices | 92 / 92 | Jan 2020–Dec 2024 | Complete | Created — simulated OHLCV |
| market_cap | 92 / 92 | 2019–2024 | Complete | Created — simulated valuation |
| financial_ratios | 92 / 92 | FY 2010–2024 | ~93% | Created — computed from raw files |
| peer_groups | 46 / 92 (50%) | Snapshot | Partial | Created — manually defined groups |

### 5.3 Standard Join Patterns (Python / SQL)

```sql
-- P&L + Balance Sheet for one year
SELECT p.*, b.borrowings, b.total_assets
FROM profitandloss p JOIN balancesheet b USING (company_id, year)

-- Full profile with sector
SELECT c.id, c.company_name, s.broad_sector, s.sub_sector
FROM companies c JOIN sectors s ON c.id = s.company_id

-- CFO + Net Profit health check
SELECT p.company_id, p.year, p.net_profit, f.operating_activity
FROM profitandloss p JOIN cashflow f USING (company_id, year)

-- Valuation multiples with earnings
SELECT m.*, p.net_profit, p.eps
FROM market_cap m JOIN profitandloss p USING (company_id, year)

-- Peer group ranking
SELECT r.company_id, r.return_on_equity_pct,
  RANK() OVER (PARTITION BY pg.peer_group_name ORDER BY r.return_on_equity_pct DESC)
FROM financial_ratios r JOIN peer_groups pg USING (company_id)
```

---

## 6. System Architecture

### 7-Layer Data Platform

| Layer | Layer Name | Components | Technology |
|---|---|---|---|
| L1 | Raw Data Ingestion | Excel loader, URL validator, schema validator | Python — pandas, openpyxl, requests |
| L2 | ETL & Normalisation | Year normaliser, ticker normaliser, dedup engine | Python — pandas, custom ETL modules |
| L3 | Persistent Storage | SQLite database (10 tables) — core + supporting | SQLite 3.x — single-file, zero-config |
| L4 | Analytics Engine | Ratio engine, screener, comparator, capital classifier | Python — pandas, NumPy, scipy.stats |
| L5 | Intelligence Layer | Peer percentiles, health scorer, NLP summarizer | Python — scikit-learn, regex, NLTK |
| L6 | Reporting Layer | PDF reports, Excel exports, chart generation | ReportLab, openpyxl, matplotlib, Plotly |
| L7 | Dashboard & API | Streamlit app (8 screens), REST API (16 endpoints) | Streamlit, FastAPI, Uvicorn |

### Technology Stack

| Category | Library / Tool | Version | Purpose |
|---|---|---|---|
| Data | pandas | ≥ 2.0 | DataFrame operations, Excel read/write, pivot tables |
| Data | NumPy | ≥ 1.24 | Vectorised KPI computation, growth rate arrays |
| Data | openpyxl | ≥ 3.1 | Read .xlsx files with header=1 for core datasets |
| Database | SQLite | 3.x | Single-file relational store; zero server overhead |
| Analytics | scipy | ≥ 1.11 | Statistical distributions, hypothesis tests |
| Analytics | scikit-learn | ≥ 1.3 | KMeans clustering, percentile ranking, scaler |
| Visualisation | matplotlib | ≥ 3.7 | Static charts for PDF reports |
| Visualisation | Plotly | ≥ 5.18 | Interactive charts for Streamlit dashboard |
| Dashboard | Streamlit | ≥ 1.30 | Multi-page web dashboard |
| API | FastAPI | ≥ 0.110 | REST API server with OpenAPI docs auto-generated |
| API | Uvicorn | ≥ 0.27 | ASGI server to run FastAPI |
| PDF | ReportLab | ≥ 4.1 | PDF document generation (all reports) |
| NLP | NLTK | ≥ 3.8 | Text tokenisation for qualitative analysis |
| Testing | pytest | ≥ 7.4 | Unit tests for ETL, KPI formulas, edge cases |
| Dev | Jupyter | ≥ 7.0 | Exploratory analysis notebook |
| Dev | black | ≥ 24.0 | Code formatting — PEP8 compliance |
| Dev | ruff | ≥ 0.4 | Linting — style and import checks |
| Dev | pre-commit | ≥ 3.7 | Git hooks: black + ruff run before every commit |
| Env | python-dotenv | ≥ 1.0 | Config via .env file — paths, thresholds, flags |

---

## 7. Module Specifications

### Module 1: Data Ingestion & ETL Pipeline
**Sprint 1 (Days 1–7)**

Reads all 7 core + 5 supplementary Excel files, normalises fields, validates schemas, removes duplicates, and loads into a 10-table SQLite database. The foundation for all downstream modules.

| # | Feature | Acceptance Criterion | Output |
|---|---|---|---|
| 1.1 | Excel file loader with `header=1` support | Loads all 7 core files with correct column headers; handles merged cells | DataFrames |
| 1.2 | Ticker normaliser | `company_id.str.strip().str.upper()` on all tables; FK integrity passes | Normalised IDs |
| 1.3 | Year label standardiser | Mar-23 → 2023-03 via `normalize_year()`; Mar / Dec FY handled | Uniform year strings |
| 1.4 | Schema validator (16 rules) | Zero schema failures on reference dataset; failures logged to CSV | validation_log.csv |
| 1.5 | Deduplication engine | No duplicate (company_id, year) pairs in time-series tables | Clean tables |
| 1.6 | SQLite loader | All 10 tables written; rowcounts match source; FK constraints enabled | nifty100.db |
| 1.7 | Load audit log | Per-table load statistics: rows_in, rows_out, rejected, timestamp | load_audit.csv |

**Outputs:** `nifty100.db`, `load_audit.csv`, `validation_failures.csv`

---

### Module 2: Financial Ratio Engine
**Sprint 2 (Days 8–14)**

Computes 50+ KPIs for every company-year combination across all 14 available years. Handles all edge cases: division by zero, negative equity, debt-free companies, bank/NBFC D/E carve-out, and CAGR sign anomalies.

| # | KPI | Formula | Edge Case |
|---|---|---|---|
| 2.1 | Net Profit Margin | net_profit / sales × 100 | None if sales = 0 |
| 2.2 | Operating Profit Margin | operating_profit / sales × 100 | Cross-check vs opm_percentage |
| 2.3 | Return on Equity (ROE) | net_profit / (equity + reserves) × 100 | None if equity ≤ 0 |
| 2.4 | Return on Capital (ROCE) | EBIT / (equity + reserves + borrowings) × 100 | Exclude NBFC/Banks from D/E flag |
| 2.5 | Debt-to-Equity | borrowings / (equity + reserves) | 0 for debt-free; flag >5 for non-financials |
| 2.6 | Interest Coverage | (op_profit + other_income) / interest | None if interest = 0; 999 displayed as 'Debt Free' |
| 2.7 | Free Cash Flow | CFO + CFI | Negative allowed; flag if negative 3yr consecutive |
| 2.8 | CAGR (Revenue, PAT, EPS) | ((end/start)^(1/n) − 1) × 100 | Turnaround flag if base < 0 and end > 0 |
| 2.9 | Asset Turnover | sales / total_assets | None if total_assets = 0 |
| 2.10 | Capital Allocation Class | Sign pattern of CFO/CFI/CFF | 8 patterns → labels: Reinvest, Return, Distress, etc. |

**Outputs:** `financial_ratios` table (SQLite), `capital_allocation.csv`, `ratio_edge_cases.log`

---

### Module 3: Company Screener & Filter Engine
**Sprint 3 (Days 15–21)**

Multi-criteria stock screener with 15+ filterable metrics. Analyst configures thresholds via YAML config; no code changes needed to add new screening presets.

| # | Feature | Criteria / Logic | Output |
|---|---|---|---|
| 3.1 | Preset screeners (6 templates) | Quality, Value, Growth, Dividend, Momentum, Debt-Free | Ranked company list |
| 3.2 | Custom filter builder | Analyst defines thresholds in `screener_config.yaml` | Configurable |
| 3.3 | Ranking engine | RANK() OVER sector partition on composite score (50% profitability, 30% growth, 20% valuation) | Score 0–100 |
| 3.4 | Sector-relative screener | Same thresholds normalised within broad_sector; flags outliers (>2σ or bottom decile) | Peer-adjusted rank |
| 3.5 | Screener export (Excel + CSV) | Top-N results with all KPIs; sortable, formatted | screener_output.xlsx |
| 3.6 | Multi-year trend filter | Filter companies where metric improved consecutively for N years | Trend table |

**Outputs:** `screener_output.xlsx`, `screener_config.yaml`, Screener API endpoint

---

### Module 4: Peer Comparison Engine
**Sprint 3 (Days 15–21)**

Compares companies within their peer group across 20 metrics. Computes within-group percentile rank for every metric. Produces radar charts and comparison tables.

| # | Feature | Logic | Output |
|---|---|---|---|
| 4.1 | Intra-group percentile rank | PERCENT_RANK() OVER (PARTITION BY peer_group ORDER BY metric) | Rank 0–1 per metric |
| 4.2 | Multi-metric radar chart | 8 axes: ROE, ROCE, NPM, D/E, FCF, PAT CAGR, Revenue CAGR, EPS CAGR | Plotly radar / matplotlib polar |
| 4.3 | Side-by-side comparison table | Up to 5 companies: all 14 ratios, 5-year CAGR, capital allocation pattern | Formatted HTML + PDF |
| 4.4 | Benchmark gap analysis | Metric_value vs benchmark_company in peer group; gap in absolute & pct | Heatmap: green=above bench, red=below |
| 4.5 | Best-in-class detection | Company in top quartile (≥75th pctile) for ≥6 of 10 metrics | 'Best in Class' badge |
| 4.6 | Weak company detection | Bottom quartile (≤25th pctile) for ≥4 of 10 metrics | 'Watch List' flag |

**Outputs:** `peer_comparison.xlsx`, `radar_charts/` (92 PNGs), `peer_percentiles` table (SQLite)

---

### Module 5: Interactive Streamlit Dashboard
**Sprint 4 (Days 22–28)**

8-screen web application. All screens load from SQLite. Deployed locally via `streamlit run app.py`. All charts are Plotly interactive; all tables are sortable.

| # | Screen | Key Widgets / Features | Data Source |
|---|---|---|---|
| 5.1 | Home / Overview | Nifty 100 summary KPIs: avg ROE, median P/E, sectors donut | companies + financial_ratios |
| 5.2 | Company Profile | Search by name/ticker. KPI tiles, P&L chart, BS chart, CF bar chart, pros/cons badges | All core tables |
| 5.3 | Financial Screener | Sidebar sliders for 10 metrics. Live-updating results table. CSV download | financial_ratios + market_cap |
| 5.4 | Peer Comparison | Select peer group → radar chart + side-by-side table | peer_groups + financial_ratios |
| 5.5 | Trend Analysis | Select company + metric → 10-year sparkline + YoY % change annotation | profitandloss + balancesheet |
| 5.6 | Sector Analysis | Sector selector → bubble chart (revenue vs ROE, size = mkt cap) | sectors + financial_ratios + market_cap |
| 5.7 | Capital Allocation Map | Treemap of 92 companies by capital pattern (8 categories) | financial_ratios (CFO/CFI/CFF signs) |
| 5.8 | Annual Reports | Company → year → clickable BSE PDF link. Badge for missing reports | documents |

**Outputs:** `app.py + pages/`, `dashboard_guide.md`

---

### Module 6: Valuation & Market Data Module
**Sprint 4 (Days 22–28)**

Uses `market_cap.xlsx` to compute and display valuation metrics. Flags companies trading above historical average multiples.

| # | Feature | Logic | Output |
|---|---|---|---|
| 6.1 | P/E Trend Chart | Line chart of P/E ratio across 2019–2024 per company | Plotly chart |
| 6.2 | P/B vs ROE Scatter | X=P/B, Y=ROE, size=Mkt Cap, colour=sector for all 92 | Scatter plot PNG |
| 6.3 | EV/EBITDA Comp Table | Current EV/EBITDA vs 5yr median, vs sector median. Flag if >20% above sector | Formatted table |
| 6.4 | Dividend Yield Ranker | Rank 92 companies by dividend yield. Filter by min yield threshold | Ranked list |
| 6.5 | FCF Yield Calculator | FCF / Market_Cap × 100. Rank descending | Computed column |
| 6.6 | Overvaluation Flag | P/E > (sector_median × 1.5) → 'Caution' badge; P/E < (sector_median × 0.7) → 'Discount' badge | Badge system |

**Outputs:** `valuation_summary.xlsx`, `valuation_flags.csv`

---

### Module 7: Cash Flow Intelligence Module
**Sprint 4–5 (Days 22–35)**

Deep analysis of cash flow quality, CapEx intensity, FCF generation, and capital allocation patterns.

| # | Feature | Logic | Output |
|---|---|---|---|
| 7.1 | CFO Quality Score | CFO/PAT ratio > 1.0 across 5yr avg = 'High Quality Earnings'. <0.5 = 'Accrual Risk' | Quality badge |
| 7.2 | CapEx Intensity | CapEx / Revenue %. Light (<3%): asset-light. Heavy (>8%): capital intensive | Category label |
| 7.3 | FCF CAGR | FCF CAGR over 5yr and 10yr | CAGR column |
| 7.4 | FCF Conversion Rate | FCF / EBITDA. >60% = efficient. <30% = CapEx heavy | Ratio + tier |
| 7.5 | Debt Repayment Detection | CFF < 0 AND borrowings declining YoY → 'Deleveraging' flag | Event flag |
| 7.6 | Distress Pattern | CFO < 0 AND CFF > 0 (equity/debt raise to fund operations) | 'Distress Signal' alert badge |
| 7.7 | Capital Allocation Matrix | 8 CFO/CFI/CFF sign patterns → descriptive labels | Pattern table |

**Outputs:** `cashflow_intelligence.xlsx`, `distress_alerts.csv`

---

### Module 8: Automated PDF Report Generator
**Sprint 5 (Days 29–35)**

Generates company-level and portfolio-level PDF reports on demand using ReportLab.

| # | Report Type | Contents | Frequency |
|---|---|---|---|
| 8.1 | Company Tearsheet (2-page) | Page 1: KPI tiles, 10yr revenue & profit bar, ROE/ROCE trend. Page 2: BS composition, CF waterfall, capital allocation badge, pros/cons | On-demand via API |
| 8.2 | Portfolio Summary (1-page/co) | All 92 companies: company name, sector, top 6 KPIs, trend arrow (↑ ↓ →) for 3yr direction | Weekly batch |
| 8.3 | Sector Report | Sector header page + all companies in sector. Sector median KPI table. Best/worst highlighted | Monthly batch |
| 8.4 | Screener Output Report | Formatted PDF of screener results with charts, sorted by composite score | On-demand |
| 8.5 | Peer Group Report | Radar charts + side-by-side table for each of 11 peer groups | Weekly batch |

**Outputs:** `reports/tearsheets/` (92 PDFs), `reports/portfolio/`, `reports/sector/` (11 PDFs)

---

### Module 9: NLP & Qualitative Analysis Module
**Sprint 5 (Days 29–35)**

Parses and enriches qualitative text fields. Auto-generates pros/cons for companies with missing records.

| # | Feature | Logic | Output |
|---|---|---|---|
| 9.1 | Analysis text parser | Regex `r'(\d+)\s*Years?:?\s*([\d.]+)%'` on growth fields | Parsed numeric table |
| 9.2 | Auto pros/cons generator | 12 pro rules (ROE>20%, FCF positive 5yr, D/E=0, revenue CAGR>15%, etc.) + 12 con rules | pros_cons_generated.csv |
| 9.3 | Business description tagger | Classify `about_company` text into sector tags using keyword matching | Tag validation report |
| 9.4 | Sentiment scorer | Basic polarity scoring using NLTK SentimentIntensityAnalyzer | Sentiment score per entry |
| 9.5 | CAGR cross-validator | Compare parsed analysis.xlsx CAGR vs Ratio Engine computed CAGR. Flag >5% divergence | cross_validation.csv |

**Outputs:** `pros_cons_generated.csv`, `analysis_parsed.csv`

---

### Module 10: Statistical Analysis & Clustering Module
**Sprint 5–6 (Days 29–42)**

Uses scikit-learn for KMeans clustering of companies by financial profile. Computes portfolio-level statistics and correlation matrices.

| # | Feature | Logic | Output |
|---|---|---|---|
| 10.1 | KMeans clustering (5 clusters) | Features: ROE, D/E, Revenue CAGR, FCF CAGR, OPM. StandardScaler + KMeans(n=5). Elbow method | cluster_labels.csv |
| 10.2 | Cluster profiling | Mean/median per cluster. Labels: High-Quality Growth, Defensive Dividend, Value Cyclicals, Distressed, Emerging Growth | Cluster profile table |
| 10.3 | Correlation matrix | Pearson correlation of 10 KPIs across all 92 companies × latest year | correlation_heatmap.png |
| 10.4 | Outlier detection | Z-score per metric per sector. \|Z\|>3 → 'Outlier' flag | outlier_report.csv |
| 10.5 | Portfolio statistics | Distribution of ROE, D/E, P/E across Nifty 100. P10/P25/P50/P75/P90 percentile table | portfolio_stats.csv |

**Outputs:** `cluster_labels.csv`, `portfolio_stats.csv`, `outlier_report.csv`

---

### Module 11: REST API Module
**Sprint 6 (Days 36–42)**

FastAPI server exposing 16 endpoints. Auto-generates OpenAPI documentation at `/docs`.

| # | Endpoint | Method | Description |
|---|---|---|---|
| 11.1 | /api/v1/companies | GET | List all 92 companies. Supports `?sector=` filter. |
| 11.2 | /api/v1/companies/{ticker} | GET | Full company profile: KPIs, pros/cons, sector, description. |
| 11.3 | /api/v1/companies/{ticker}/pl | GET | P&L history. Supports `?from_year=` `?to_year=`. |
| 11.4 | /api/v1/companies/{ticker}/bs | GET | Balance sheet history. Same year filters. |
| 11.5 | /api/v1/companies/{ticker}/cashflow | GET | Cash flow history. Same year filters. |
| 11.6 | /api/v1/companies/{ticker}/ratios | GET | All 14 pre-computed KPIs per year for one company. |
| 11.7 | /api/v1/companies/{ticker}/tearsheet | GET | Returns pre-generated tearsheet PDF (binary download). |
| 11.8 | /api/v1/screener | GET | `?min_roe=&max_de=&sector=&min_cagr=` → ranked list. |
| 11.9 | /api/v1/sectors | GET | List all 11 sectors with company count and median KPIs. |
| 11.10 | /api/v1/sectors/{sector}/companies | GET | All companies in a sector with KPI summary. |
| 11.11 | /api/v1/peers/{group_name} | GET | All companies in a peer group with percentile ranks. |
| 11.12 | /api/v1/companies/{ticker}/peers/compare | GET | Radar data: company vs peer group average for 8 metrics. |
| 11.13 | /api/v1/market-cap/{ticker} | GET | Historical valuation multiples (P/E, P/B, EV/EBITDA) 2019–2024. |
| 11.14 | /api/v1/portfolio/stats | GET | Portfolio-level statistics: P10–P90 for all 10 core KPIs. |
| 11.15 | /api/v1/companies/{ticker}/documents | GET | Annual report links for a company. |
| 11.16 | /api/v1/health | GET | Server health check: DB row counts and server uptime. |

**Outputs:** `api/main.py`, `openapi.json`

---

### Module 12: Testing & Quality Assurance Module
**Sprint 6 (Days 36–45)**

pytest test suite with 60+ test cases.

| # | Test Category | Test Cases | Pass Criterion |
|---|---|---|---|
| 12.1 | ETL Tests | year_normaliser (20 cases), ticker_normaliser (15 cases), dedup (5 cases), load_audit (5 cases) | All 45 ETL tests pass |
| 12.2 | KPI Formula Tests | ROE with positive equity, ROE with negative equity (None), D/E for debt-free (0), ICR for interest=0, CAGR turnaround flag | All 20 formula tests pass |
| 12.3 | DQ Rule Tests | Each of 14 DQ rules triggered on crafted violation records; severity correct | 14/14 rules trigger correctly |
| 12.4 | API Tests | /health returns 200; /companies returns 92 records; /screener with valid filters; invalid ticker returns 404 | All 10 API tests pass |
| 12.5 | Regression Tests | After any schema change, run full suite. No previously-passing test should fail | Zero regressions |

**Outputs:** `tests/` directory, `pytest_report.html`

---

## 8. 45-Day Sprint Plan

| Sprint | Days | Theme | Modules | Exit Criteria |
|---|---|---|---|---|
| Sprint 1 | 1–7 | Data Foundation | Module 1 | nifty100.db built; all 10 tables loaded; 0 CRITICAL DQ failures |
| Sprint 2 | 8–14 | Ratio Engine | Module 2 | financial_ratios table populated 92×14yr; all KPI formula tests pass |
| Sprint 3 | 15–21 | Screener & Peers | Modules 3–4 | 6 preset screeners operational; peer percentile table built for all 11 groups |
| Sprint 4 | 22–28 | Dashboard & Valuation | Modules 5–6 | Streamlit app running on localhost:8501; all 8 screens navigable |
| Sprint 5 | 29–35 | Intelligence & Reports | Modules 7–9 | 92 company tearsheet PDFs generated; pros_cons_generated.csv complete |
| Sprint 6 | 36–45 | API, ML & QA | Modules 10–12 | All 16 API endpoints return correct data; 60+ pytest tests pass |

### Sprint 1 — Data Foundation (Days 1–7)

| Day | Tasks | Deliverable |
|---|---|---|
| D01 | Set up project directory structure. Create venv; install all dependencies; configure `.env` file | requirements.txt, .env.template |
| D02 | Write Excel loader with `header=1` support. Write `normalize_year()` and `normalize_ticker()` functions | etl/loader.py, tests/etl/test_normalise.py |
| D03 | Implement schema validator (16 DQ rules). Run against all 7 files. Log failures | etl/validator.py, validation_failures.csv |
| D04 | Build SQLite schema (10 tables with FK constraints). Write loader to insert normalised DataFrames | db/schema.sql, db/loader.py |
| D05 | Load all 5 supplementary files. Run full load for all 12 files. Generate load_audit.csv | nifty100.db, load_audit.csv |
| D06 | Data quality review: manually check 5 random companies across all time-series tables. Fix any loader bugs | DQ review notes |
| D07 | Write 10 SQL exploratory queries. Sprint retrospective | exploratory_queries.sql, sprint1_retro.md |

### Sprint 2 — Ratio Engine (Days 8–14)

| Day | Tasks | Deliverable |
|---|---|---|
| D08 | Implement profitability ratios: NPM, OPM, ROE, ROCE. Edge cases: negative equity, zero sales. Cross-validate OPM | analytics/ratios.py |
| D09 | Implement leverage + efficiency ratios: D/E (bank carve-out), ICR (debt-free substitution), Asset Turnover | tests/kpi/test_leverage.py |
| D10 | Implement CAGR engine: Revenue CAGR, PAT CAGR, EPS CAGR for 3yr, 5yr, 10yr windows. Turnaround flag logic | analytics/cagr.py |
| D11 | Implement cash flow KPIs: FCF, CFO Quality Score, CapEx Intensity, FCF Conversion, capital allocation pattern | analytics/cashflow_kpis.py |
| D12 | Populate financial_ratios table in SQLite for all 92 companies × all years | Updated financial_ratios table |
| D13 | Implement ROCE for banks/NBFCs: sector-relative approach. Log anomalies | sector_roce_notes.csv |
| D14 | Run all 20 KPI formula tests. Fix failures. Write ratio_edge_cases.log | All KPI tests green, sprint2_retro.md |

### Sprint 3 — Screener & Peer Comparison (Days 15–21)

| Day | Tasks | Deliverable |
|---|---|---|
| D15 | Build custom filter engine: load screener_config.yaml; apply threshold filters via pandas query | src/screener/engine.py |
| D16 | Implement 6 preset screeners. Test each preset on the full 92-company universe | 6 screener presets in config |
| D17 | Build ranking engine: composite score (50/30/20 weights). Sector-relative normalisation | screener_output.xlsx |
| D18 | Build peer group module: load peer_groups.xlsx; compute PERCENT_RANK per metric for all 11 groups | analytics/peer.py, peer_percentiles table |
| D19 | Generate radar chart data for each company-peer group pair. Plot Plotly radar PNGs | reports/radar_charts/ (92 PNGs) |
| D20 | Generate peer_comparison.xlsx: one sheet per peer group, all metrics, colour-coded cells | peer_comparison.xlsx |
| D21 | Run all DQ rule tests. Fix failures. Sprint retrospective | All tests green, sprint3_retro.md |

### Sprint 4 — Dashboard & Valuation (Days 22–28)

| Day | Tasks | Deliverable |
|---|---|---|
| D22 | Scaffold Streamlit app: main `app.py` + pages/ directory. Shared data loader. Style config | app.py, pages/ skeleton |
| D23 | Build Home screen (5.1) and Company Profile screen (5.2) | pages/01_home.py, pages/02_profile.py |
| D24 | Build Screener screen (5.3) and Peer Comparison screen (5.4) | pages/03_screener.py, pages/04_peer.py |
| D25 | Build Trend Analysis (5.5), Sector Analysis (5.6), Capital Allocation Map (5.7), Annual Reports (5.8) | pages/05–08.py |
| D26 | Build Valuation module: valuation_summary.xlsx, overvaluation flags, FCF yield column | valuation_summary.xlsx |
| D27 | Dashboard integration testing: test all 8 screens with 10 random tickers | dashboard_qa.md |
| D28 | Sprint retrospective. Update README with app run instructions | README.md update, sprint4_retro.md |

### Sprints 5–6 — Intelligence, Reports, API & QA (Days 29–45)

| Days | Theme | Key Tasks | Exit Gate |
|---|---|---|---|
| D29–30 | NLP Module | Parser for analysis.xlsx CAGR text. Auto pros/cons generator (12 pro + 12 con rules) | pros_cons_generated.csv: 92 companies |
| D31–32 | Cash Flow Intelligence | CFO quality score, CapEx intensity, distress pattern flagging, capital allocation matrix | cashflow_intelligence.xlsx |
| D33–35 | PDF Report Generator | Company Tearsheet (2-page × 92). Sector reports (11). Portfolio summary | 92 tearsheets + 11 sector PDFs |
| D36–37 | KMeans Clustering | StandardScaler + KMeans(n=5). Elbow plot. Assign cluster labels. Correlation matrix heatmap | cluster_labels.csv, heatmap.png |
| D38–40 | FastAPI Server | 16 endpoints in api/ directory. Uvicorn server. OpenAPI docs. Postman collection | openapi.json, postman_collection.json |
| D41–42 | Full Test Suite | 60+ pytest tests across 4 categories. Fix failures. Generate HTML test report | pytest_report.html: all green |
| D43 | Integration Testing | End-to-end: API → Dashboard data flow. Load test with 10 concurrent screener queries | perf_notes.md |
| D44 | Documentation | Update all docstrings. Write analyst_guide.pdf | analyst_guide.pdf |
| D45 | Final Sign-Off | Run acceptance checklist (20 gates). Present to team lead. Archive final deliverables | Signed acceptance_checklist.pdf |

---

## 9. KPI Reference (50+ Metrics)

| KPI | Category | Formula | Benchmark | Edge Case / Warning Flag |
|---|---|---|---|---|
| Net Profit Margin | Profitability | net_profit / sales × 100 | >10% = good; >20% = excellent | None if sales=0. Negative allowed. |
| Operating Profit Margin | Profitability | operating_profit / sales × 100 | >15% = good; >25% = excellent | Cross-check vs opm_percentage field ±1%. |
| EBIT Margin | Profitability | (operating_profit − depreciation) / sales × 100 | >12% preferred | Excludes other_income to get core ops only. |
| Return on Equity (ROE) | Returns | net_profit / (equity + reserves) × 100 | >15% = good; >20% = excellent | None if equity+reserves ≤ 0. |
| Return on Capital (ROCE) | Returns | EBIT / (equity + reserves + borrowings) × 100 | >15% = good; >25% = excellent | Bank carve-out: use sector-relative benchmark. |
| Return on Assets (ROA) | Returns | net_profit / total_assets × 100 | >5% = good; >10% = excellent | None if total_assets = 0. |
| Debt-to-Equity (D/E) | Leverage | borrowings / (equity + reserves) | <1.0 = healthy; <0.5 = conservative | 0 = debt-free. Flag >5 for non-financials. |
| Interest Coverage (ICR) | Leverage | (op_profit + other_income) / interest | >3× = safe; >5× = strong | None if interest=0 → display 'Debt Free'. Flag if <1.5×. |
| Net Debt | Leverage | borrowings − investments − cash | < 0 = net cash positive | investments used as liquid asset proxy. |
| Net Debt / EBITDA | Leverage | net_debt / operating_profit | <2× = healthy; >4× = stressed | None if EBITDA < 0. |
| Asset Turnover | Efficiency | sales / total_assets | >1× = efficient. Asset-light >2× | None if total_assets = 0. |
| Fixed Asset Turnover | Efficiency | sales / fixed_assets | >3× = good | None if fixed_assets = 0 (service cos). |
| Working Capital Days | Efficiency | (other_asset − other_liabilities) / sales × 365 | Lower = better | >180 days = slow collections flag. |
| Revenue CAGR (3yr) | Growth | (sales_t / sales_{t-3})^(1/3) − 1 | >10% = healthy; >20% = fast | Turnaround flag if base < 0. |
| Revenue CAGR (5yr) | Growth | (sales_t / sales_{t-5})^(1/5) − 1 | >12% = healthy; >25% = strong | Turnaround flag if base < 0. |
| Revenue CAGR (10yr) | Growth | (sales_t / sales_{t-10})^(1/10) − 1 | >10% sustained = excellent | Turnaround flag. None if <10yr history. |
| PAT CAGR (3yr) | Growth | (net_profit_t / net_profit_{t-3})^(1/3) − 1 | >15% = healthy; >25% = strong | Turnaround flag. More volatile than revenue. |
| PAT CAGR (5yr) | Growth | (net_profit_t / net_profit_{t-5})^(1/5) − 1 | >15% = healthy; >30% = excellent | Turnaround flag. |
| EPS CAGR (5yr) | Growth | (eps_t / eps_{t-5})^(1/5) − 1 | >12% = healthy | Must align with PAT CAGR unless share count changed. |
| Free Cash Flow | Cash Quality | operating_activity + investing_activity | > 0 = generating cash | Negative 3yr consecutive → 'FCF Concern' flag. |
| CFO / PAT Ratio | Cash Quality | operating_activity / net_profit | >1.0 = high quality earnings | <0.5 = accrual risk. None if net_profit = 0. |
| CapEx Intensity | Cash Quality | abs(investing_activity) / sales × 100 | <3% = asset-light; >8% = capital intensive | investing_activity proxy — may include non-CapEx items. |
| FCF Conversion Rate | Cash Quality | FCF / operating_profit × 100 | >60% = efficient; <30% = heavy | None if operating_profit = 0. |
| FCF Yield | Valuation | FCF / market_cap_crore × 100 | >3% = attractive | Requires market_cap table join. |
| Price-to-Earnings (P/E) | Valuation | market_cap / net_profit | 15–25× = fair for India large caps | None if net_profit ≤ 0. Compare within sector. |
| Price-to-Book (P/B) | Valuation | market_cap / (equity + reserves) | >3× = expensive for value investors | Varies widely by sector: IT >8×, utilities <2×. |
| EV/EBITDA | Valuation | enterprise_value / operating_profit | 12–18× = fair for Indian large caps | None if EBITDA < 0. |
| Dividend Yield | Valuation | dividend_yield_pct from market_cap table | >2% = dividend-paying; >4% = high yield | Requires market_cap table. |
| Dividend Payout Ratio | Profitability | dividend_payout from P&L table | 30–60% = balanced | Flag >100% (paying more than earned). |
| Book Value Per Share | Valuation | (equity + reserves) / (equity_cap / face_value) | >1 always. Rising trend = good | Computed — cross-check vs companies.book_value. |
| Earnings Per Share (EPS) | Profitability | eps from P&L table | Rising trend preferred | Dilution risk if equity issuance ongoing. |
| Capital Allocation: Reinvestor | Qualitative | CFO>0, CFI<0, CFF<0 | Ideal: paying debt + investing from ops | Pattern: (+, −, −) |
| Capital Allocation: Distress | Qualitative | CFO<0, CFF>0 | Raising funds to fund ops — red flag | Pattern: (−, ?, +) |
| Composite Quality Score | Composite | 0.3×ROE_score + 0.25×FCF_score + 0.25×ROCE_score + 0.20×DE_score | 70–100 = excellent; 40–70 = moderate | Normalised 0–100 using P10/P90 winsorisation. |

---

## 10. Data Quality Rules

| Rule ID | Rule Name | Condition | Severity | Action |
|---|---|---|---|---|
| DQ-01 | Company PK Uniqueness | len(companies) == companies.id.nunique() | CRITICAL | Halt load. Investigate duplicate ticker. |
| DQ-02 | Annual PK Uniqueness | No duplicate (company_id, year) in P&L, BS, CF tables | CRITICAL | Deduplicate: keep last occurrence. Log all duplicates. |
| DQ-03 | FK Integrity | All company_id in child tables exist in companies.id | CRITICAL | Reject orphan rows. Log to validation_failures.csv. |
| DQ-04 | Balance Sheet Balance | \|total_assets − total_liabilities\| / total_assets < 0.01 | WARNING | Flag row. Do not reject. Analyst review required. |
| DQ-05 | OPM Cross-Check | \|opm_percentage − (op_profit/sales×100)\| < 1.0 | WARNING | Flag row. Use computed OPM in Ratio Engine. |
| DQ-06 | Positive Sales | sales > 0 for all non-bank companies | WARNING | Flag rows with sales ≤ 0. Exclude from growth CAGR. |
| DQ-07 | Year Format | After normalize_year(), all values match `r'^\d{4}-\d{2}$'` | CRITICAL | Reject row if unparseable. Log raw value. |
| DQ-08 | Ticker Format | company_id = company_id.strip().upper(). Length: 2–12 chars | CRITICAL | Normalise silently. If length out of range, reject. |
| DQ-09 | Net Cash Check | \|net_cash_flow − (CFO+CFI+CFF)\| ≤ 10 (₹ Cr tolerance) | WARNING | Flag and compute net_cash_flow from components if mismatch. |
| DQ-10 | Non-Negative Fixed Assets | fixed_assets ≥ 0 | WARNING | Negative fixed_assets → coerce to 0 and log. |
| DQ-11 | Tax Rate Range | 0 ≤ tax_percentage ≤ 60 | WARNING | Flag out-of-range. Can indicate one-off deferred tax reversal. |
| DQ-12 | Dividend Payout Cap | dividend_payout ≤ 200 (pct) | WARNING | Flag >200% as likely data entry error. Analyst confirm. |
| DQ-13 | URL Validity (documents) | requests.head(Annual_Report).status_code == 200 | WARNING | Log 404 URLs. Do not reject row — URL decay expected. |
| DQ-14 | EPS Sign Consistency | eps > 0 if net_profit > 0 | WARNING | Flag mismatch (may indicate adjustments). Use net_profit/shares. |
| DQ-15 | BSE/ASE Balance (ext.) | total_liabilities == total_assets (strict, after DQ-04 flag) | INFO | Informational counter. Flag in load_audit only. |
| DQ-16 | Coverage Check | Each company has ≥ 5 years of P&L, BS, CF records | WARNING | Flag companies with < 5yr history. Exclude from CAGR if < 3yr. |

---

## 11. API Specification

| Endpoint | Method | Query Params | Response Fields | Status Codes |
|---|---|---|---|---|
| /api/v1/companies | GET | sector, market_cap_category, search | id, company_name, broad_sector, sub_sector, roe_pct, roce_pct | 200 OK, 400 Bad Request |
| /api/v1/companies/{ticker} | GET | year (optional; default=latest) | Full company object: all companies fields + latest KPIs + sector | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/pl | GET | from_year (YYYY-MM), to_year | Array of P&L rows. All 13 numeric fields | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/bs | GET | from_year, to_year | Array of balance sheet rows. All 11 numeric fields | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/cashflow | GET | from_year, to_year | Array of cash flow rows. CFO, CFI, CFF, net_cash_flow | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/ratios | GET | year (optional; default=all) | Array: company_id, year + 14 computed KPI fields | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/tearsheet | GET | — | Binary PDF stream (application/pdf). Triggers download | 200 OK, 404 Not Found |
| /api/v1/screener | GET | min_roe, max_de, min_fcf, sector, min_rev_cagr_5yr, min_pat_cagr_5yr, max_pe | Array of matching companies with composite score | 200 OK, 400 Bad Request |
| /api/v1/sectors | GET | — | Array: sector_name, company_count, median_roe, median_pe, median_de | 200 OK |
| /api/v1/sectors/{sector}/companies | GET | year (default=latest) | Array of companies in sector with top 8 KPIs each | 200 OK, 404 Not Found |
| /api/v1/peers/{group_name} | GET | year (default=latest) | Array of companies + percentile rank for each of 10 metrics | 200 OK, 404 Not Found |
| /api/v1/companies/{ticker}/peers/compare | GET | year (default=latest) | Radar data: 8 axis metrics for company + group average + benchmark | 200 OK, 404 Not Found |
| /api/v1/market-cap/{ticker} | GET | from_year, to_year | Array: year, market_cap_crore, pe_ratio, pb_ratio, ev_ebitda, div_yield | 200 OK, 404 Not Found |
| /api/v1/portfolio/stats | GET | year (default=latest) | P10–P90 table for 10 KPIs across all 92 companies | 200 OK |
| /api/v1/companies/{ticker}/documents | GET | from_year, to_year | Array: year, Annual_Report URL, is_url_valid (boolean) | 200 OK, 404 Not Found |
| /api/v1/health | GET | — | status, db_row_counts (all 10 tables), uptime_seconds, version | 200 OK, 503 DB Unavailable |

---

## 12. Risk Register

| Risk ID | Risk | Likelihood | Impact | Mitigation Strategy |
|---|---|---|---|---|
| R-01 | Missing years of data for some companies (coverage < 5yr) | High | Medium | DQ-16 flags companies with < 5yr. Exclude from CAGR. |
| R-02 | BSE Annual Report URLs returning 404 (link decay) | High | Low | DQ-13 validates URLs on load. Dashboard shows 'Report unavailable' gracefully. |
| R-03 | analysis.xlsx text parsing fails for new formats | Medium | Medium | Regex tested for 5 format variants. Unknown formats logged to parse_failures.csv. |
| R-04 | Bank / NBFC D/E misclassification skews screener results | Medium | High | sectors.broad_sector used to carve out Financials from D/E filter. Tested on 19 financial companies. |
| R-05 | Negative equity companies breaking ROE formula | Medium | High | ROE = None if equity+reserves ≤ 0. Logged. Excluded from screener ROE filter. |
| R-06 | Simulated stock_prices / market_cap values cause incorrect real conclusions | Low | High | All simulated datasets clearly labelled SIMULATED in column comments and dashboard tooltips. |
| R-07 | CAGR turnaround flag not applied → misleading growth metrics | Low | High | CAGR engine explicitly checks base year sign. Turnaround flag stored alongside CAGR. |
| R-08 | ReportLab LayoutError on very long text cells overflowing frames | Medium | Medium | All tables use WORDWRAP; cells > 200 chars truncated with ellipsis. |
| R-09 | Streamlit slows down with full 92-company dataset on low-spec hardware | Low | Medium | SQLite queries cached with @st.cache_data (TTL=600s). Max screener result set = 50 rows. |
| R-10 | Peer group coverage is partial (46/92 companies) | Medium | Medium | Peer module gracefully handles companies not in any group: returns 'No peer group assigned'. |
| R-11 | pros/cons auto-generation produces low-confidence or incorrect flags | Medium | Low | Confidence score displayed alongside auto-generated entries. Threshold: only show if confidence > 60%. |
| R-12 | FastAPI / Uvicorn port conflict on analyst machine | Low | Low | Default port 8000. .env file contains PORT variable. README documents port change procedure. |

---

## 13. Deliverables Checklist

| # | Deliverable | Format | Owner | Sprint | Sign-Off Criteria |
|---|---|---|---|---|---|
| D-01 | nifty100.db | SQLite file | ETL | S1 | All 10 tables populated. Rowcounts match source. FK constraints pass. |
| D-02 | load_audit.csv | CSV | ETL | S1 | All 12 files loaded. Zero CRITICAL failures. |
| D-03 | validation_failures.csv | CSV | ETL | S1 | All DQ rule violations documented with severity. |
| D-04 | exploratory_queries.sql | SQL | ETL | S1 | 10+ queries covering coverage, nulls, year distribution. |
| D-05 | financial_ratios table | SQLite table | Analytics | S2 | 14 KPI columns. 1,184+ rows. KPI formula tests pass. |
| D-06 | capital_allocation.csv | CSV | Analytics | S2 | All 92 companies × all years with pattern label. |
| D-07 | screener_output.xlsx | Excel | Analytics | S3 | 6 preset screener results with composite score + 20 KPIs. |
| D-08 | screener_config.yaml | YAML | Analytics | S3 | All 15 filter thresholds defined. Analyst-editable. |
| D-09 | peer_comparison.xlsx | Excel | Analytics | S3 | 11 sheets. Colour-coded percentile cells. 20 metrics. |
| D-10 | radar_charts/ (92 PNGs) | PNG files | Analytics | S3 | One radar chart per company. 8 axes. Peer avg overlay. |
| D-11 | Streamlit Dashboard (app.py) | Python app | Frontend | S4 | 8 screens. All navigable. CSV export functional. |
| D-12 | valuation_summary.xlsx | Excel | Analytics | S4 | All 92 companies. P/E, P/B, EV/EBITDA, flags. |
| D-13 | cashflow_intelligence.xlsx | Excel | Analytics | S5 | CFO quality score, FCF CAGR, CapEx intensity, distress flags. |
| D-14 | pros_cons_generated.csv | CSV | Analytics | S5 | 92 companies. Rule-triggered. Confidence > 60%. |
| D-15 | analysis_parsed.csv | CSV | Analytics | S5 | Structured CAGR numbers from analysis.xlsx. Cross-validated. |
| D-16 | Company Tearsheets (92 PDFs) | PDF files | Reporting | S5 | 2 pages per company. All 92 companies. |
| D-17 | Sector Reports (11 PDFs) | PDF files | Reporting | S5 | One per broad sector. KPI table + company list. |
| D-18 | Portfolio Summary PDF | PDF | Reporting | S5 | All 92 companies, 1-page each in one document. |
| D-19 | cluster_labels.csv | CSV | Analytics | S6 | 5 clusters. All 92 companies assigned. Cluster names labelled. |
| D-20 | FastAPI Server (api/) | Python app | API | S6 | 16 endpoints. openapi.json exported. /health returns 200. |
| D-21 | pytest_report.html | HTML | QA | S6 | 60+ tests. All green. Runtime < 120 seconds total. |
| D-22 | analyst_guide.pdf | PDF | QA | S6 | Screener usage guide + dashboard navigation. 10–15 pages. |
| D-23 | acceptance_checklist.pdf | PDF | QA | S6 | 23 deliverables reviewed and signed off. Date stamped. |

---

## 14. Acceptance Criteria

| Gate | Area | Criterion | Tested By |
|---|---|---|---|
| AC-01 | Data Coverage | 92 companies present in companies table | `SELECT COUNT(*) FROM companies → 92` |
| AC-02 | Time Coverage | ≥ 90% of companies have ≥ 10 years of P&L, BS, CF records | DQ coverage query in load_audit.csv |
| AC-03 | Schema Integrity | All FK relationships intact | `PRAGMA foreign_key_check returns 0 rows` |
| AC-04 | KPI Completeness | financial_ratios table has ≥ 1,100 rows. All 14 KPI columns populated | `SELECT COUNT(*) FROM financial_ratios` |
| AC-05 | CAGR Accuracy | Revenue CAGR for 3 manually-checked companies matches hand-computed Excel value ±0.1% | Manual Excel spot check |
| AC-06 | ROE Accuracy | ROE for 5 companies in latest year matches companies.roe_percentage ±5% | Manual comparison |
| AC-07 | Screener Accuracy | Quality preset screener (ROE>15, D/E<1, FCF>0) produces ≥ 10 and ≤ 50 companies | Screener run on full DB |
| AC-08 | Dashboard Load | Company Profile screen loads for any of 92 tickers in < 3 seconds on localhost | Manual stopwatch test |
| AC-09 | Dashboard Export | CSV download on Screener screen produces well-formed file with correct headers | Download and open test |
| AC-10 | PDF Quality | No text overflow, no overlapping pages in any generated report | Visual review of 5 random tearsheets |
| AC-11 | API Health | GET /api/v1/health returns HTTP 200 with db_row_counts for all 10 tables | `curl /api/v1/health` |
| AC-12 | API Accuracy | GET /api/v1/companies/TCS/ratios returns rows for ≥ 10 years | API response check |
| AC-13 | API Screener | GET /api/v1/screener?min_roe=15&max_de=1 returns consistent result with Module 3 output | Response vs Excel comparison |
| AC-14 | Peer Coverage | Peer percentile table populated for all 11 peer groups. All member tickers present | `SELECT DISTINCT peer_group_name → 11` |
| AC-15 | Cluster Coverage | All 92 companies assigned to a cluster (0–4). No nulls in cluster_id column | cluster_labels.csv null check |
| AC-16 | NLP Coverage | pros_cons_generated.csv has ≥ 1 pro and ≥ 1 con for every company | CSV null check per company_id |
| AC-17 | Report Coverage | 92 tearsheet PDFs exist in reports/tearsheets/. Each is ≥ 50KB | `ls reports/tearsheets/ \| wc -l → 92` |
| AC-18 | Test Coverage | pytest count shows ≥ 60 tests collected. 0 failures. 0 errors | `pytest --tb=short output` |
| AC-19 | DQ Documentation | validation_failures.csv exists. All rows have company_id, field, issue, severity | File presence + column check |
| AC-20 | Documentation | analyst_guide.pdf exists and is ≥ 10 pages. Contains screener and dashboard sections | File size and page count check |

---

## 15. Project Directory Structure

```
nifty100/
├── data/
│   ├── raw/                    # 7 core Excel files (READ ONLY — never modify)
│   ├── supporting/             # 5 supplementary Excel files
│   └── nifty100.db             # Primary SQLite database (10 tables)
│
├── src/
│   ├── etl/                    # loader.py, validator.py, normaliser.py, schema.sql
│   ├── analytics/              # ratios.py, cagr.py, cashflow_kpis.py, screener/engine.py, peer.py, clustering.py
│   ├── nlp/                    # parser.py (analysis.xlsx), pros_cons_generator.py
│   ├── dashboard/              # app.py, pages/ (01–08), utils/charts.py, utils/db.py
│   ├── api/                    # main.py, routers/ (companies, screener, peers, sectors, reports, health)
│   └── reports/                # tearsheet.py, sector_report.py, portfolio_report.py, screener_report.py
│
├── tests/
│   ├── etl/                    # ETL normaliser and loader tests
│   ├── kpi/                    # Formula accuracy tests
│   ├── api/                    # Endpoint response tests
│   └── dq/                     # Data quality rule tests (60+ pytest test files)
│
├── config/
│   ├── screener_config.yaml    # All screening thresholds — analyst-editable
│   ├── .env.template           # Environment variable template
│   └── logging_config.yaml     # Logging configuration
│
├── reports/
│   ├── tearsheets/             # 92 company tearsheet PDFs
│   ├── sector/                 # 11 sector PDFs
│   ├── portfolio/              # Portfolio summary PDFs (weekly)
│   └── radar_charts/           # 92 radar chart PNGs
│
├── output/                     # Screener exports, ad hoc CSVs, final deliverables archive
├── notebooks/                  # Exploratory Jupyter notebooks (not in production path)
├── docs/                       # Project document PDF, analyst guide, openapi.json
│
├── requirements.txt            # All pip dependencies pinned to minor version
├── .env                        # DB_PATH, PORT, LOG_LEVEL, SIMULATED_DATA_FLAG (not committed to git)
├── README.md                   # This file
└── Makefile                    # make load, make test, make report, make api, make dashboard
```

---

## 16. Environment Setup & Quick-Start

### Prerequisites

- Python 3.10+
- Node.js (optional, for docx generation)
- Git

### Setup Steps

| Step | Command / Action | Expected Output |
|---|---|---|
| 1. Clone / unzip project | `unzip nifty100_project.zip -d nifty100/` | Project directory created with data/, src/, tests/, config/ |
| 2. Create virtual environment | `python3 -m venv .venv && source .venv/bin/activate` | `(.venv)` prompt in terminal |
| 3. Install dependencies | `pip install -r requirements.txt` | All 20 libraries installed; no errors |
| 4. Configure environment | `cp config/.env.template .env && nano .env` | Set `DB_PATH=data/nifty100.db`; `PORT=8000`; `LOG_LEVEL=INFO` |
| 5. Build database (ETL) | `python src/etl/loader.py` (or: `make load`) | nifty100.db created; load_audit.csv shows 12 files loaded |
| 6. Run KPI computation | `python src/analytics/ratios.py` (or: `make ratios`) | financial_ratios table populated; 1,100+ rows |
| 7. Run test suite | `pytest tests/ --html=reports/pytest_report.html` (or: `make test`) | 60+ tests collected; 0 failures |
| 8. Generate PDF reports | `python src/reports/portfolio_report.py` (or: `make report`) | reports/tearsheets/ populated with 92 PDFs |
| 9. Start Streamlit dashboard | `streamlit run src/dashboard/app.py` (or: `make dashboard`) | Browser opens at http://localhost:8501 |
| 10. Start REST API | `uvicorn src.api.main:app --port 8000` (or: `make api`) | API running at http://localhost:8000/docs |

### Makefile Reference

| Target | What it does | When to use |
|---|---|---|
| `make load` | Runs ETL: loads all 12 files into nifty100.db. Re-runnable (idempotent). | Day 1 and after any source file update |
| `make ratios` | Runs Ratio Engine: populates financial_ratios table. | After `make load`. Re-run after any KPI formula change. |
| `make test` | Runs full pytest suite. Generates HTML report. | Before every commit. Must be 0 failures. |
| `make report` | Generates all PDF reports: 92 tearsheets + 11 sector + 1 portfolio. | Sprint 5+. Run once a week for fresh reports. |
| `make dashboard` | Starts Streamlit on port 8501. | Day-to-day analytics work. |
| `make api` | Starts FastAPI/Uvicorn on port 8000. | Sprint 6+. When dashboard needs live API. |
| `make clean` | Deletes .pyc files, `__pycache__`, and test artifacts (NOT the database). | Before packaging final deliverables. |

---

## 17. Coding Standards & Best Practices

| Area | Standard | Tooling |
|---|---|---|
| Formatting | Black — line length 88. No manual formatting. | `black src/ tests/` — run pre-commit |
| Linting | ruff — all default rules enabled. Zero linting errors before commit. | `ruff check src/ tests/` |
| Type Hints | All function signatures must have type annotations. Return types mandatory. | mypy (optional in S1; mandatory S4+) |
| Docstrings | One-line docstring for all public functions. | `def load_pl(path: str) -> pd.DataFrame: """Load profitandloss Excel. Returns normalised DataFrame."""` |
| Imports | stdlib → third-party → local. One blank line between groups. | ruff enforces. |
| Naming | snake_case for functions/variables. PascalCase for classes. UPPER_CASE for module-level constants. | Python PEP 8 |
| Configuration | All thresholds in `screener_config.yaml` or `.env`. Zero hardcoded values in analytics/ or api/. | python-dotenv + PyYAML |
| Error Handling | Wrap external I/O (file reads, URL fetches) in try/except. Log error; do not raise to user. | `logging` module |
| Logging | Use Python logging (not print). DEBUG for ETL detail; INFO for milestones; WARNING for DQ; ERROR for failures. | `import logging; logger = logging.getLogger(__name__)` |
| Database | Use context manager (`with sqlite3.connect(DB) as conn`) for all queries. Parameterised queries only — no f-string SQL. | `conn.execute('SELECT * FROM t WHERE id = ?', (ticker,))` |
| Testing | One test file per source module. Test file: `tests/etl/test_loader.py` mirrors `src/etl/loader.py`. | pytest — fixtures in conftest.py |
| Git | Commit message format: `[S1] feat: load P&L from Excel`. Max 72 chars. No squash commits. | Each commit must be a coherent unit. |

---

## 18. ETL Edge Cases

### Year Normalisation Reference (`normalize_year()`)

| Raw Value | Output | Action |
|---|---|---|
| Mar-23 | 2023-03 | Standard format — most common |
| Mar 23 | 2023-03 | Strip space before parse |
| March-2023 | 2023-03 | Full month name support |
| 2023 | 2023-03 | Integer year → assume March FY close |
| FY23 | 2023-03 | FY prefix removal |
| Dec-22 | 2022-12 | December year-end company (e.g. NESTLEIND) |
| Jun-23 | 2023-06 | June year-end (some banks) |
| 2023-03 | 2023-03 | Already normalised — pass through |
| garbage | PARSE_ERROR | Reject row; log raw value to parse_failures.csv |

### Ticker Normalisation Reference

| Raw Value | Output |
|---|---|
| TCS | TCS |
| tcs | TCS |
| BAJAJ-AUTO | BAJAJ-AUTO |
| M&M | M&M |
| MISSING | Reject row — no FK match possible |

### CAGR Edge Case Decision Table

| Base Year Value | End Year Value | CAGR Result | Flag | Display As |
|---|---|---|---|---|
| Positive (> 0) | Positive (> 0) | Computed normally | — | e.g. 18.3% |
| Positive (> 0) | Negative (< 0) | None | DECLINE_TO_LOSS | N/A — turned loss |
| Negative (< 0) | Positive (> 0) | None | TURNAROUND | Turnaround ↑ |
| Negative (< 0) | Negative (< 0) | None | BOTH_NEGATIVE | N/A — both loss |
| Zero | Any | None | ZERO_BASE | N/A — base=0 |
| < 3yr history | Any | None | INSUFFICIENT | N/A — < 3yr |

---

## 19. Sample SQL Queries

```sql
-- Top 10 ROE Companies (Latest Year)
SELECT r.company_id, c.company_name, r.return_on_equity_pct
FROM financial_ratios r
JOIN companies c ON r.company_id = c.id
WHERE r.year = (SELECT MAX(year) FROM financial_ratios)
ORDER BY r.return_on_equity_pct DESC
LIMIT 10;

-- Debt-Free Companies
SELECT company_id, year, debt_to_equity
FROM financial_ratios
WHERE debt_to_equity = 0
  AND year = (SELECT MAX(year) FROM financial_ratios);

-- Consecutive FCF Positive (5yr)
SELECT company_id, COUNT(*) AS positive_fcf_yrs
FROM financial_ratios
WHERE free_cash_flow_cr > 0
GROUP BY company_id
HAVING positive_fcf_yrs >= 5;

-- Sector Median ROE
SELECT s.broad_sector, ROUND(AVG(r.return_on_equity_pct), 1) AS median_roe
FROM financial_ratios r
JOIN sectors s ON r.company_id = s.company_id
WHERE r.year = (SELECT MAX(year) FROM financial_ratios)
GROUP BY s.broad_sector
ORDER BY median_roe DESC;

-- Capital Allocation Pattern Count
SELECT pattern_label, COUNT(*) AS companies
FROM capital_allocation
WHERE year = (SELECT MAX(year) FROM capital_allocation)
GROUP BY pattern_label
ORDER BY companies DESC;

-- Revenue CAGR > 15% (5yr)
SELECT r.company_id, c.company_name, r.revenue_cagr_5yr
FROM financial_ratios r
JOIN companies c ON r.company_id = c.id
WHERE r.revenue_cagr_5yr > 15
ORDER BY r.revenue_cagr_5yr DESC;

-- Missing Annual Reports
SELECT c.id, c.company_name, 2024 - COUNT(d.Year) AS missing_yrs
FROM companies c
LEFT JOIN documents d ON c.id = d.company_id AND d.Year >= 2015
GROUP BY c.id
HAVING missing_yrs > 2
ORDER BY missing_yrs DESC;

-- Peer Group Rankings (ROE)
SELECT p.peer_group_name, r.company_id, r.return_on_equity_pct,
  RANK() OVER (PARTITION BY p.peer_group_name ORDER BY r.return_on_equity_pct DESC) AS roe_rank
FROM financial_ratios r
JOIN peer_groups p ON r.company_id = p.company_id
WHERE r.year = (SELECT MAX(year) FROM financial_ratios);
```

---

## 20. Screener Configuration Reference

### Preset Screeners (`screener_config.yaml`)

| Preset Name | Filters Applied | Ranking Metric | Expected Company Count |
|---|---|---|---|
| Quality Compounder | ROE > 15%, D/E < 1.0, FCF > 0, Revenue CAGR 5yr > 10% | Composite Score (desc) | 15–35 companies |
| Value Pick | P/E < 20, P/B < 3.0, D/E < 2.0, Dividend Yield > 1% | FCF Yield (desc) | 10–25 companies |
| Growth Accelerator | PAT CAGR 5yr > 20%, Revenue CAGR 5yr > 15%, D/E < 2.0 | PAT CAGR 5yr (desc) | 8–20 companies |
| Dividend Champion | Dividend Yield > 2%, Dividend Payout < 80%, FCF > 0 | Dividend Yield (desc) | 10–20 companies |
| Debt-Free Blue Chip | D/E = 0, ROE > 12%, Revenue > 5,000 Cr | ROE (desc) | 15–30 companies |
| Turnaround Watch | Revenue CAGR 3yr > 10%, FCF improving (positive latest yr), D/E declining | Revenue CAGR 3yr (desc) | 5–15 companies |

### Composite Score Weights

| Dimension | Weight | Inputs | Normalisation |
|---|---|---|---|
| Profitability | 35% | ROE (15%), ROCE (10%), NPM (10%) | Winsorise P10–P90; scale 0–100 per metric; weighted avg |
| Cash Quality | 30% | FCF CAGR 5yr (15%), CFO/PAT ratio (10%), FCF > 0 flag (5%) | Same; FCF flag = 100 if positive, 0 if negative |
| Growth | 20% | Revenue CAGR 5yr (10%), PAT CAGR 5yr (10%) | Same; CAGR flags (Turnaround) → score = 0 |
| Leverage | 15% | D/E score (10%), ICR score (5%) | D/E: 0=100, 0.5=85, 1=70, 2=50, >5=0. ICR: >10=100, 5=75, 3=50, <1.5=0 |

---

## 21. Dashboard Screen Specifications

| Screen | URL Path | Key Data Queries | Interactive Elements | Export |
|---|---|---|---|---|
| Home / Overview | / | SELECT from companies + financial_ratios (latest year) | Sector filter chips, year selector (2019–2024) | — |
| Company Profile | /company | All tables for selected ticker | Ticker search box, year range slider | PDF tearsheet download link |
| Financial Screener | /screener | SELECT from financial_ratios + market_cap with WHERE clauses | 10 metric sliders in sidebar, preset dropdown | CSV download, Excel download |
| Peer Comparison | /peers | SELECT from peer_percentiles + financial_ratios for group | Peer group dropdown, metric axis selector (8 axes) | PNG chart save, Excel table |
| Trend Analysis | /trends | SELECT time-series from financial_ratios for ticker + metric | Ticker search, metric multi-select (overlay up to 3) | CSV download |
| Sector Analysis | /sectors | SELECT with JOIN sectors | Sector dropdown, year slider, metric selector for axes | PNG chart save |
| Capital Allocation Map | /capital | SELECT capital_allocation by year | Year slider, click on pattern category → company list | CSV download |
| Annual Reports | /documents | SELECT from documents WHERE company_id = ticker | Ticker search, year filter | — |

---

## 22. Testing Framework

| Test File | Test Name | Input | Expected Output |
|---|---|---|---|
| tests/etl/test_normalise.py | test_year_mar23 | Mar-23 | 2023-03 |
| tests/etl/test_normalise.py | test_year_fy24 | FY24 | 2024-03 |
| tests/etl/test_normalise.py | test_year_dec22 | Dec-22 | 2022-12 |
| tests/etl/test_normalise.py | test_year_garbage | xyz | PARSE_ERROR |
| tests/etl/test_normalise.py | test_ticker_strip | `  TCS  ` | TCS |
| tests/etl/test_normalise.py | test_ticker_lower | tcs | TCS |
| tests/kpi/test_ratios.py | test_roe_positive | net_profit=100, equity=500 | ROE = 20.0 |
| tests/kpi/test_ratios.py | test_roe_neg_equity | net_profit=100, equity=-50 | ROE = None |
| tests/kpi/test_ratios.py | test_de_debtfree | borrowings=0, equity=500 | D/E = 0 |
| tests/kpi/test_ratios.py | test_icr_debtfree | interest=0 | ICR = None (display 'Debt Free') |
| tests/kpi/test_ratios.py | test_cagr_turnaround | base=-100, end=200 | CAGR = None, flag='TURNAROUND' |
| tests/kpi/test_ratios.py | test_cagr_normal | base=100, end=161, n=5 | CAGR ≈ 10.0% |
| tests/dq/test_rules.py | test_dq04_bs_balance | assets=1000, liab=1020 | DQ-04 WARNING triggered |
| tests/dq/test_rules.py | test_dq06_zero_sales | sales=0 | DQ-06 WARNING triggered |
| tests/api/test_health.py | test_health_200 | GET /api/v1/health | HTTP 200, status='ok' |
| tests/api/test_api.py | test_companies_count | GET /api/v1/companies | 92 records returned |
| tests/api/test_api.py | test_invalid_ticker | GET /api/v1/companies/INVALID | HTTP 404 |
| tests/api/test_api.py | test_screener_filter | GET /api/v1/screener?min_roe=15 | All results have ROE ≥ 15 |

---

## 23. Sector Benchmarks

> For relative scoring, normalise KPIs against these sector ranges rather than the universal Nifty 100 range. A D/E of 4× is a CRITICAL flag for an IT company but completely normal for a bank. The Ratio Engine uses `sectors.broad_sector` to select the appropriate benchmark range for each metric.

| Sector | ROE Range | D/E Range | OPM Range | P/E Range | Notes |
|---|---|---|---|---|---|
| Financials (Banks) | 12–22% | > 5× (normal) | 25–45% NIM proxy | 12–25× | D/E structurally high — use NIM + ROA for banks instead of OPM |
| Financials (NBFC) | 12–20% | 3–8× (normal) | 30–55% NIM proxy | 15–30× | Higher ROA and ROE expected for consumer finance vs banks |
| Information Technology | 25–50% | 0–0.3× | 20–35% | 22–40× | Asset-light; high ROE; low D/E; premium P/E for growth |
| Consumer Staples (FMCG) | 20–45% | 0–0.5× | 15–28% | 40–70× | Very high P/E; brand moat; consistent margins; low debt |
| Healthcare / Pharma | 15–30% | 0–0.8× | 15–25% | 25–45× | Moderate debt; R&D adds intangible assets; premium for growth |
| Energy (Oil & Gas) | 10–18% | 0.5–2× | 8–18% | 8–15× | Capital intensive; commodity-linked margins; PSU majority |
| Energy (Power) | 8–15% | 1–4× | 25–40% | 12–20× | High D/E normal for regulated utilities; stable margin |
| Consumer Discretionary | 10–25% | 0.3–1.5× | 10–20% | 25–50× | Wide range; auto OEMs have lower OPM than consumer brands |
| Materials (Steel) | 10–25% | 0.3–1× | 12–22% | 8–18× | Cyclical; margins volatile with commodity prices |
| Materials (Cement) | 12–22% | 0.3–1× | 18–28% | 18–35× | Oligopoly; regional pricing power; moderate debt |
| Industrials | 12–22% | 0.3–1.5× | 10–20% | 20–35× | Capital goods order-book driven; L&T sets benchmark |
| Conglomerates | 10–20% | 0.5–2× | 8–18% | 15–30× | Diverse revenue streams; holding company discount applied |

---

## 24. Communication & Review Plan

### Week-by-Week Review Schedule

| Week | Days | Review Meeting | Deliverables to Share | Go / No-Go Criteria |
|---|---|---|---|---|
| Week 1 | D01–07 | End of D07 — Sprint 1 Review (30 min) | nifty100.db, load_audit.csv, validation_failures.csv, exploratory_queries.sql | All 10 tables loaded. Zero CRITICAL DQ failures. Coverage > 90%. |
| Week 2 | D08–14 | End of D14 — Sprint 2 Review (45 min) | financial_ratios table (SQLite export), ratio_edge_cases.log, all KPI tests green | 1,100+ rows in financial_ratios. Formula spot-checks pass. All 20 KPI tests green. |
| Week 3 | D15–21 | End of D21 — Sprint 3 Review (45 min) | screener_output.xlsx (6 presets), peer_comparison.xlsx (11 groups), radar chart samples | 6 screeners operational. 11 peer groups populated. All DQ tests pass. |
| Week 4 | D22–28 | End of D28 — Sprint 4 Demo (60 min) | Live Streamlit dashboard demo, valuation_summary.xlsx | All 8 screens load without errors. Screener returns correct results. CSV download works. |
| Week 5 | D29–35 | End of D35 — Sprint 5 Review (45 min) | Sample tearsheets (3 companies), pros_cons_generated.csv, cashflow_intelligence.xlsx | 5 tearsheets reviewed: no overflow. NLP coverage > 90%. CF flags spot-checked. |
| Week 6 | D36–42 | End of D42 — Sprint 6 Review (60 min) | API demo (Postman), pytest_report.html, cluster_labels.csv | 16 endpoints live. 60+ tests pass. Cluster labels make business sense. |
| Final | D43–45 | D45 — Project Sign-Off (90 min) | All 23 deliverables, acceptance_checklist.pdf signed | All 20 acceptance gates pass. Lead signs acceptance_checklist.pdf. Project archived. |

### Daily Stand-Up Format (5 minutes per person)

| Question | Guidance | Max Time |
|---|---|---|
| What did I complete yesterday? | Name the specific deliverable or sub-task. Reference the sprint task board item. | 90 seconds |
| What will I complete today? | Commit to a specific deliverable — not vague ('work on module X'). Name the file/function. | 90 seconds |
| What is blocking me? | Only blockers that cannot self-resolve within 2 hours. Escalate to team lead after 2 hours. | 60 seconds |
| Anything to share? | Optional: share a finding, risk spotted, or cross-team dependency discovered. Keep it brief. | 60 seconds |

---

## 25. Glossary

| Term | Definition |
|---|---|
| Asset Turnover | Sales divided by total assets. Measures how efficiently a company uses its assets to generate revenue. |
| Book Value Per Share | (Equity capital + Reserves) divided by number of shares outstanding. Represents net asset value per share. |
| CAGR | Compound Annual Growth Rate. ((End Value / Start Value)^(1/n) − 1) × 100. Annualised growth metric. |
| CapEx | Capital Expenditure. Funds used to acquire or upgrade long-term physical assets. Proxy: absolute value of investing_activity. |
| Capital Allocation | How a company distributes its generated cash between reinvestment, debt repayment, and shareholder returns. |
| CFI | Cash Flow from Investing Activities. Covers CapEx, acquisitions, and investment purchases. Typically negative. |
| CFF | Cash Flow from Financing Activities. Covers debt issuance/repayment and equity transactions including dividends. |
| CFO | Cash Flow from Operations. Cash generated by core business activities. Must be positive for a healthy business. |
| CWIP | Capital Work-In-Progress. Assets under construction not yet in use. Excluded from net fixed assets. |
| D/E | Debt-to-Equity Ratio. Total borrowings divided by total equity (capital + reserves). Measures leverage. |
| Debt-Free | Company with zero or negligible borrowings. D/E = 0. ICR displayed as 'Debt Free' instead of infinity. |
| EBIT | Earnings Before Interest and Taxes. Operating_profit minus depreciation. Core operational earnings metric. |
| EBITDA | Earnings Before Interest, Taxes, Depreciation & Amortisation. Proxy: operating_profit in this dataset. |
| EPS | Earnings Per Share. Net profit divided by number of shares. Source: eps column in profitandloss table. |
| EV | Enterprise Value. Market Cap + Net Debt. Represents total company value to all capital providers. |
| EV/EBITDA | Enterprise Value divided by EBITDA. Cross-sector valuation multiple. Lower = potentially cheaper. |
| FCF | Free Cash Flow. CFO + CFI. Cash available after maintaining/expanding asset base. Core quality metric. |
| FCF Yield | FCF divided by Market Cap × 100. Higher = better value for cash-generating companies. |
| FK | Foreign Key. A database constraint linking child table rows to parent table rows via a shared key column. |
| FY | Financial Year. In India, April 1 to March 31. FY24 = April 2023 to March 2024. Labelled 'Mar-24' in source data. |
| GICS | Global Industry Classification Standard. Tiered sector taxonomy: Sector → Industry Group → Industry → Sub-Industry. |
| ICR | Interest Coverage Ratio. (EBIT + Other Income) / Interest expense. Measures ability to service debt. |
| KPI | Key Performance Indicator. A quantifiable measure used to evaluate business performance. 50+ defined in this document. |
| Large Cap | Companies with market capitalisation > ₹20,000 Crore. All Nifty 100 companies qualify. |
| Nifty 100 | NSE India index of 100 largest companies by free-float market cap. This dataset covers 92 of those companies. |
| NPM | Net Profit Margin. Net profit divided by total sales × 100. Expressed as percentage. |
| NBFC | Non-Banking Financial Company. Lender/financial services firm that is NOT a bank. High D/E structurally normal. |
| NSE | National Stock Exchange of India. Primary stock exchange. Ticker symbols used as company primary keys. |
| OPM | Operating Profit Margin. Operating profit divided by sales × 100. EBITDA margin proxy. |
| P/B | Price-to-Book Ratio. Market Cap divided by Book Value (equity + reserves). >1 means market premium to assets. |
| P/E | Price-to-Earnings Ratio. Market Cap divided by Net Profit. Standard equity valuation multiple. |
| PAT | Profit After Tax. Same as Net Profit in this dataset. |
| PBT | Profit Before Tax. Net Profit divided by (1 − tax_percentage/100). Pre-tax earnings. |
| ROCE | Return on Capital Employed. EBIT / (Equity + Borrowings) × 100. Measures returns on all capital, not just equity. |
| ROE | Return on Equity. Net Profit / (Equity + Reserves) × 100. Measures returns on shareholders' funds. |
| SQLite | Serverless, file-based relational database. Single .db file. Zero configuration. Used for this project's data store. |
| Turnaround Flag | Applied to CAGR calculations where the base year value is negative and end year value is positive. CAGR set to None. |
| Winsorisation | Statistical technique: cap extreme values at P10/P90. Prevents outliers from distorting composite score normalisation. |

---

> **Document Version:** 1.0 | **Prepared for:** Data Analytics Platform Initiative | **45-Day Project**  
> *This document is CONFIDENTIAL and intended solely for the internal project team. No part of this document may be reproduced or shared externally without written approval from the Project Manager.*
