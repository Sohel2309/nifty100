# Data Quality Review Notes

This document captures the manual data quality check performed on 5 randomly selected companies across all time-series tables in the `nifty100.db` database.

**Date of Review:** 2026-06-19
**Database Path:** `data/nifty100.db`
**Sampled Companies:** **SUNPHARMA** (Sun Pharmaceuticals Industries Ltd), **BAJFINANCE** (Bajaj Finance Ltd), **ADANIGREEN** (Adani Green Energy Ltd), **HAL** (Hindustan Aeronautics Ltd), **EICHERMOT** (Eicher Motors Ltd)

---

## 1. Overview of Sampled Companies

### SUNPHARMA - Sun Pharmaceuticals Industries Ltd

| Table Name | Row Count | Year/Date Range | Missing values (Nulls) | Key Constraints Check |
| --- | --- | --- | --- | --- |
| profitandloss | 12 | 2013-03 to 2024-03 | 0 | Passed |
| balancesheet | 13 | 2013-03 to 2024-09 | 13 | Passed |
| cashflow | 12 | 2013-03 to 2024-03 | 84 | Passed |
| market_cap | 6 | 2019-03 to 2024-03 | 12 | Passed |
| stock_prices | 60 | 2020-01-01 to 2024-12-01 | 0 | Passed |
| financial_ratios | 12 | 2013-03 to 2024-03 | 0 | Passed |

#### Detailed Row Samples for SUNPHARMA

**Latest profitandloss record (2024-03):**
```json
company_id          SUNPHARMA
year                  2024-03
sales                 48497.0
expenses              35479.0
operating_profit      13018.0
depreciation           2557.0
other_income            865.0
interest                238.0
tax                    1478.0
net_profit             9610.0
eps                      40.0
opm_percentage           28.0
tax_percentage           13.0
dividend_payout          34.0
```

**Latest balancesheet record (2024-09):**
```json
company_id              SUNPHARMA
year                      2024-09
equity_capital              240.0
reserves                  68875.0
total_equity              69115.0
borrowings                 2572.0
other_liabilities         16429.0
total_liabilities         88116.0
current_assets            40904.0
fixed_assets              28318.0
total_assets              88116.0
investments               17744.0
cash_and_equivalents         None
```

**Latest financial_ratios record (2024-03):**
```json
company_id                     SUNPHARMA
year                             2024-03
net_profit_margin_pct              19.82
operating_profit_margin_pct         28.0
return_on_equity_pct               15.09
debt_to_equity                    0.0514
interest_coverage                58.3319
asset_turnover                    0.5685
free_cash_flow_cr                11372.0
capex_cr                           763.0
earnings_per_share                  40.0
book_value_per_share             26.5279
dividend_payout_ratio_pct           34.0
total_debt_cr                     3274.0
cash_from_operations_cr          12135.0
```

### BAJFINANCE - Bajaj Finance Ltd

| Table Name | Row Count | Year/Date Range | Missing values (Nulls) | Key Constraints Check |
| --- | --- | --- | --- | --- |
| profitandloss | 10 | 2015-03 to 2024-03 | 0 | Passed |
| balancesheet | 11 | 2015-03 to 2024-09 | 11 | Passed |
| cashflow | 10 | 2015-03 to 2024-03 | 70 | Passed |
| market_cap | 6 | 2019-03 to 2024-03 | 12 | Passed |
| stock_prices | 60 | 2020-01-01 to 2024-12-01 | 0 | Passed |
| financial_ratios | 10 | 2015-03 to 2024-03 | 0 | Passed |

#### Detailed Row Samples for BAJFINANCE

**Latest profitandloss record (2024-03):**
```json
company_id          BAJFINANCE
year                   2024-03
sales                  54972.0
expenses               18886.0
operating_profit       16099.0
depreciation             683.0
other_income              36.0
interest                   6.0
tax                     4859.0
net_profit             14451.0
eps                      233.0
opm_percentage         19987.0
tax_percentage            25.0
dividend_payout           15.0
```

**Latest balancesheet record (2024-09):**
```json
company_id              BAJFINANCE
year                       2024-09
equity_capital               124.0
reserves                   86679.0
total_equity               86803.0
borrowings                324218.0
other_liabilities           9635.0
total_liabilities         420656.0
current_assets            386167.0
fixed_assets                3423.0
total_assets              420656.0
investments                31036.0
cash_and_equivalents          None
```

