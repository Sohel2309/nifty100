"""
REST API Module for Nifty 100 Financial Intelligence Platform
Implements all 16 specified analytical and CRUD endpoints using FastAPI.
Cleans float('nan') and inf values for JSON compliance.
"""

import os
import time
import math
import sqlite3
import pandas as pd
from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(
    title="Nifty 100 Financial Intelligence REST API",
    description="Fundamental analysis, KPI ratios, CAGR, and valuation endpoints for Nifty 100",
    version="1.0.0"
)

# Record server start time for health uptime
server_start_time = time.time()

def get_db_conn():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def clean_value(val: Any) -> Any:
    """Helper to convert float('nan') or inf values to None for JSON compliance"""
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val

def clean_dict(d: dict) -> dict:
    """Helper to recursively clean dictionary values"""
    return {k: clean_value(v) for k, v in d.items()}

def clean_records(records: List[dict]) -> List[dict]:
    """Helper to clean list of records"""
    return [clean_dict(r) for r in records]

# 1. GET /api/v1/companies -> List all 92 companies (supports ?sector= filter)
@app.get("/api/v1/companies", summary="List all companies")
def list_companies(sector: Optional[str] = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    
    if sector:
        query = """
            SELECT c.id, c.company_name, COALESCE(s.broad_sector, c.sector) as broad_sector, s.sub_sector
            FROM companies c
            LEFT JOIN sectors s ON c.id = s.company_id
            WHERE s.broad_sector = ? OR c.sector = ?
        """
        cursor.execute(query, (sector, sector))
    else:
        query = """
            SELECT c.id, c.company_name, COALESCE(s.broad_sector, c.sector) as broad_sector, s.sub_sector
            FROM companies c
            LEFT JOIN sectors s ON c.id = s.company_id
        """
        cursor.execute(query)
        
    rows = cursor.fetchall()
    conn.close()
    
    return clean_records([dict(r) for r in rows])

# 2. GET /api/v1/companies/{ticker} -> Full company profile: KPIs, pros/cons, sector, description
@app.get("/api/v1/companies/{ticker}", summary="Get company profile")
def get_company(ticker: str):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # Check if company exists
    cursor.execute("SELECT * FROM companies WHERE id = ?", (ticker_clean,))
    co = cursor.fetchone()
    if not co:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker_clean}' not found.")
        
    # Get sector info
    cursor.execute("SELECT broad_sector, sub_sector FROM sectors WHERE company_id = ?", (ticker_clean,))
    sec = cursor.fetchone()
    broad_sector = sec['broad_sector'] if sec else co['sector']
    sub_sector = sec['sub_sector'] if sec else co['sub_sector']
    
    # Get pros/cons
    cursor.execute("SELECT pros, cons FROM prosandcons WHERE company_id = ?", (ticker_clean,))
    pc = cursor.fetchone()
    
    conn.close()
    
    res = dict(co)
    res['broad_sector'] = broad_sector
    res['sub_sector'] = sub_sector
    res['pros'] = pc['pros'] if pc else None
    res['cons'] = pc['cons'] if pc else None
    return clean_dict(res)

# 3. GET /api/v1/companies/{ticker}/pl -> P&L history
@app.get("/api/v1/companies/{ticker}/pl", summary="Get P&L history")
def get_pl_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    query = "SELECT * FROM profitandloss WHERE company_id = ?"
    params = [ticker_clean]
    
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
        
    query += " ORDER BY year"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No P&L data found for ticker '{ticker_clean}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 4. GET /api/v1/companies/{ticker}/bs -> Balance sheet history
@app.get("/api/v1/companies/{ticker}/bs", summary="Get Balance Sheet history")
def get_bs_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    query = "SELECT * FROM balancesheet WHERE company_id = ?"
    params = [ticker_clean]
    
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
        
    query += " ORDER BY year"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Balance Sheet data found for ticker '{ticker_clean}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 5. GET /api/v1/companies/{ticker}/cashflow -> Cash flow history
@app.get("/api/v1/companies/{ticker}/cashflow", summary="Get Cash Flow history")
def get_cf_history(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    query = "SELECT * FROM cashflow WHERE company_id = ?"
    params = [ticker_clean]
    
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
        
    query += " ORDER BY year"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Cash Flow data found for ticker '{ticker_clean}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 6. GET /api/v1/companies/{ticker}/ratios -> Pre-computed KPIs
@app.get("/api/v1/companies/{ticker}/ratios", summary="Get calculated financial ratios")
def get_ratios(ticker: str, year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    if year:
        query = "SELECT * FROM financial_ratios WHERE company_id = ? AND year = ?"
        params = [ticker_clean, year]
    else:
        query = "SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year"
        params = [ticker_clean]
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No ratio records found for ticker '{ticker_clean}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 7. GET /api/v1/companies/{ticker}/tearsheet -> Binary PDF download stream
@app.get("/api/v1/companies/{ticker}/tearsheet", summary="Download company tearsheet PDF")
def download_tearsheet(ticker: str):
    ticker_clean = ticker.strip().upper()
    pdf_path = f"reports/tearsheets/{ticker_clean}_tearsheet.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF Tearsheet not pre-generated for ticker '{ticker_clean}'.")
        
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"{ticker_clean}_tearsheet.pdf"
    )

