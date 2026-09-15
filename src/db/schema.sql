-- ============================================================
-- Nifty 100 Financial Intelligence Platform
-- SQLite Database Schema (10 Tables with Foreign Key Constraints)
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ============================================================
-- TABLE 1: companies (Reference - 92 companies)
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    sub_sector TEXT,
    market_cap_2024 REAL,
    face_value REAL,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    company_logo TEXT,
    about_company TEXT,
    chart_link TEXT,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_ticker CHECK (id != '' AND id = UPPER(id))
);

CREATE INDEX idx_companies_sector ON companies(sector);

-- ============================================================
-- TABLE 2: profitandloss (Time-Series - P&L Statement)
-- ============================================================
CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    sales REAL NOT NULL,
    expenses REAL NOT NULL,
    operating_profit REAL,
    depreciation REAL,
    other_income REAL,
    interest REAL,
    tax REAL,
    net_profit REAL NOT NULL,
    eps REAL,
    opm_percentage REAL,
    tax_percentage REAL,
    dividend_payout REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT unique_pl CHECK (company_id != '' AND year != ''),
    UNIQUE(company_id, year)
);

CREATE INDEX idx_pl_company_year ON profitandloss(company_id, year);
CREATE INDEX idx_pl_year ON profitandloss(year);

-- ============================================================
-- TABLE 3: balancesheet (Time-Series - Balance Sheet Statement)
-- ============================================================
CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    equity_capital REAL NOT NULL,
    reserves REAL,
    total_equity REAL,
    borrowings REAL NOT NULL,
    other_liabilities REAL,
    total_liabilities REAL NOT NULL,
    current_assets REAL,
    fixed_assets REAL,
    total_assets REAL NOT NULL,
    investments REAL,
    cash_and_equivalents REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT unique_bs CHECK (company_id != '' AND year != ''),
    UNIQUE(company_id, year)
);

CREATE INDEX idx_bs_company_year ON balancesheet(company_id, year);
CREATE INDEX idx_bs_year ON balancesheet(year);

-- ============================================================
-- TABLE 4: cashflow (Time-Series - Cash Flow Statement)
-- ============================================================
CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    operating_activity REAL NOT NULL,
    depreciation_added_back REAL,
    working_capital_change REAL,
    investing_activity REAL,
    capital_expenditure REAL,
    acquisitions REAL,
    financing_activity REAL,
    dividends_paid REAL,
    debt_raised REAL,
    debt_repaid REAL,
    net_cash_flow REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT unique_cf CHECK (company_id != '' AND year != ''),
    UNIQUE(company_id, year)
);

CREATE INDEX idx_cf_company_year ON cashflow(company_id, year);
CREATE INDEX idx_cf_year ON cashflow(year);

-- ============================================================
-- TABLE 5: analysis (Reference - Pre-computed growth metrics per company)
-- ============================================================
CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL UNIQUE,
    revenue_3yr_cagr REAL,
    revenue_5yr_cagr REAL,
    revenue_10yr_cagr REAL,
    pat_3yr_cagr REAL,
    pat_5yr_cagr REAL,
    pat_10yr_cagr REAL,
    eps_3yr_cagr REAL,
    eps_5yr_cagr REAL,
    eps_10yr_cagr REAL,
    roe_5yr_avg REAL,
    roic_5yr_avg REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX idx_analysis_company ON analysis(company_id);

-- ============================================================
-- TABLE 6: documents (Reference - Annual report links)
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    document_name TEXT,
    document_url TEXT NOT NULL,
    document_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

CREATE INDEX idx_documents_company_year ON documents(company_id, year);

-- ============================================================
-- TABLE 7: prosandcons (Reference - Qualitative insights per company)
-- ============================================================
CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL UNIQUE,
    pros TEXT,
    cons TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX idx_proscons_company ON prosandcons(company_id);

-- ============================================================
-- TABLE 8: sectors (Reference - Sector/subsector mapping - 11 broad + N sub)
-- ============================================================
CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL UNIQUE,
    broad_sector TEXT NOT NULL,
    sub_sector TEXT,
    peer_group TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX idx_sectors_broad ON sectors(broad_sector);
CREATE INDEX idx_sectors_company ON sectors(company_id);

-- ============================================================
-- TABLE 9: stock_prices (Time-Series - OHLCV data Jan 2020-Dec 2024)
-- ============================================================
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, date)
);

CREATE INDEX idx_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX idx_prices_date ON stock_prices(date);

-- ============================================================
-- TABLE 10: market_cap (Time-Series - Valuation data 2019-2024)
-- ============================================================
CREATE TABLE IF NOT EXISTS market_cap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    market_cap_cr REAL NOT NULL,
    earnings_cr REAL,
    book_value_cr REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,
    dividend_yield REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

