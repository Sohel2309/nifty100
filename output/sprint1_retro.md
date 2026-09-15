# Sprint 1 Retrospective — Data Foundation

**Sprint Period:** Days 1–7  
**Effective Date:** June 2026  
**Status:** Completed  
**Owner:** ETL Analyst & QA Team  

---

## 1. Objectives & Achievements

### What was Planned:
1. Set up the project directory structure, configure environment parameters (`.env`), and install dependencies.
2. Build an Excel loader script supporting custom header specification (`header=1` for core files) and date/ticker normalization.
3. Build a Schema Validator implementing 16 specific Data Quality (DQ) checks.
4. Establish a SQLite database schema with 10 tables and load normalized DataFrames.
5. Expand database loading to include all 5 supplementary files (running full load across all 12 files).
6. Perform manual spot checks on 5 random companies to verify time-series records.
7. Write 10 exploratory SQL queries to analyze data and produce a Sprint 1 Retrospective.

### What was Accomplished:
* **100% of tasks were completed successfully** according to specifications.
* Expanded the SQLite database structure from **10 tables to 12 tables** by modeling `peer_groups` and `financial_ratios` directly as SQL tables rather than using flat files.
* Configured the `SchemaValidator` to validate all **12 datasets** prior to database loading.
* Successfully ingested **12,083 source records** and loaded **12,030 clean records** (Overall Success Rate: **99.56%**). Only minor expected records with missing URLs/values were filtered.
* Documented a thorough manual data quality review on 5 random companies (**SUNPHARMA**, **BAJFINANCE**, **ADANIGREEN**, **HAL**, **EICHERMOT**) in `output/dq_review_notes.md`.
* Compiled and validated **10 SQL exploratory queries** in `output/exploratory_queries.sql`.

---

## 2. Ingestion & Database Summary

The load audit log generated at `output/load_audit.csv` records the following ingestion statistics:

| Table Name | Source Rows | Loaded Rows | Rejected Rows | Status |
| --- | --- | --- | --- | --- |
| **companies** | 92 | 92 | 0 | SUCCESS |
| **profitandloss** | 1,070 | 1,070 | 0 | SUCCESS |
| **balancesheet** | 1,140 | 1,140 | 0 | SUCCESS |
| **cashflow** | 1,056 | 1,054 | 2 | PARTIAL (Missing CFO values) |
| **analysis** | 4 | 4 | 0 | SUCCESS |
| **documents** | 1,456 | 1,405 | 51 | PARTIAL (Missing Report URLs) |
| **prosandcons** | 4 | 4 | 0 | SUCCESS |
| **financial_ratios** | 1,041 | 1,041 | 0 | SUCCESS |
| **peer_groups** | 56 | 56 | 0 | SUCCESS |
| **sectors** | 92 | 92 | 0 | SUCCESS |
| **stock_prices** | 5,520 | 5,520 | 0 | SUCCESS |
| **market_cap** | 552 | 552 | 0 | SUCCESS |
| **Total** | **12,083** | **12,030** | **53** | **99.56% Success** |

---

## 3. Key Issues Resolved (Loader Bugs)

1. **Text Column Coercion Bug (`peer_group_name`)**:
   - *Problem*: During the loading of `peer_groups.xlsx`, the SQLite insertions failed with `NOT NULL constraint failed: peer_groups.peer_group_name`. Upon analysis, `peer_group_name` was being run through `pd.to_numeric` (coerced with `errors='coerce'`) because it was not declared in the `text_columns` set in `loader.py`.
   - *Solution*: Added `'peer_group_name'` to `text_columns` inside `loader.py`, preventing numeric coercion of text peer group labels.
2. **Boolean Check Constraint Mismatch (`is_benchmark`)**:
   - *Problem*: SQLite does not have a native boolean type. The raw boolean `True/False` values in Python were triggering check constraint failures on the `is_benchmark CHECK (is_benchmark IN (0, 1))` rule in SQLite.
   - *Solution*: Converted the `is_benchmark` column to an integer representation (`0` or `1`) during DataFrame preprocessing inside `run_etl_load()`.
3. **Exploratory Query Column Ambiguity**:
   - *Problem*: Running queries on joined tables (like Query 4 and Query 9) using `WITH` statements resulted in SQLite errors: `ambiguous column name: company_id`.
   - *Solution*: Added explicit aliases (`fr.company_id`, `pl.company_id`) in all SQL select queries to avoid column name overlaps.

---

## 4. Key Takeaways & Lessons Learned

* **Validation Precedes Ingestion**: Standardizing data (stripping tickers, mapping dates, standardizing booleans) before validating keeps the validation engine clean.
* **SQLite Constraints are Powerful**: Enforcing Foreign Key constraints (`PRAGMA foreign_keys = ON`) and custom table check constraints guarantees referential integrity immediately at the database tier.
* **Unicode Handlers on Windows**: Script execution writing markdown files with standard UTF-8 symbols (like `✓` or `✔`) can fail with a `UnicodeEncodeError` on Windows systems unless `encoding='utf-8'` is explicitly set.

---

## 5. Next Steps (Sprint 2 Preview)

With a highly validated and clean SQL database platform, we are ready to proceed with **Sprint 2: Financial Ratio Engine (Days 8-14)**:
* Implement the core analytics ratio formulas (ROE, ROCE, NPM, OPM, Debt/Equity).
* Handle edge cases such as division by zero, negative equity, and debt-free interest coverage.
* Build the CAGR growth computation engine.
* Build automated unit tests to verify calculated KPIs against the pre-loaded `financial_ratios` table.