# 8. GET /api/v1/screener -> Filtering endpoint consistent with screener engine
@app.get("/api/v1/screener", summary="Stock Screener API")
def run_screener(
    min_roe: Optional[float] = None,
    max_de: Optional[float] = None,
    min_fcf: Optional[float] = None,
    sector: Optional[str] = None,
    min_rev_cagr_5yr: Optional[float] = None,
    min_pat_cagr_5yr: Optional[float] = None,
    max_pe: Optional[float] = None
):
    conn = get_db_conn()
    latest_year = "2024-03"
    
    # Load all ratios, analysis, and market cap
    query = f"""
        SELECT 
            c.id as Ticker, 
            c.company_name as CompanyName, 
            COALESCE(s.broad_sector, c.sector) as Sector,
            r.return_on_equity_pct as ROE, 
            r.debt_to_equity as DE,
            r.free_cash_flow_cr as FCF,
            a.revenue_5yr_cagr as RevCAGR,
            a.pat_5yr_cagr as PatCAGR,
            m.pe_ratio as PE
        FROM companies c
        LEFT JOIN sectors s ON c.id = s.company_id
        LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
        LEFT JOIN analysis a ON c.id = a.company_id
        LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Filter
    if min_roe is not None:
        df = df[df['ROE'] >= min_roe]
    if max_de is not None:
        df = df[df['DE'] <= max_de]
    if min_fcf is not None:
        df = df[df['FCF'] >= min_fcf]
    if sector:
        df = df[df['Sector'] == sector]
    if min_rev_cagr_5yr is not None:
        df = df[df['RevCAGR'] >= min_rev_cagr_5yr]
    if min_pat_cagr_5yr is not None:
        df = df[df['PatCAGR'] >= min_pat_cagr_5yr]
    if max_pe is not None:
        df = df[df['PE'] <= max_pe]
        
    return clean_records(df.to_dict(orient='records'))

# 9. GET /api/v1/sectors -> List all 11 sectors with counts and medians
@app.get("/api/v1/sectors", summary="Get Sector Summaries")
def get_sectors():
    conn = get_db_conn()
    latest_year = "2024-03"
    
    query = f"""
        SELECT 
            COALESCE(s.broad_sector, c.sector) as Sector,
            r.return_on_equity_pct as ROE,
            m.pe_ratio as PE,
            r.debt_to_equity as DE
        FROM companies c
        LEFT JOIN sectors s ON c.id = s.company_id
        LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = '{latest_year}'
        LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = '{latest_year}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return []
        
    summary = []
    for sec_name, group in df.groupby('Sector'):
        summary.append({
            'sector_name': sec_name,
            'company_count': len(group),
            'median_roe': group['ROE'].median(),
            'median_pe': group['PE'].median(),
            'median_de': group['DE'].median()
        })
        
    return clean_records(summary)

# 10. GET /api/v1/sectors/{sector}/companies -> All companies in sector with top KPIs
@app.get("/api/v1/sectors/{sector}/companies", summary="Get companies in a sector")
def get_sector_companies(sector: str, year: str = "2024-03"):
    conn = get_db_conn()
    
    query = """
        SELECT 
            c.id as Ticker,
            c.company_name as CompanyName,
            r.return_on_equity_pct as ROE,
            r.net_profit_margin_pct as NPM,
            r.debt_to_equity as DE,
            r.interest_coverage as ICR,
            r.free_cash_flow_cr as FCF,
            m.pe_ratio as PE
        FROM companies c
        JOIN sectors s ON c.id = s.company_id
        LEFT JOIN financial_ratios r ON c.id = r.company_id AND r.year = ?
        LEFT JOIN market_cap m ON c.id = m.company_id AND m.year = ?
        WHERE s.broad_sector = ?
    """
    df = pd.read_sql_query(query, conn, params=[year, year, sector])
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No companies found in sector '{sector}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 11. GET /api/v1/peers/{group_name} -> Percentile rankings in peer group
@app.get("/api/v1/peers/{group_name}", summary="Get peer percentile ranks")
def get_peers(group_name: str, year: str = "2024-03"):
    conn = get_db_conn()
    
    query = """
        SELECT *
        FROM peer_percentiles
        WHERE peer_group_name = ? AND year = ?
    """
    df = pd.read_sql_query(query, conn, params=[group_name, year])
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No percentile ranks found for group '{group_name}' in {year}.")
        
    return clean_records(df.to_dict(orient='records'))

