-- ==============================================================================
-- Nifty 100 Financial Intelligence Platform
-- Sprint 1 - D07 Deliverable: 10 SQL Exploratory Queries
-- Database: nifty100.db
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Top 10 Companies by 2024 Market Capitalization
-- Intent: Identify the largest companies in the index by market value.
-- ------------------------------------------------------------------------------
SELECT 
    id AS ticker,
    company_name,
    sector,
    market_cap_2024 AS mkt_cap_cr
FROM companies
ORDER BY market_cap_2024 DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 2: Broad Sector Distribution and Market Value
-- Intent: Count companies in each sector and sum their total market capitalization.
-- ------------------------------------------------------------------------------
SELECT 
    sector AS broad_sector,
    COUNT(*) AS company_count,
    ROUND(SUM(market_cap_2024), 2) AS total_mkt_cap_cr,
    ROUND(AVG(market_cap_2024), 2) AS avg_mkt_cap_cr
FROM companies
GROUP BY sector
ORDER BY total_mkt_cap_cr DESC;


-- ------------------------------------------------------------------------------
-- QUERY 3: Sector-Wise Financial Ratios (Latest Year)
-- Intent: Evaluate average margins, ROE, and ROCE across different sectors.
-- ------------------------------------------------------------------------------
WITH latest_ratios AS (
    SELECT 
        r.company_id,
        r.net_profit_margin_pct,
        r.operating_profit_margin_pct,
        r.return_on_equity_pct
    FROM financial_ratios r
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest ON r.company_id = latest.company_id AND r.year = latest.max_year
)
SELECT 
    c.sector AS broad_sector,
    COUNT(c.id) AS company_count,
    ROUND(AVG(lr.operating_profit_margin_pct), 2) AS avg_opm_pct,
    ROUND(AVG(lr.net_profit_margin_pct), 2) AS avg_npm_pct,
    ROUND(AVG(lr.return_on_equity_pct), 2) AS avg_roe_pct
FROM companies c
INNER JOIN latest_ratios lr ON c.id = lr.company_id
GROUP BY c.sector
ORDER BY avg_roe_pct DESC;


-- ------------------------------------------------------------------------------
-- QUERY 4: Top 10 Cash Generators by Free Cash Flow (Latest Year)
-- Intent: Find companies generating the highest free cash flow in absolute terms.
-- ------------------------------------------------------------------------------
WITH latest_fcf AS (
    SELECT 
        fr.company_id,
        fr.year,
        fr.free_cash_flow_cr,
        fr.cash_from_operations_cr,
        fr.capex_cr
    FROM financial_ratios fr
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest ON fr.company_id = latest.company_id AND fr.year = latest.max_year
)
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    lf.year,
    lf.cash_from_operations_cr AS cfo_cr,
    lf.capex_cr,
    lf.free_cash_flow_cr AS fcf_cr
FROM companies c
INNER JOIN latest_fcf lf ON c.id = lf.company_id
ORDER BY lf.free_cash_flow_cr DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 5: Consistent Performers (Positive NPM and FCF for Last 5 Years)
-- Intent: Filter companies that maintained positive profitability and FCF consistently.
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS ticker,
    c.company_name,
    COUNT(r.year) AS years_count,
    ROUND(MIN(r.net_profit_margin_pct), 2) AS min_npm_pct,
    ROUND(MIN(r.free_cash_flow_cr), 2) AS min_fcf_cr
FROM companies c
INNER JOIN financial_ratios r ON c.id = r.company_id
WHERE r.year >= '2020-03' 
  AND r.net_profit_margin_pct > 0 
  AND r.free_cash_flow_cr > 0
