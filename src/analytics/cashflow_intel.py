"""
Cash Flow Intelligence Engine for Nifty 100 Financial Intelligence Platform
Computes CFO Quality, CapEx Intensity, FCF Conversion, Distress Alerts, and Allocation matrix.
"""

import os
import sqlite3
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

def score_cfo_quality(val):
    if pd.isna(val):
        return 'Normal'
    if val > 1.0:
        return 'High Quality Earnings'
    elif val < 0.5:
        return 'Accrual Risk'
    else:
        return 'Normal'

def score_capex_intensity(val):
    if pd.isna(val):
        return 'Moderate'
    if val < 3.0:
        return 'Asset-Light'
    elif val > 8.0:
        return 'Capital Intensive'
    else:
        return 'Moderate'

def score_fcf_conversion(val):
    if pd.isna(val):
        return 'Average'
    if val > 60.0:
        return 'Efficient'
    elif val < 30.0:
        return 'CapEx Heavy'
    else:
        return 'Average'

def run_cashflow_analysis(db_path: str):
    """Run cash flow intelligence metrics and export spreadsheets"""
    logger.info(f"Connecting to database for Cash Flow analysis: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # Load required data tables
    df_co = pd.read_sql_query("SELECT id, company_name, sector FROM companies", conn)
    df_sec = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
    df_cf = pd.read_sql_query("SELECT * FROM cashflow", conn)
    df_bs = pd.read_sql_query("SELECT * FROM balancesheet", conn)
    df_pl = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    
    conn.close()
    
    # Clean tickers
    for df in [df_co, df_sec, df_cf, df_bs, df_pl, df_ratios]:
        for col in ['company_id', 'id']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
                
    df_co.rename(columns={'id': 'company_id'}, inplace=True)
    df_co_sec = df_co.merge(df_sec, on='company_id', how='left')
    df_co_sec['broad_sector'] = df_co_sec['broad_sector'].fillna(df_co_sec['sector'])
    
    # Filter for latest year (2024-03)
    latest_year = "2024-03"
    
    df_cf_latest = df_cf[df_cf['year'] == latest_year].copy()
    df_bs_latest = df_bs[df_bs['year'] == latest_year].copy()
    df_pl_latest = df_pl[df_pl['year'] == latest_year].copy()
    df_ratios_latest = df_ratios[df_ratios['year'] == latest_year].copy()
    
    # ============================================================
    # 7.1: CFO Quality Score (CFO/PAT ratio > 1.0 across 5yr avg = 'High Quality Earnings')
    # ============================================================
    # First, calculate CFO/PAT for all years
    df_cf_flat = df_cf.merge(df_pl[['company_id', 'year', 'net_profit']], on=['company_id', 'year'], how='inner')
    df_cf_flat['cfo_pat_ratio'] = df_cf_flat.apply(
        lambda r: (r['operating_activity'] / r['net_profit']) if (pd.notna(r['operating_activity']) and pd.notna(r['net_profit']) and r['net_profit'] > 0) else np.nan,
        axis=1
    )
    # 5yr average CFO/PAT per company (up to latest year)
    df_cf_5yr_avg = df_cf_flat.groupby('company_id')['cfo_pat_ratio'].mean().reset_index().rename(columns={'cfo_pat_ratio': 'cfo_pat_5yr_avg'})
    
    df_cf_5yr_avg['cfo_quality_badge'] = df_cf_5yr_avg['cfo_pat_5yr_avg'].apply(score_cfo_quality)
    
    # ============================================================
    # 7.2: CapEx Intensity (CapEx / Revenue %. Light <3%, Heavy >8%)
    # ============================================================
    df_capex_flat = df_ratios_latest[['company_id', 'capex_cr']].merge(
        df_pl_latest[['company_id', 'sales']], on='company_id', how='inner'
    )
    df_capex_flat['capex_intensity_pct'] = df_capex_flat.apply(
        lambda r: (r['capex_cr'] / r['sales'] * 100) if (pd.notna(r['capex_cr']) and pd.notna(r['sales']) and r['sales'] > 0) else np.nan,
        axis=1
    )
    
    df_capex_flat['capex_intensity_tier'] = df_capex_flat['capex_intensity_pct'].apply(score_capex_intensity)
    
    # ============================================================
    # 7.4: FCF Conversion Rate (FCF / EBITDA. >60% efficient, <30% CapEx heavy)
    # ============================================================
    # We use operating_profit as EBITDA
    df_fcf_conv = df_ratios_latest[['company_id', 'free_cash_flow_cr']].merge(
        df_pl_latest[['company_id', 'operating_profit']], on='company_id', how='inner'
    )
    df_fcf_conv['fcf_conversion_pct'] = df_fcf_conv.apply(
        lambda r: (r['free_cash_flow_cr'] / r['operating_profit'] * 100) if (pd.notna(r['free_cash_flow_cr']) and pd.notna(r['operating_profit']) and r['operating_profit'] > 0) else np.nan,
        axis=1
    )
    
    df_fcf_conv['fcf_conversion_tier'] = df_fcf_conv['fcf_conversion_pct'].apply(score_fcf_conversion)
    
    # ============================================================
    # 7.5: Debt Repayment Detection (CFF < 0 AND borrowings declining YoY -> 'Deleveraging')
    # ============================================================
    # Load previous year (2023-03) borrowings for comparison
    df_bs_prev = df_bs[df_bs['year'] == "2023-03"].copy()
    
    df_deleveraging = df_cf_latest[['company_id', 'financing_activity']].merge(
        df_bs_latest[['company_id', 'borrowings']], on='company_id', how='inner'
    )
    df_deleveraging = df_deleveraging.merge(
        df_bs_prev[['company_id', 'borrowings']], on='company_id', how='left', suffixes=('_latest', '_prev')
    )
    
    def check_deleveraging(row):
        cff = row['financing_activity']
        bor_latest = row['borrowings_latest']
        bor_prev = row['borrowings_prev']
        if pd.isna(cff) or pd.isna(bor_latest) or pd.isna(bor_prev):
            return 0
        if cff < 0 and bor_latest < bor_prev:
            return 1
        return 0
        
    df_deleveraging['deleveraging_flag'] = df_deleveraging.apply(check_deleveraging, axis=1)
    
    # ============================================================
    # 7.6: Distress Pattern (CFO < 0 AND CFF > 0 -> 'Distress Signal')
    # ============================================================
    df_distress = df_cf_latest[['company_id', 'operating_activity', 'financing_activity']].copy()
    df_distress['distress_flag'] = df_distress.apply(
        lambda r: 1 if (pd.notna(r['operating_activity']) and pd.notna(r['financing_activity']) and r['operating_activity'] < 0 and r['financing_activity'] > 0) else 0,
        axis=1
    )
    
    # Merge and export distress_alerts.csv
    df_distress_export = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(df_distress, on='company_id', how='inner')
    Path("output").mkdir(exist_ok=True)
    df_distress_export.to_csv("output/distress_alerts.csv", index=False)
    logger.info("Saved distress_alerts.csv to output/")
    
    # ============================================================
    # 7.7: Capital Allocation Matrix
    # ============================================================
    # sign patterns -> descriptive labels
    def get_cf_pattern(row):
        cfo = "+" if row['operating_activity'] >= 0 else "-"
        cfi = "+" if row['investing_activity'] >= 0 else "-"
        cff = "+" if row['financing_activity'] >= 0 else "-"
        return f"[{cfo}, {cfi}, {cff}]"
        
    pattern_labels = {
        "[+, -, -]": "Standard Operations (Healthy)",
        "[+, -, +]": "Aggressive Growth Expansion",
        "[+, +, -]": "Cash Harvester (Paying Debt)",
        "[+, +, +]": "High Liquidity Accumulation",
        "[-, -, +]": "Startup / External Financing",
        "[-, -, -]": "Cash Burn (High Risk)",
        "[-, +, +]": "Survival / Asset Sales",
        "[-, +, -]": "Liquidation / Restructuring"
    }
    
    df_matrix = df_cf_latest[['company_id', 'operating_activity', 'investing_activity', 'financing_activity']].copy()
    df_matrix['pattern'] = df_matrix.apply(get_cf_pattern, axis=1)
    df_matrix['pattern_description'] = df_matrix['pattern'].map(pattern_labels)
    
    # ============================================================
    # Export cashflow_intelligence.xlsx
    # ============================================================
    # Join all calculations to a single master sheet
    df_master = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(
        df_cf_5yr_avg[['company_id', 'cfo_pat_5yr_avg', 'cfo_quality_badge']], on='company_id', how='left'
    )
    df_master = df_master.merge(
        df_capex_flat[['company_id', 'capex_intensity_pct', 'capex_intensity_tier']], on='company_id', how='left'
    )
    df_master = df_master.merge(
        df_fcf_conv[['company_id', 'fcf_conversion_pct', 'fcf_conversion_tier']], on='company_id', how='left'
    )
    df_master = df_master.merge(
        df_deleveraging[['company_id', 'deleveraging_flag']], on='company_id', how='left'
    )
    df_master = df_master.merge(
        df_distress_export[['company_id', 'operating_activity', 'financing_activity', 'distress_flag']], on='company_id', how='left'
    )
    df_master = df_master.merge(
        df_matrix[['company_id', 'pattern', 'pattern_description']], on='company_id', how='left'
    )
    
    intel_path = "output/cashflow_intelligence.xlsx"
    with pd.ExcelWriter(intel_path, engine='openpyxl') as writer:
        df_master.to_excel(writer, sheet_name='CashFlow_Intelligence', index=False)
        # Add summary count sheet for pattern matrix
        pattern_counts = df_matrix['pattern_description'].value_counts().reset_index()
        pattern_counts.columns = ['Allocation Pattern Category', 'Number of Companies']
        pattern_counts.to_excel(writer, sheet_name='Pattern_Matrix_Summary', index=False)
        
    logger.info(f"Saved cashflow_intelligence.xlsx report to {intel_path}")
    logger.info("Cash Flow Intelligence analysis completed successfully!")

def main():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    run_cashflow_analysis(db_path)

if __name__ == '__main__':
    main()