# 12. GET /api/v1/companies/{ticker}/peers/compare -> Radar data
@app.get("/api/v1/companies/{ticker}/peers/compare", summary="Get peer comparison radar metrics")
def compare_peers(ticker: str, year: str = "2024-03"):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # Get company peer group name
    cursor.execute("SELECT peer_group_name FROM peer_groups WHERE company_id = ?", (ticker_clean,))
    grp = cursor.fetchone()
    if not grp:
        conn.close()
        raise HTTPException(status_code=404, detail=f"No peer group assigned for ticker '{ticker_clean}'.")
        
    group_name = grp['peer_group_name']
    
    # Fetch all percentiles in this group
    df_pct = pd.read_sql_query(
        "SELECT * FROM peer_percentiles WHERE peer_group_name = ? AND year = ?",
        conn, params=[group_name, year]
    )
    conn.close()
    
    # Get current company values
    df_co = df_pct[df_pct['company_id'] == ticker_clean]
    if df_co.empty:
        raise HTTPException(status_code=404, detail=f"No percentiles found for '{ticker_clean}' in {year}.")
        
    # Get benchmark company values
    df_bench = df_pct[df_pct['is_benchmark'] == 1]
    
    # 8 axes list
    axes_cols = [
        'return_on_equity_pct_pr', 'net_profit_margin_pct_pr', 'debt_to_equity_pr',
        'interest_coverage_pr', 'free_cash_flow_cr_pr', 'pat_5yr_cagr_pr',
        'revenue_5yr_cagr_pr', 'eps_5yr_cagr_pr'
    ]
    
    res = {
        'company_id': ticker_clean,
        'peer_group': group_name,
        'company_values': df_co[axes_cols].iloc[0].to_dict(),
        'peer_averages': df_pct[axes_cols].mean().to_dict(),
        'benchmark_company': df_bench['company_id'].values[0] if not df_bench.empty else None,
        'benchmark_values': df_bench[axes_cols].iloc[0].to_dict() if not df_bench.empty else {}
    }
    
    return clean_dict(res)

# 13. GET /api/v1/market-cap/{ticker} -> Valuation multiples
@app.get("/api/v1/market-cap/{ticker}", summary="Get historical multiples")
def get_multiples(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    query = "SELECT year, market_cap_cr, pe_ratio, pb_ratio, ev_ebitda, dividend_yield FROM market_cap WHERE company_id = ?"
    params = [ticker_clean]
    
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
        
    query += " ORDER BY year"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No market cap details found for ticker '{ticker_clean}'.")
        
    return clean_records(df.to_dict(orient='records'))

# 14. GET /api/v1/portfolio/stats -> Percentiles P10-P90 across all 92
@app.get("/api/v1/portfolio/stats", summary="Get portfolio statistics")
def get_portfolio_stats():
    # Load portfolio_stats.csv
    csv_path = "output/portfolio_stats.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Portfolio statistics not calculated.")
    df = pd.read_csv(csv_path)
    return clean_records(df.to_dict(orient='records'))

# 15. GET /api/v1/companies/{ticker}/documents -> Annual report links
@app.get("/api/v1/companies/{ticker}/documents", summary="Get filing documents")
def get_documents(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    ticker_clean = ticker.strip().upper()
    conn = get_db_conn()
    
    query = "SELECT year, document_name, document_url, document_type FROM documents WHERE company_id = ?"
    params = [ticker_clean]
    
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
        
    query += " ORDER BY year DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No document filings found for ticker '{ticker_clean}'.")
        
    # Append boolean is_url_valid
    records = []
    for _, row in df.iterrows():
        records.append({
            'year': row['year'],
            'Annual_Report': row['document_url'],
            'document_name': row['document_name'],
            'document_type': row['document_type'],
            'is_url_valid': True if (row['document_url'] and row['document_url'].startswith('http')) else False
        })
        
    return clean_records(records)

# 16. GET /api/v1/health -> DB row counts, server uptime
@app.get("/api/v1/health", summary="Health check")
def health_check():
    conn = get_db_conn()
    cursor = conn.cursor()
    
    tables = [
        'companies', 'profitandloss', 'balancesheet', 'cashflow',
        'analysis', 'documents', 'prosandcons', 'sectors',
        'stock_prices', 'market_cap'
    ]
    
    row_counts = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_counts[table] = cursor.fetchone()[0]
        except Exception:
            row_counts[table] = -1
            
    conn.close()
    
    uptime = time.time() - server_start_time
    
    return clean_dict({
        'status': 'ok',
        'db_row_counts': row_counts,
        'uptime_seconds': int(uptime),
        'version': '1.0.0'
    })
