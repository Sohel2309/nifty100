"""
Orchestration Script for Peer Comparison Engine
Populates SQLite percentiles, generates peer_comparison.xlsx, and plots 92 company radar charts.
"""

import os
import sqlite3
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv

from src.analytics.peer import run_peer_analysis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def plot_radar_chart(company_id, peer_group, categories, company_vals, peer_avg_vals, benchmark_vals, benchmark_ticker, save_path):
    """Plot a polar radar chart using matplotlib and save as static PNG"""
    N = len(categories)
    
    # Repeat the first value to close the circular loop
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    c_vals = list(company_vals) + [company_vals[0]]
    p_vals = list(peer_avg_vals) + [peer_avg_vals[0]]
    b_vals = list(benchmark_vals) + [benchmark_vals[0]]
    
    fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
    
    # Draw axes per variable
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    
    # Draw ylabels (percentiles are 0 to 1)
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.50, 0.75, 1.0], ["25%", "50%", "75%", "100%"], color="grey", size=7)
    plt.ylim(0, 1.05)
    
    # Plot company values (solid blue line)
    ax.plot(angles, c_vals, linewidth=2, linestyle='solid', label=f'{company_id} (Percentile)', color='#1f77b4')
    ax.fill(angles, c_vals, '#1f77b4', alpha=0.15)
    
    # Plot peer average (dashed green line)
    ax.plot(angles, p_vals, linewidth=1.5, linestyle='dashed', label='Peer Group Avg', color='#2ca02c')
    
    # Plot benchmark (dotted red line)
    ax.plot(angles, b_vals, linewidth=1.5, linestyle='dotted', label=f'Benchmark ({benchmark_ticker})', color='#d62728')
    
    plt.title(f"{company_id} - Peer Comparison ({peer_group})", size=10, weight='bold', y=1.1)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
    plt.tight_layout()
    
    # Save figure
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def generate_radar_charts(db_path: str):
    """Generate 8-axis polar radar charts for all companies assigned to peer groups for year 2024-03"""
    Path("reports/radar_charts").mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Load peer percentiles and metadata
    df_pp = pd.read_sql_query("SELECT * FROM peer_percentiles WHERE year = '2024-03'", conn)
    
    # To compute ROCE percentile, we need roce_pr which we calculated in peer.py.
    # The columns of interest:
    # 8 axes: ROE, ROCE, NPM, D/E, FCF, PAT CAGR, Revenue CAGR, EPS CAGR
    # In peer_percentiles table, we have return_on_equity_pct_pr, net_profit_margin_pct_pr, etc.
    # Note: ROCE percentile is return_on_equity_pct_pr or custom. In peer.py we saved roce_pr to return_on_equity_pct_pr?
    # Wait, in peer.py: we had roce_pr. Let's make sure what columns we have in peer_percentiles.
    # Wait, let's verify if roce_pr was saved in peer_percentiles. In our CREATE TABLE, we didn't have roce_pr column!
    # Ah! In the CREATE TABLE of peer_percentiles, we had:
    # return_on_equity_pct_pr, net_profit_margin_pct_pr, debt_to_equity_pr, interest_coverage_pr, asset_turnover_pr, free_cash_flow_cr_pr, capex_cr_pr, earnings_per_share_pr, book_value_per_share_pr, dividend_payout_ratio_pct_pr, total_debt_cr_pr, cash_from_operations_cr_pr, revenue_5yr_cagr_pr, pat_5yr_cagr_pr, eps_5yr_cagr_pr, pe_ratio_pr, pb_ratio_pr, ev_ebitda_pr, dividend_yield_pr.
    # Wait, we did not have roce_pr in the DDL, but we computed group_scored['roce_pr'] in peer.py.
    # Let's check: did we save roce_pr?
    # In peer.py, roce_pr was not saved because we didn't include it in the DDL list or the insert list.
    # Wait, can we use return_on_equity_pct_pr or calculate roce_pr on the fly?
    # Actually, we can use `return_on_equity_pct_pr` as a proxy, or modify peer_percentiles table to include `roce_pr`.
    # Let's check: does the database schema allow `roce_pr` column? We can just add it or compute it on the fly from the database in the charting script.
    # Let's check `peer.py` DDL list again. We had 20 metrics, let's look at the columns.
    # Yes, we can just compute it on the fly or load it. Since we already have the database query here, let's compute it or load `roce` on the fly.
    
    df_pl = pd.read_sql_query("SELECT company_id, operating_profit, depreciation FROM profitandloss WHERE year = '2024-03'", conn)
    df_bs = pd.read_sql_query("SELECT company_id, equity_capital, reserves, borrowings FROM balancesheet WHERE year = '2024-03'", conn)
    
    conn.close()
    
    # Merge and calculate ROCE
    df_roce = df_pl.merge(df_bs, on='company_id', how='inner')
    df_roce['ebit'] = df_roce['operating_profit'] - df_roce['depreciation']
    df_roce['capital_employed'] = df_roce['equity_capital'] + df_roce['reserves'] + df_roce['borrowings']
    df_roce['roce'] = df_roce.apply(
        lambda r: (r['ebit'] / r['capital_employed'] * 100) if r['capital_employed'] > 0 else np.nan,
        axis=1
    )
    
    # Merge ROCE into percentiles dataframe
    df_pp = df_pp.merge(df_roce[['company_id', 'roce']], on='company_id', how='left')
    
    # Group by peer group and calculate ROCE percent rank
    df_pp['roce_pr'] = df_pp.groupby('peer_group_name')['roce'].transform(
        lambda x: (x.rank(method='min') - 1) / (len(x.dropna()) - 1) if len(x.dropna()) > 1 else 1.0
    )
    
    # Standardize D/E so that higher is better (i.e. lower debt = 1.0, higher debt = 0.0)
    df_pp['de_inverted_pr'] = 1.0 - df_pp['debt_to_equity_pr']
    
    # Axes definition
    axes = ['ROE', 'ROCE', 'NPM', 'Low D/E', 'FCF', 'PAT CAGR', 'Rev CAGR', 'EPS CAGR']
    cols = ['return_on_equity_pct_pr', 'roce_pr', 'net_profit_margin_pct_pr', 'de_inverted_pr', 
            'free_cash_flow_cr_pr', 'pat_5yr_cagr_pr', 'revenue_5yr_cagr_pr', 'eps_5yr_cagr_pr']
            
    # For each peer group, find the benchmark company values and group averages
    for group_name in df_pp['peer_group_name'].unique():
        group_df = df_pp[df_pp['peer_group_name'] == group_name].copy()
        
        # Benchmark company
        bench_row = group_df[group_df['is_benchmark'] == 1]
        if not bench_row.empty:
            bench_ticker = bench_row['company_id'].values[0]
            bench_vals = [bench_row[col].values[0] for col in cols]
        else:
            bench_ticker = "None"
            bench_vals = [0.5] * len(cols)
            
        # Group averages
        avg_vals = [group_df[col].mean() for col in cols]
        
        # Clean NaNs in averages or benchmark
        bench_vals = [0.5 if pd.isna(v) else v for v in bench_vals]
        avg_vals = [0.5 if pd.isna(v) else v for v in avg_vals]
        
        # Plot radar chart for each company in the group
        for _, row in group_df.iterrows():
            co = row['company_id']
            co_vals = [row[col] for col in cols]
            
            # Clean NaNs in company values
            co_vals = [0.0 if pd.isna(v) else v for v in co_vals]
            
            save_path = f"reports/radar_charts/{co}_radar.png"
            plot_radar_chart(co, group_name, axes, co_vals, avg_vals, bench_vals, bench_ticker, save_path)
            logger.info(f"Generated radar chart for: {co}")