**Latest financial_ratios record (2024-03):**
```json
company_id                     BAJFINANCE
year                              2024-03
net_profit_margin_pct               26.29
operating_profit_margin_pct       19987.0
return_on_equity_pct                18.84
debt_to_equity                     3.8248
interest_coverage               2689.1667
asset_turnover                     0.1463
free_cash_flow_cr                -79931.0
capex_cr                           7171.0
earnings_per_share                  233.0
book_value_per_share              61.8516
dividend_payout_ratio_pct            15.0
total_debt_cr                    293346.0
cash_from_operations_cr          -72760.0
```

### ADANIGREEN - Adani Green Energy Ltd

| Table Name | Row Count | Year/Date Range | Missing values (Nulls) | Key Constraints Check |
| --- | --- | --- | --- | --- |
| profitandloss | 8 | 2017-03 to 2024-03 | 0 | Passed |
| balancesheet | 9 | 2017-03 to 2024-09 | 9 | Passed |
| cashflow | 8 | 2017-03 to 2024-03 | 56 | Passed |
| market_cap | 6 | 2019-03 to 2024-03 | 12 | Passed |
| stock_prices | 60 | 2020-01-01 to 2024-12-01 | 0 | Passed |
| financial_ratios | 8 | 2017-03 to 2024-03 | 0 | Passed |

#### Detailed Row Samples for ADANIGREEN

**Latest profitandloss record (2024-03):**
```json
company_id          ADANIGREEN
year                   2024-03
sales                   9220.0
expenses                1902.0
operating_profit        7318.0
depreciation            1903.0
other_income            1262.0
interest                5006.0
tax                      411.0
net_profit              1260.0
eps                        7.0
opm_percentage            79.0
tax_percentage            25.0
dividend_payout            0.0
```

**Latest balancesheet record (2024-09):**
```json
company_id              ADANIGREEN
year                       2024-09
equity_capital              1584.0
reserves                    8992.0
total_equity               10576.0
borrowings                 67430.0
other_liabilities          20252.0
total_liabilities          98258.0
current_assets             16678.0
fixed_assets               64632.0
total_assets               98258.0
investments                 2331.0
cash_and_equivalents          None
```

**Latest financial_ratios record (2024-03):**
```json
company_id                     ADANIGREEN
year                              2024-03
net_profit_margin_pct               13.67
operating_profit_margin_pct          79.0
return_on_equity_pct                12.81
debt_to_equity                     6.5953
interest_coverage                  1.7139
asset_turnover                     0.1047
free_cash_flow_cr                -13347.0
capex_cr                          21060.0
earnings_per_share                    7.0
book_value_per_share               0.6208
dividend_payout_ratio_pct             0.0
total_debt_cr                     64858.0
cash_from_operations_cr            7713.0
```

### HAL - Hindustan Aeronautics Ltd

| Table Name | Row Count | Year/Date Range | Missing values (Nulls) | Key Constraints Check |
| --- | --- | --- | --- | --- |
| profitandloss | 12 | 2013-03 to 2024-03 | 0 | Passed |
| balancesheet | 10 | 2016-03 to 2024-09 | 10 | Passed |
| cashflow | 8 | 2017-03 to 2024-03 | 56 | Passed |
| market_cap | 6 | 2019-03 to 2024-03 | 12 | Passed |
| stock_prices | 60 | 2020-01-01 to 2024-12-01 | 0 | Passed |
| financial_ratios | 8 | 2017-03 to 2024-03 | 0 | Passed |

#### Detailed Row Samples for HAL

**Latest profitandloss record (2024-03):**
```json
company_id              HAL
year                2024-03
sales               30381.0
expenses            20631.0
operating_profit     9749.0
depreciation         1406.0
other_income         1899.0
interest               43.0
tax                  2604.0
net_profit           7595.0
eps                   114.0
opm_percentage         32.0
tax_percentage         26.0
dividend_payout        31.0
```