CREATE INDEX idx_mkt_company_year ON market_cap(company_id, year);
CREATE INDEX idx_mkt_year ON market_cap(year);


-- ============================================================
-- TABLE 11: financial_ratios (Time-Series - Pre-computed ratios)
-- ============================================================
CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    capex_cr REAL,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT unique_ratios CHECK (company_id != '' AND year != ''),
    UNIQUE(company_id, year)
);

CREATE INDEX idx_ratios_company_year ON financial_ratios(company_id, year);
CREATE INDEX idx_ratios_year ON financial_ratios(year);

-- ============================================================
-- TABLE 12: peer_groups (Reference - Peer comparison groups)
-- ============================================================
CREATE TABLE IF NOT EXISTS peer_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_group_name TEXT NOT NULL,
    company_id TEXT NOT NULL,
    is_benchmark BOOLEAN NOT NULL CHECK (is_benchmark IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(peer_group_name, company_id)
);

CREATE INDEX idx_peergroups_name ON peer_groups(peer_group_name);
CREATE INDEX idx_peergroups_company ON peer_groups(company_id);

-- ============================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================

-- View: Complete company profile with latest KPIs
CREATE VIEW IF NOT EXISTS v_company_profile AS
SELECT 
    c.id,
    c.company_name,
    c.sector,
    s.broad_sector,
    s.sub_sector,
    s.peer_group,
    c.market_cap_2024,
    c.roe_percentage,
    c.roce_percentage,
    a.revenue_5yr_cagr,
    a.pat_5yr_cagr,
    a.roe_5yr_avg
FROM companies c
LEFT JOIN sectors s ON c.id = s.company_id
LEFT JOIN analysis a ON c.id = a.company_id;

-- View: Latest financials per company (most recent year)
CREATE VIEW IF NOT EXISTS v_latest_financials AS
WITH latest_years AS (
    SELECT company_id, MAX(year) as max_year
    FROM profitandloss
    GROUP BY company_id
)
SELECT 
    pl.company_id,
    pl.year,
    pl.sales,
    pl.operating_profit,
    pl.net_profit,
    pl.eps,
    bs.total_assets,
    bs.total_equity,
    bs.borrowings,
    cf.operating_activity,
    mm.pe_ratio,
    mm.market_cap_cr
FROM profitandloss pl
LEFT JOIN balancesheet bs ON pl.company_id = bs.company_id AND pl.year = bs.year
LEFT JOIN cashflow cf ON pl.company_id = cf.company_id AND pl.year = cf.year
LEFT JOIN market_cap mm ON pl.company_id = mm.company_id AND pl.year = mm.year
WHERE (pl.company_id, pl.year) IN (SELECT company_id, max_year FROM latest_years);

-- ============================================================
-- TRIGGERS FOR AUDIT TIMESTAMPS
-- ============================================================

CREATE TRIGGER IF NOT EXISTS tr_companies_updated
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_profitandloss_updated
AFTER UPDATE ON profitandloss
BEGIN
    UPDATE profitandloss SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_balancesheet_updated
AFTER UPDATE ON balancesheet
BEGIN
    UPDATE balancesheet SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_cashflow_updated
AFTER UPDATE ON cashflow
BEGIN
    UPDATE cashflow SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_financial_ratios_updated
AFTER UPDATE ON financial_ratios
BEGIN
    UPDATE financial_ratios SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_peer_groups_updated
AFTER UPDATE ON peer_groups
BEGIN
    UPDATE peer_groups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================
-- INITIALIZATION COMMENTS
-- ============================================================
-- Schema Version: 1.1
-- Created: 2026-06-19
-- Tables: 12 (core + supplementary)
-- Views: 2 (common queries)
-- Triggers: 6 (audit timestamp maintenance)
--
-- Key Constraints:
-- - ALL TEXT IDs: company_id = UPPERCASE, normalized
-- - ALL YEAR VALUES: YYYY-MM format (e.g., 2023-03 for Mar-23)
-- - FK CASCADE: Delete company → cascades to all related records
-- - PRAGMA foreign_keys = ON: Enforced on connection
-- - PRAGMA journal_mode = WAL: Write-Ahead Logging for concurrency
--
-- Time-Series Tables (profitandloss, balancesheet, cashflow, stock_prices, market_cap, financial_ratios):
-- - Composite unique (company_id, year/date)
-- - Indexed on (company_id, year/date) for fast joins
--
-- Reference Tables (companies, analysis, documents, prosandcons, sectors, peer_groups):
-- - Single unique/composite unique reference mappings
-- - No time-series versioning
-- ============================================================