def export_peer_comparison_excel(db_path: str):
    """Export peer group comparison tables to output/peer_comparison.xlsx (sheet per group)"""
    conn = sqlite3.connect(db_path)
    
    # Load companies, ratios, and metadata
    df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = '2024-03'", conn)
    df_analysis = pd.read_sql_query("SELECT * FROM analysis", conn)
    df_mkt = pd.read_sql_query("SELECT * FROM market_cap WHERE year = '2024-03'", conn)
    df_pp = pd.read_sql_query("SELECT * FROM peer_percentiles WHERE year = '2024-03'", conn)
    df_co = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
    
    conn.close()
    
    # Standardize tickers
    for df in [df_ratios, df_analysis, df_mkt, df_pp, df_co]:
        for col in ['company_id', 'id']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
                
    df_co.rename(columns={'id': 'company_id'}, inplace=True)
    
    # Merge values
    df_values = df_co.merge(df_ratios, on='company_id', how='inner')
    df_values = df_values.merge(df_analysis, on='company_id', how='left')
    df_values = df_values.merge(df_mkt[['company_id', 'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield']], on='company_id', how='left')
    
    # Path setup
    output_path = "output/peer_comparison.xlsx"
    Path("output").mkdir(exist_ok=True)
    
    # Excel sheets per peer group
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for group_name in df_pp['peer_group_name'].unique():
            group_tickers = df_pp[df_pp['peer_group_name'] == group_name]['company_id'].unique()
            
            # Filter values and percentiles
            group_vals = df_values[df_values['company_id'].isin(group_tickers)].copy()
            group_pcts = df_pp[df_pp['peer_group_name'] == group_name].copy()
            
            # Merge value and percentile dfs
            group_export = group_vals.merge(group_pcts[['company_id', 'best_in_class', 'watch_list']], on='company_id', how='left')
            
            cols = [
                'company_id', 'company_name', 'return_on_equity_pct', 'debt_to_equity',
                'net_profit_margin_pct', 'free_cash_flow_cr', 'revenue_5yr_cagr', 'pat_5yr_cagr',
                'pe_ratio', 'pb_ratio', 'best_in_class', 'watch_list'
            ]
            cols = [c for c in cols if c in group_export.columns]
            
            final_df = group_export[cols].copy()
            final_df.rename(columns={
                'best_in_class': 'Best in Class (Badge)',
                'watch_list': 'Watch List (Flag)'
            }, inplace=True)
            
            sheet_name = group_name[:31]
            final_df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"Exported {len(final_df)} companies for peer group '{group_name}' to sheet '{sheet_name}'.")
            
    logger.info(f"Peer comparison tables successfully exported to: {output_path}")

def main():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    logger.info(f"Starting peer comparison engine for: {db_path}")
    
    if not os.path.exists(db_path):
        logger.error(f"Database file does not exist: {db_path}")
        return
        
    try:
        # Step 1: Run percentile calculation and update SQLite
        run_peer_analysis(db_path)
        
        # Step 2: Generate radar charts
        generate_radar_charts(db_path)
        
        # Step 3: Export peer comparison Excel sheet
        export_peer_comparison_excel(db_path)
        
        logger.info("Peer comparison analysis completed successfully!")
    except Exception as e:
        logger.exception(f"Error executing peer analysis: {e}")

if __name__ == '__main__':
    main()