GROUP BY c.id, c.company_name
HAVING years_count >= 5
ORDER BY min_npm_pct DESC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Debt-to-Equity Analysis for Non-Financial Companies
-- Intent: Rank companies by leverage (Debt/Equity), excluding Banks/NBFCs.
-- ------------------------------------------------------------------------------
WITH latest_leverage AS (
    SELECT 
        r.company_id,
        r.year,
        r.debt_to_equity,
        r.total_debt_cr
    FROM financial_ratios r
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest ON r.company_id = latest.company_id AND r.year = latest.max_year
)
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    ll.year,
    ROUND(ll.debt_to_equity, 4) AS debt_to_equity,
    ll.total_debt_cr AS total_debt_cr
FROM companies c
INNER JOIN latest_leverage ll ON c.id = ll.company_id
WHERE c.sector NOT LIKE '%Financials%' 
  AND c.sector NOT LIKE '%Banks%'
ORDER BY ll.debt_to_equity DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 7: High-Growth Tickers (Revenue & PAT CAGR > 15% in Analysis sheet)
-- Intent: Spot double-engine growth companies from parsed growth metrics.
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    a.revenue_5yr_cagr AS rev_5y_cagr_pct,
    a.pat_5yr_cagr AS pat_5y_cagr_pct
FROM companies c
INNER JOIN analysis a ON c.id = a.company_id
WHERE a.revenue_5yr_cagr > 15.0 
  AND a.pat_5yr_cagr > 15.0
ORDER BY a.pat_5yr_cagr DESC;


-- ------------------------------------------------------------------------------
-- QUERY 8: Reasonable Valuation Filter (Low P/E with High ROE)
-- Intent: Identify potentially undervalued stocks with high returns on equity.
-- ------------------------------------------------------------------------------
WITH latest_valuation AS (
    SELECT 
        m.company_id,
        m.pe_ratio,
        m.year
    FROM market_cap m
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM market_cap
        GROUP BY company_id
    ) latest ON m.company_id = latest.company_id AND m.year = latest.max_year
),
latest_roe AS (
    SELECT 
        r.company_id,
        r.return_on_equity_pct
    FROM financial_ratios r
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest ON r.company_id = latest.company_id AND r.year = latest.max_year
)
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    ROUND(v.pe_ratio, 2) AS pe_ratio,
    ROUND(lr.return_on_equity_pct, 2) AS roe_pct
FROM companies c
INNER JOIN latest_valuation v ON c.id = v.company_id
INNER JOIN latest_roe lr ON c.id = lr.company_id
WHERE v.pe_ratio > 0 
  AND v.pe_ratio < 25.0
  AND lr.return_on_equity_pct > 18.0
ORDER BY v.pe_ratio ASC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 9: Effective Tax Rate Outliers (Latest Year)
-- Intent: Detect companies with unusually high (>40%) or low (<10%) effective tax rates.
-- ------------------------------------------------------------------------------
WITH latest_pbt_tax AS (
    SELECT 
        pl.company_id,
        pl.year,
        pl.tax_percentage,
        pl.net_profit
    FROM profitandloss pl
    INNER JOIN (
        SELECT company_id, MAX(year) AS max_year
        FROM profitandloss
        GROUP BY company_id
    ) latest ON pl.company_id = latest.company_id AND pl.year = latest.max_year
)
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    t.year,
    ROUND(t.tax_percentage, 2) AS tax_percentage,
    t.net_profit AS net_profit_cr
FROM companies c
INNER JOIN latest_pbt_tax t ON c.id = t.company_id
WHERE (t.tax_percentage < 10.0 OR t.tax_percentage > 40.0)
  AND t.net_profit > 10.0 -- Ignore minor or loss-making companies
ORDER BY t.tax_percentage DESC;


-- ------------------------------------------------------------------------------
-- QUERY 10: Missing Annual Report Links by Company
-- Intent: Find companies in the system that do not have annual reports loaded.
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS ticker,
    c.company_name,
    c.sector,
    COUNT(d.id) AS report_count
FROM companies c
LEFT JOIN documents d ON c.id = d.company_id
GROUP BY c.id, c.company_name
HAVING report_count = 0
ORDER BY c.id ASC;
