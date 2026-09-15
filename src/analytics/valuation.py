"""
Valuation and Market Data Engine for Nifty 100 Financial Intelligence Platform
Computes historical multiples, FCF yields, overvaluation flags, and exports summaries.
"""

import os
import sqlite3
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

def score_valuation(row):
    """Score valuation PE based on rules"""
    pe = row['pe_ratio']
    sec_med = row['sector_median_pe']
    if pd.isna(pe) or pd.isna(sec_med) or sec_med <= 0:
        return 'Neutral'
    if pe > sec_med * 1.5:
        return 'Caution'
    elif pe < sec_med * 0.7:
        return 'Discount'
    else:
        return 'Neutral'

def run_valuation_analysis(db_path: str):
    """Run all valuation calculations and export sheets & csv files"""
    logger.info(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # 1. Load companies, sectors, market_cap, financial_ratios
    df_co = pd.read_sql_query("SELECT id, company_name, sector FROM companies", conn)
    df_sec = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
    df_mkt = pd.read_sql_query("SELECT * FROM market_cap", conn)
    df_ratios = pd.read_sql_query("SELECT company_id, year, free_cash_flow_cr, return_on_equity_pct FROM financial_ratios", conn)
    
    conn.close()
    
    # Clean company IDs
    for df in [df_co, df_sec, df_mkt, df_ratios]:
        for col in ['company_id', 'id']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
                
    df_co.rename(columns={'id': 'company_id'}, inplace=True)
    
    # Merge sector info
    df_co_sec = df_co.merge(df_sec, on='company_id', how='left')
    # If broad_sector is missing, fall back to sector
    df_co_sec['broad_sector'] = df_co_sec['broad_sector'].fillna(df_co_sec['sector'])
    
    # Standardize years in market_cap and ratios
    df_mkt['year'] = df_mkt['year'].astype(str).str.strip()
    df_ratios['year'] = df_ratios['year'].astype(str).str.strip()
    
    # Year YYYY-MM mapping for market_cap: standardise
    # e.g., '2024-03' in market_cap, make sure it matches
    # Ratios also has YYYY-MM
    
    # Let's filter for latest year: '2024-03'
    latest_year = "2024-03"
    
    # ============================================================
    # 6.1: P/E Trend Table
    # ============================================================
    # Select PE ratios for all years, pivot by year
    df_pe_pivot = df_mkt.pivot(index='company_id', columns='year', values='pe_ratio').reset_index()
    # Merge company name
    df_pe_trends = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(df_pe_pivot, on='company_id', how='inner')
    
    # ============================================================
    # 6.2: P/B vs ROE Scatter Chart
    # ============================================================
    df_mkt_latest = df_mkt[df_mkt['year'] == latest_year].copy()
    df_ratios_latest = df_ratios[df_ratios['year'] == latest_year].copy()
    
    df_scatter_data = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(df_mkt_latest[['company_id', 'pb_ratio', 'market_cap_cr']], on='company_id', how='inner')
    df_scatter_data = df_scatter_data.merge(df_ratios_latest[['company_id', 'return_on_equity_pct']], on='company_id', how='inner')
    
    # Drop rows with NaNs in required fields
    df_scatter_clean = df_scatter_data.dropna(subset=['pb_ratio', 'return_on_equity_pct', 'market_cap_cr'])
    
    # Plot using matplotlib
    Path("reports").mkdir(exist_ok=True)
    plt.figure(figsize=(10, 7))
    
    # Create colors per sector
    sectors_list = df_scatter_clean['broad_sector'].unique()
    colors = plt.cm.get_cmap('tab20', len(sectors_list))
    sector_color_map = {sec: colors(i) for i, sec in enumerate(sectors_list)}
    
    for sec in sectors_list:
        sec_df = df_scatter_clean[df_scatter_clean['broad_sector'] == sec]
        # scale size by market cap
        sizes = sec_df['market_cap_cr'] / 1000.0  # scale size
        sizes = np.clip(sizes, 20, 1000)          # clip for display
        plt.scatter(
            sec_df['pb_ratio'], sec_df['return_on_equity_pct'],
            s=sizes, label=sec, color=sector_color_map[sec], alpha=0.7, edgecolors='black'
        )
        
    plt.xlabel('Price-to-Book (P/B) Ratio', fontsize=11)
    plt.ylabel('Return on Equity (ROE) %', fontsize=11)
    plt.title('P/B vs ROE Scatter Chart (Nifty 100 - March 2024)', fontsize=13, weight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Sectors', fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("reports/pb_roe_scatter.png", dpi=120)
    plt.close()
    logger.info("Saved P/B vs ROE scatter plot to reports/pb_roe_scatter.png.")
    
    # ============================================================
    # 6.3: EV/EBITDA Comp Table
    # ============================================================
    # EV/EBITDA 5yr median per company
    df_ev_ebitda_5yr = df_mkt.groupby('company_id')['ev_ebitda'].median().reset_index().rename(columns={'ev_ebitda': '5yr_median_ev_ebitda'})
    
    # Sector median EV/EBITDA for latest year
    df_mkt_latest_sec = df_mkt_latest.merge(df_co_sec[['company_id', 'broad_sector']], on='company_id', how='inner')
    df_sec_median_ev = df_mkt_latest_sec.groupby('broad_sector')['ev_ebitda'].median().reset_index().rename(columns={'ev_ebitda': 'sector_median_ev_ebitda'})
    
    # Merge EV/EBITDA comparisons
    df_ev_comp = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(
        df_mkt_latest[['company_id', 'ev_ebitda']], on='company_id', how='inner'
    )
    df_ev_comp = df_ev_comp.merge(df_ev_ebitda_5yr, on='company_id', how='left')
    df_ev_comp = df_ev_comp.merge(df_sec_median_ev, on='broad_sector', how='left')
    
    # Flag if current EV/EBITDA > 20% above sector median
    df_ev_comp['above_sector_20pct_flag'] = df_ev_comp.apply(
        lambda r: 1 if (pd.notna(r['ev_ebitda']) and pd.notna(r['sector_median_ev_ebitda']) and r['sector_median_ev_ebitda'] > 0 and r['ev_ebitda'] > r['sector_median_ev_ebitda'] * 1.2) else 0,
        axis=1
    )
    
    # ============================================================
    # 6.4: Dividend Yield Ranker
    # ============================================================
    df_div_rank = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(
        df_mkt_latest[['company_id', 'dividend_yield']], on='company_id', how='inner'
    ).sort_values('dividend_yield', ascending=False)
    
    # ============================================================
    # 6.5: FCF Yield Calculator
    # ============================================================
    df_fcf_yield_calc = df_co_sec[['company_id', 'company_name', 'broad_sector']].merge(
        df_mkt_latest[['company_id', 'market_cap_cr']], on='company_id', how='inner'
    )
    df_fcf_yield_calc = df_fcf_yield_calc.merge(
        df_ratios_latest[['company_id', 'free_cash_flow_cr']], on='company_id', how='inner'
    )
    
    df_fcf_yield_calc['fcf_yield'] = df_fcf_yield_calc.apply(
        lambda r: (r['free_cash_flow_cr'] / r['market_cap_cr'] * 100) if (pd.notna(r['free_cash_flow_cr']) and pd.notna(r['market_cap_cr']) and r['market_cap_cr'] > 0) else np.nan,
        axis=1
    )
    df_fcf_yield_calc = df_fcf_yield_calc.sort_values('fcf_yield', ascending=False)
    
    # ============================================================
    # 6.6: Overvaluation Flag & valuation_flags.csv
    # ============================================================
    # Sector median P/E for latest year
    df_sec_median_pe = df_mkt_latest_sec.groupby('broad_sector')['pe_ratio'].median().reset_index().rename(columns={'pe_ratio': 'sector_median_pe'})
    
    df_pe_flags = df_co_sec[['company_id', 'company_name', 'sector', 'broad_sector']].merge(
        df_mkt_latest[['company_id', 'pe_ratio']], on='company_id', how='inner'
    )
    df_pe_flags = df_pe_flags.merge(df_sec_median_pe, on='broad_sector', how='left')
    
    df_pe_flags['valuation_badge'] = df_pe_flags.apply(score_valuation, axis=1)
    
    # Save CSV flags
    Path("output").mkdir(exist_ok=True)
    df_pe_flags.to_csv("output/valuation_flags.csv", index=False)
    logger.info("Saved valuation flags to output/valuation_flags.csv.")
    
    # ============================================================
    # Export valuation_summary.xlsx
    # ============================================================
    summary_path = "output/valuation_summary.xlsx"
    with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
        df_pe_trends.to_excel(writer, sheet_name='PE_Trends', index=False)
        df_ev_comp.to_excel(writer, sheet_name='EV_EBITDA_Comp', index=False)
        df_div_rank.to_excel(writer, sheet_name='Dividend_Yield_Ranks', index=False)
        df_fcf_yield_calc.to_excel(writer, sheet_name='FCF_Yield_Ranks', index=False)
        df_pe_flags.to_excel(writer, sheet_name='Overvaluation_Flags', index=False)
        
    logger.info(f"Saved valuation summary report to {summary_path}.")

def main():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    run_valuation_analysis(db_path)
    logger.info("Valuation module completed successfully!")

if __name__ == '__main__':
    main()