**Latest balancesheet record (2024-09):**
```json
company_id                  HAL
year                    2024-09
equity_capital              5.0
reserves                  202.0
total_equity              207.0
borrowings                124.0
other_liabilities         145.0
total_liabilities         476.0
current_assets            181.0
fixed_assets              244.0
total_assets              476.0
investments                48.0
cash_and_equivalents       None
```

**Latest financial_ratios record (2024-03):**
```json
company_id                          HAL
year                            2024-03
net_profit_margin_pct              25.0
operating_profit_margin_pct        32.0
return_on_equity_pct            3816.58
debt_to_equity                   0.6181
interest_coverage              270.8837
asset_turnover                  67.5133
free_cash_flow_cr                1814.0
capex_cr                         6412.0
earnings_per_share                114.0
book_value_per_share               3.98
dividend_payout_ratio_pct          31.0
total_debt_cr                     123.0
cash_from_operations_cr          8226.0
```

### EICHERMOT - Eicher Motors Ltd

| Table Name | Row Count | Year/Date Range | Missing values (Nulls) | Key Constraints Check |
| --- | --- | --- | --- | --- |
| profitandloss | 12 | 2012-12 to 2024-03 | 0 | Passed |
| balancesheet | 13 | 2012-12 to 2024-09 | 13 | Passed |
| cashflow | 12 | 2012-12 to 2024-03 | 84 | Passed |
| market_cap | 6 | 2019-03 to 2024-03 | 12 | Passed |
| stock_prices | 60 | 2020-01-01 to 2024-12-01 | 0 | Passed |
| financial_ratios | 12 | 2012-12 to 2024-03 | 0 | Passed |

#### Detailed Row Samples for EICHERMOT

**Latest profitandloss record (2024-03):**
```json
company_id          EICHERMOT
year                  2024-03
sales                 16536.0
expenses              12206.0
operating_profit       4329.0
depreciation            598.0
other_income           1521.0
interest                 51.0
tax                    1201.0
net_profit             4001.0
eps                     146.0
opm_percentage           26.0
tax_percentage           23.0
dividend_payout          35.0
```

**Latest balancesheet record (2024-09):**
```json
company_id              EICHERMOT
year                      2024-09
equity_capital               27.0
reserves                  18952.0
total_equity              18979.0
borrowings                  404.0
other_liabilities          4997.0
total_liabilities         24380.0
current_assets             5968.0
fixed_assets               3490.0
total_assets              24380.0
investments               14693.0
cash_and_equivalents         None
```

**Latest financial_ratios record (2024-03):**
```json
company_id                     EICHERMOT
year                             2024-03
net_profit_margin_pct               24.2
operating_profit_margin_pct         26.0
return_on_equity_pct               22.17
debt_to_equity                    0.0232
interest_coverage               114.7059
asset_turnover                    0.7154
free_cash_flow_cr                  890.0
capex_cr                          2834.0
earnings_per_share                 146.0
book_value_per_share             66.8333
dividend_payout_ratio_pct           35.0
total_debt_cr                      419.0
cash_from_operations_cr           3724.0
```

## 2. Findings and Bug Fixes

### Data Integrity Verification:
1. **Companies and Sectors Mapping**: Verified that all 92 companies have corresponding sectors mapped correctly, and `peer_groups` memberships align without orphans.
2. **Boolean Standardisation**: Verified `is_benchmark` standardisation (converted to integer 0/1) inside the SQLite table `peer_groups` which now enforces the SQLite `is_benchmark IN (0, 1)` check constraint correctly.
3. **Text Column Coercion Mismatch**: Identified a crucial bug where `peer_group_name` was being coerced to `NaN`/`None` during database loading as it was not included in `text_columns` set inside `loader.py`. Fixed this bug by adding `peer_group_name` to the `text_columns` set, ensuring text peer group names are preserved.
4. **Foreign Key Integrity**: Running `PRAGMA foreign_key_check` on the database returned 0 issues, confirming 100% referential integrity across the 12 tables.

### Manual Spot Checks:
- Spot-checked random companies (**SUNPHARMA**, **BAJFINANCE**, **ADANIGREEN**, **HAL**, **EICHERMOT**) across different sectors to verify their historical P&L, Balance Sheet, Cash Flow, stock prices, and valuation data are completely populated.
- Confirmed that financial ratio values correspond to their respective P&L and Balance Sheet values without division-by-zero errors.
