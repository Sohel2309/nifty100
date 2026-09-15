"""
Orchestration Script to Compute and Populate Financial Ratios and CAGR Growth Metrics
Reads historical financial data from SQLite db, calculates KPIs, and updates database tables.
"""

import os
import sqlite3
import logging
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

from src.analytics.ratios import (
    calculate_npm,
    calculate_opm,
    calculate_roe,
    calculate_roce,
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_asset_turnover,
    calculate_book_value_per_share
)
from src.analytics.cagr import (
    calculate_cagr_for_company,
    calculate_average_metric
)
from src.analytics.cashflow_kpis import (
    calculate_fcf,
    calculate_capex,
    classify_capital_allocation
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_connection(db_path: str) -> sqlite3.Connection:
    """Get connection with foreign keys enabled"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def setup_directories():
    """Ensure output and logs directories exist"""
    Path("output").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

def compute_all_ratios(db_path: str) -> List[dict]:
    """
    Computes all financial ratios for all company-year combinations.
    Writes edge cases to logs and outputs.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Fetch companies reference mapping (sectors & face value)
    cursor.execute("""
        SELECT c.id, c.face_value, s.broad_sector 
        FROM companies c
        LEFT JOIN sectors s ON c.id = s.company_id
    """)
    companies_ref = {row[0]: {"face_value": row[1], "broad_sector": row[2]} for row in cursor.fetchall()}
    
    # 2. Load core financial statements into pandas to merge them
    df_pl = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    df_bs = pd.read_sql_query("SELECT * FROM balancesheet", conn)
    df_cf = pd.read_sql_query("SELECT * FROM cashflow", conn)
    
    conn.close()
    
    # Standardize company_id and year
    for df in [df_pl, df_bs, df_cf]:
        if not df.empty:
            df['company_id'] = df['company_id'].str.strip().str.upper()
            df['year'] = df['year'].str.strip()
            
    # Merge datasets
    merged = pd.merge(df_pl, df_bs, on=['company_id', 'year'], how='outer', suffixes=('_pl', '_bs'))
    merged = pd.merge(merged, df_cf, on=['company_id', 'year'], how='outer')
    
    if merged.empty:
        logger.warning("No data found to compute ratios.")
        return []
        
    records_to_insert = []
    edge_cases = []
    capital_allocation_records = []
    
    for _, row in merged.iterrows():
        company_id = row['company_id']
        year = row['year']
        
        # Skip rows where either company_id or year is missing
        if pd.isna(company_id) or pd.isna(year):
            continue
            
        ref = companies_ref.get(company_id, {"face_value": 10.0, "broad_sector": "Unknown"})
        face_value = ref["face_value"]
        broad_sector = ref["broad_sector"]
        
        # Extract inputs safely
        sales = row.get('sales')
        net_profit = row.get('net_profit')
        operating_profit = row.get('operating_profit')
        depreciation = row.get('depreciation')
        other_income = row.get('other_income')
        interest = row.get('interest')
        equity_capital = row.get('equity_capital')
        reserves = row.get('reserves')
        borrowings = row.get('borrowings')
        total_assets = row.get('total_assets')
        reported_opm = row.get('opm_percentage')
        eps = row.get('eps')
        dividend_payout = row.get('dividend_payout')
        
        operating_activity = row.get('operating_activity')
        investing_activity = row.get('investing_activity')
        financing_activity = row.get('financing_activity')
        
        # Perform calculations
        npm = calculate_npm(net_profit, sales)
        opm = calculate_opm(operating_profit, sales, reported_opm, company_id, year)
        roe = calculate_roe(net_profit, equity_capital, reserves)
        roce = calculate_roce(operating_profit, depreciation, equity_capital, reserves, borrowings)
        de = calculate_debt_to_equity(borrowings, equity_capital, reserves)
        icr = calculate_interest_coverage(operating_profit, other_income, interest)
        asset_turnover = calculate_asset_turnover(sales, total_assets)
        
        # Cash Flow calculations
        fcf = calculate_fcf(operating_activity, investing_activity)
        capex = calculate_capex(investing_activity)
        bv_share = calculate_book_value_per_share(equity_capital, reserves, face_value)
        
        # Check leverage edge cases for non-financials
        if de is not None and de > 5.0 and broad_sector != 'Financials':
            edge_cases.append(
                f"[Leverage Warning] Co: {company_id}, Year: {year} | Broad Sector: {broad_sector} | Debt-to-Equity is {de:.2f} (> 5.0)"
            )
            
        # Classify Capital Allocation
        allocation_pattern = classify_capital_allocation(operating_activity, investing_activity, financing_activity)
        capital_allocation_records.append({
            'company_id': company_id,
            'year': year,
            'cfo': operating_activity,
            'cfi': investing_activity,
            'cff': financing_activity,
            'pattern': allocation_pattern
        })
        
        # Record for database
        records_to_insert.append({
            'company_id': company_id,
            'year': year,
            'net_profit_margin_pct': npm,
            'operating_profit_margin_pct': opm,
            'return_on_equity_pct': roe,
            'debt_to_equity': de,
            'interest_coverage': icr,
            'asset_turnover': asset_turnover,
            'free_cash_flow_cr': fcf,
            'capex_cr': capex,
            'earnings_per_share': eps,
            'book_value_per_share': bv_share,
            'dividend_payout_ratio_pct': dividend_payout,
            'total_debt_cr': borrowings,
            'cash_from_operations_cr': operating_activity
        })
        
    # Write edge cases log
    with open('output/ratio_edge_cases.log', 'w', encoding='utf-8') as f:
        f.write("=== FINANCIAL RATIO EDGE CASES LOG ===\n\n")
        for ec in edge_cases:
            f.write(ec + "\n")
            
    # Write capital allocation csv
    keys = ['company_id', 'year', 'cfo', 'cfi', 'cff', 'pattern']
    with open('output/capital_allocation.csv', 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(capital_allocation_records)
        
    logger.info(f"Computed ratios for {len(records_to_insert)} records.")
    return records_to_insert

def populate_ratios_db(db_path: str, records: List[dict]):
    """Insert or replace ratio records in financial_ratios table"""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Clear existing rows to avoid stale data
    cursor.execute("DELETE FROM financial_ratios")
    
    insert_sql = """
        INSERT INTO financial_ratios (
            company_id, year, net_profit_margin_pct, operating_profit_margin_pct,
            return_on_equity_pct, debt_to_equity, interest_coverage, asset_turnover,
            free_cash_flow_cr, capex_cr, earnings_per_share, book_value_per_share,
            dividend_payout_ratio_pct, total_debt_cr, cash_from_operations_cr
        ) VALUES (
            :company_id, :year, :net_profit_margin_pct, :operating_profit_margin_pct,
            :return_on_equity_pct, :debt_to_equity, :interest_coverage, :asset_turnover,
            :free_cash_flow_cr, :capex_cr, :earnings_per_share, :book_value_per_share,
            :dividend_payout_ratio_pct, :total_debt_cr, :cash_from_operations_cr
        )
    """
    
    cursor.executemany(insert_sql, records)
    conn.commit()
    conn.close()
    logger.info(f"Populated financial_ratios table in SQLite with {len(records)} rows.")

def compute_and_populate_cagr(db_path: str):
    """
    Computes CAGR (3yr, 5yr, 10yr) for Revenue, PAT, and EPS, 
    and 5yr averages for ROE and ROCE.
    Populates the analysis table.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Load all needed data from db
    df_pl = pd.read_sql_query("SELECT company_id, year, sales, net_profit, eps, operating_profit, depreciation FROM profitandloss", conn)
    df_ratios = pd.read_sql_query("SELECT company_id, year, return_on_equity_pct FROM financial_ratios", conn)
    
    # For ROCE 5yr average, we need to calculate ROCE first or fetch from financial_ratios table.
    # Wait, does the financial_ratios table have ROCE? No, it has net_profit_margin_pct, return_on_equity_pct, etc.
    # Wait! Let's check ROCE. ROCE is EBIT / Capital Employed.
    # Let's compute ROCE for each company-year using balancesheet and profitandloss tables
    df_bs = pd.read_sql_query("SELECT company_id, year, equity_capital, reserves, borrowings FROM balancesheet", conn)
    
    conn.close()
    
    # Standardize dataframes
    for df in [df_pl, df_ratios, df_bs]:
        df['company_id'] = df['company_id'].str.strip().str.upper()
        df['year'] = df['year'].str.strip()
        
    # Calculate ROCE for each year
    df_roce = pd.merge(df_pl[['company_id', 'year', 'operating_profit', 'depreciation']], df_bs, on=['company_id', 'year'], how='inner')
    df_roce['roce'] = df_roce.apply(
        lambda r: calculate_roce(r['operating_profit'], r['depreciation'], r['equity_capital'], r['reserves'], r['borrowings']),
        axis=1
    )
    
    companies = df_pl['company_id'].unique()
    analysis_records = []
    cagr_edge_cases = []
    
    for company_id in companies:
        co_pl = df_pl[df_pl['company_id'] == company_id]
        co_ratios = df_ratios[df_ratios['company_id'] == company_id]
        co_roce = df_roce[df_roce['company_id'] == company_id]
        
        if co_pl.empty:
            continue
            
        # Sort values by year
        co_pl = co_pl.sort_values('year')
        co_ratios = co_ratios.sort_values('year')
        co_roce = co_roce.sort_values('year')
        
        # Determine the latest year of data for this company
        latest_year = co_pl['year'].max()
        
        # Prepare dictionaries for lookup
        sales_dict = dict(zip(co_pl['year'], co_pl['sales']))
        pat_dict = dict(zip(co_pl['year'], co_pl['net_profit']))
        eps_dict = dict(zip(co_pl['year'], co_pl['eps']))
        
        roe_dict = dict(zip(co_ratios['year'], co_ratios['return_on_equity_pct']))
        roce_dict = dict(zip(co_roce['year'], co_roce['roce']))
        
        # Compute CAGR values
        rev_3yr, t_rev_3 = calculate_cagr_for_company(sales_dict, latest_year, 3, company_id, "Revenue")
        rev_5yr, t_rev_5 = calculate_cagr_for_company(sales_dict, latest_year, 5, company_id, "Revenue")
        rev_10yr, t_rev_10 = calculate_cagr_for_company(sales_dict, latest_year, 10, company_id, "Revenue")
        
        pat_3yr, t_pat_3 = calculate_cagr_for_company(pat_dict, latest_year, 3, company_id, "PAT")
        pat_5yr, t_pat_5 = calculate_cagr_for_company(pat_dict, latest_year, 5, company_id, "PAT")
        pat_10yr, t_pat_10 = calculate_cagr_for_company(pat_dict, latest_year, 10, company_id, "PAT")
        
        eps_3yr, t_eps_3 = calculate_cagr_for_company(eps_dict, latest_year, 3, company_id, "EPS")
        eps_5yr, t_eps_5 = calculate_cagr_for_company(eps_dict, latest_year, 5, company_id, "EPS")
        eps_10yr, t_eps_10 = calculate_cagr_for_company(eps_dict, latest_year, 10, company_id, "EPS")
        
        # Averages
        roe_5yr_avg = calculate_average_metric(roe_dict, latest_year, 5)
        roic_5yr_avg = calculate_average_metric(roce_dict, latest_year, 5) # stored as roic_5yr_avg
        
        # Log turnaround edge cases
        for metric, flag, years in [
            ("Revenue", t_rev_3, 3), ("Revenue", t_rev_5, 5), ("Revenue", t_rev_10, 10),
            ("PAT", t_pat_3, 3), ("PAT", t_pat_5, 5), ("PAT", t_pat_10, 10),
            ("EPS", t_eps_3, 3), ("EPS", t_eps_5, 5), ("EPS", t_eps_10, 10)
        ]:
            if flag:
                cagr_edge_cases.append(
                    f"[CAGR Turnaround Warning] Co: {company_id} | Metric: {metric} | Period: {years}yr"
                )
                
        analysis_records.append({
            'company_id': company_id,
            'revenue_3yr_cagr': rev_3yr,
            'revenue_5yr_cagr': rev_5yr,
            'revenue_10yr_cagr': rev_10yr,
            'pat_3yr_cagr': pat_3yr,
            'pat_5yr_cagr': pat_5yr,
            'pat_10yr_cagr': pat_10yr,
            'eps_3yr_cagr': eps_3yr,
            'eps_5yr_cagr': eps_5yr,
            'eps_10yr_cagr': eps_10yr,
            'roe_5yr_avg': roe_5yr_avg,
            'roic_5yr_avg': roic_5yr_avg
        })
        
    # Append CAGR turnaround logs to edge cases log
    with open('output/ratio_edge_cases.log', 'a', encoding='utf-8') as f:
        f.write("\n=== CAGR TURNAROUND EDGE CASES ===\n\n")
        for ec in cagr_edge_cases:
            f.write(ec + "\n")
            
    # Populate DB analysis table
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # We clear the existing analysis table first, then load the computed ones
    cursor.execute("DELETE FROM analysis")
    
    insert_sql = """
        INSERT INTO analysis (
            company_id, revenue_3yr_cagr, revenue_5yr_cagr, revenue_10yr_cagr,
            pat_3yr_cagr, pat_5yr_cagr, pat_10yr_cagr, eps_3yr_cagr,
            eps_5yr_cagr, eps_10yr_cagr, roe_5yr_avg, roic_5yr_avg
        ) VALUES (
            :company_id, :revenue_3yr_cagr, :revenue_5yr_cagr, :revenue_10yr_cagr,
            :pat_3yr_cagr, :pat_5yr_cagr, :pat_10yr_cagr, :eps_3yr_cagr,
            :eps_5yr_cagr, :eps_10yr_cagr, :roe_5yr_avg, :roic_5yr_avg
        )
    """
    
    cursor.executemany(insert_sql, analysis_records)
    conn.commit()
    conn.close()
    
    logger.info(f"Populated analysis table in SQLite with {len(analysis_records)} rows.")

def analyze_bank_roce(db_path: str):
    """
    Day 13: Sector-relative ROCE analysis for Banks/NBFCs (Financials broad sector).
    Computes sector median ROCE and logs anomalies.
    Saves results to output/sector_roce_notes.csv.
    """
    conn = get_connection(db_path)
    
    # 1. Fetch companies, their sector mapping
    df_sectors = pd.read_sql_query("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)
    # Filter for broad_sector == 'Financials'
    df_financials = df_sectors[df_sectors['broad_sector'] == 'Financials'].copy()
    financial_tickers = set(df_financials['company_id'].str.strip().str.upper())
    
    # 2. Get ROCE parameters (depreciation, operating_profit from profitandloss, and equity/borrowings from balancesheet)
    df_pl = pd.read_sql_query("SELECT company_id, year, operating_profit, depreciation FROM profitandloss", conn)
    df_bs = pd.read_sql_query("SELECT company_id, year, equity_capital, reserves, borrowings FROM balancesheet", conn)
    
    conn.close()
    
    # Standardize dataframes
    for df in [df_pl, df_bs]:
        df['company_id'] = df['company_id'].str.strip().str.upper()
        df['year'] = df['year'].str.strip()
        
    # Calculate ROCE for all company-years
    df_roce = pd.merge(df_pl, df_bs, on=['company_id', 'year'], how='inner')
    df_roce['roce'] = df_roce.apply(
        lambda r: calculate_roce(r['operating_profit'], r['depreciation'], r['equity_capital'], r['reserves'], r['borrowings']),
        axis=1
    )
    
    # Filter for financials
    df_fin_roce = df_roce[df_roce['company_id'].isin(financial_tickers)].copy()
    
    if df_fin_roce.empty:
        logger.warning("No financial company ROCE data found for relative analysis.")
        return
        
    # Drop rows with None ROCE
    df_fin_roce = df_fin_roce.dropna(subset=['roce'])
    
    # Group by year to compute median and standard deviation
    sector_stats = df_fin_roce.groupby('year')['roce'].agg(['median', 'std']).reset_index()
    sector_stats.rename(columns={'median': 'sector_median', 'std': 'sector_std'}, inplace=True)
    
    # Fill NaN std (e.g. if only 1 company in a year) with 0
    sector_stats['sector_std'] = sector_stats['sector_std'].fillna(0.0)
    
    # Merge stats back
    df_fin_roce = df_fin_roce.merge(sector_stats, on='year', how='left')
    df_fin_roce = df_fin_roce.merge(df_financials, on='company_id', how='left')
    
    notes_records = []
    anomalies = []
    
    for _, row in df_fin_roce.iterrows():
        co = row['company_id']
        year = row['year']
        roce = row['roce']
        median = row['sector_median']
        std = row['sector_std']
        sub_sec = row['sub_sector']
        
        diff = roce - median
        classification = "Outperforming" if diff >= 0 else "Underperforming"
        
        # Determine anomaly
        is_anomaly = False
        anomaly_reason = []
        
        if std > 0 and abs(diff) > 1.5 * std:
            is_anomaly = True
            anomaly_reason.append(f"Significant deviation from sector median (>1.5 std, diff={diff:.2f}%)")
            
        if roce < 0:
            is_anomaly = True
            anomaly_reason.append("Negative ROCE")
            
        if roce > 30.0:
            is_anomaly = True
            anomaly_reason.append("Exceptionally high ROCE (>30%)")
            
        note = "; ".join(anomaly_reason) if is_anomaly else "Normal"
        
        if is_anomaly:
            anomalies.append(
                f"[ROCE Bank Anomaly] Co: {co}, Year: {year} | ROCE: {roce:.2f}% | Sector Median: {median:.2f}% | Note: {note}"
            )
            
        notes_records.append({
            'company_id': co,
            'year': year,
            'sub_sector': sub_sec,
            'computed_roce': round(roce, 4),
            'sector_median_roce': round(median, 4),
            'deviation_from_median': round(diff, 4),
            'classification': classification,
            'anomaly_flag': 1 if is_anomaly else 0,
            'note': note
        })
        
    # Write to sector_roce_notes.csv
    keys = ['company_id', 'year', 'sub_sector', 'computed_roce', 'sector_median_roce', 'deviation_from_median', 'classification', 'anomaly_flag', 'note']
    with open('output/sector_roce_notes.csv', 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(notes_records)
        
    # Append ROCE bank anomaly logs to edge cases log
    with open('output/ratio_edge_cases.log', 'a', encoding='utf-8') as f:
        f.write("\n=== BANK/NBFC ROCE ANOMALIES ===\n\n")
        for ec in anomalies:
            f.write(ec + "\n")
            
    logger.info(f"Sector-relative ROCE analysis completed. Exported {len(notes_records)} records to output/sector_roce_notes.csv.")

def main():
    setup_directories()
    
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    logger.info(f"Connecting to database at: {db_path}")
    
    if not Path(db_path).exists():
        logger.error(f"Database file does not exist: {db_path}")
        return
        
    try:
        # Step 1: Compute and populate ratios
        records = compute_all_ratios(db_path)
        if records:
            populate_ratios_db(db_path, records)
            
        # Step 2: Compute and populate CAGR/averages
        compute_and_populate_cagr(db_path)
        
        # Step 3: Sector-relative ROCE analysis for Banks/NBFCs
        analyze_bank_roce(db_path)
        
        logger.info("Ratio Engine and CAGR computation completed successfully!")
    except Exception as e:
        logger.exception(f"Error executing ratio engine calculations: {e}")

if __name__ == '__main__':
    main()
