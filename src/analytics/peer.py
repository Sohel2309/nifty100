"""
Peer Comparison Engine for Nifty 100 Financial Intelligence Platform
Calculates intra-group percentile ranks, benchmark gaps, and Best in Class / Watch List badges.
Populates the peer_percentiles table in SQLite.
"""

import sqlite3
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

def create_peer_percentiles_table(db_path: str):
    """Create peer_percentiles database table if it doesn't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peer_percentiles (
            company_id TEXT NOT NULL,
            year TEXT NOT NULL,
            peer_group_name TEXT NOT NULL,
            is_benchmark INTEGER NOT NULL CHECK (is_benchmark IN (0, 1)),
            net_profit_margin_pct_pr REAL,
            operating_profit_margin_pct_pr REAL,
            return_on_equity_pct_pr REAL,
            debt_to_equity_pr REAL,
            interest_coverage_pr REAL,
            asset_turnover_pr REAL,
            free_cash_flow_cr_pr REAL,
            capex_cr_pr REAL,
            earnings_per_share_pr REAL,
            book_value_per_share_pr REAL,
            dividend_payout_ratio_pct_pr REAL,
            total_debt_cr_pr REAL,
            cash_from_operations_cr_pr REAL,
            revenue_5yr_cagr_pr REAL,
            pat_5yr_cagr_pr REAL,
            eps_5yr_cagr_pr REAL,
            pe_ratio_pr REAL,
            pb_ratio_pr REAL,
            ev_ebitda_pr REAL,
            dividend_yield_pr REAL,
            best_in_class INTEGER,
            watch_list INTEGER,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Ensured peer_percentiles table exists in SQLite database.")

def compute_percent_rank(series: pd.Series) -> pd.Series:
    """
    Compute standard SQL percent_rank: (rank - 1) / (N - 1).
    Ascending order. Higher value -> higher percentile rank.
    """
    # Exclude NaNs from ranking
    non_null = series.dropna()
    if len(non_null) <= 1:
        # If 0 or 1 valid entries, assign 1.0 to any non-null value
        res = pd.Series(np.nan, index=series.index)
        if len(non_null) == 1:
            res[non_null.index[0]] = 1.0
        return res
        
    ranks = non_null.rank(method='min', ascending=True)
    pr = (ranks - 1) / (len(non_null) - 1)
    
    # Reindex to original series shape to preserve indices and NaNs
    return pr.reindex(series.index)

def calculate_roce(op_prof, dep, eq, res, bor):
    """Helper to compute ROCE"""
    if pd.isna(op_prof) or pd.isna(dep) or pd.isna(eq) or pd.isna(res) or pd.isna(bor):
        return np.nan
    ebit = op_prof - dep
    cap = eq + res + bor
    if cap <= 0:
        return np.nan
    return (ebit / cap) * 100

def run_peer_analysis(db_path: str):
    """
    Computes percentiles and saves results to peer_percentiles table in SQLite.
    Also executes Best-in-Class and Watch List badge scoring.
    """
    create_peer_percentiles_table(db_path)
    
    conn = sqlite3.connect(db_path)
    
    # Load peer group mapping
    df_pg = pd.read_sql_query("SELECT * FROM peer_groups", conn)
    if df_pg.empty:
        logger.warning("No peer groups found in peer_groups table.")
        conn.close()
        return
        
    df_pg['company_id'] = df_pg['company_id'].str.strip().str.upper()
    
    # Load ratios, analysis, market cap, and profit/loss
    df_ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    df_analysis = pd.read_sql_query("SELECT * FROM analysis", conn)
    df_mkt = pd.read_sql_query("SELECT * FROM market_cap", conn)
    df_pl = pd.read_sql_query("SELECT company_id, year, operating_profit, depreciation FROM profitandloss", conn)
    df_bs = pd.read_sql_query("SELECT company_id, year, equity_capital, reserves, borrowings FROM balancesheet", conn)
    
    conn.close()
    
    # Standardize company_ids and years
    for df in [df_ratios, df_analysis, df_mkt, df_pl, df_bs]:
        if not df.empty:
            df['company_id'] = df['company_id'].str.strip().str.upper()
            if 'year' in df.columns:
                df['year'] = df['year'].astype(str).str.strip()
                
    # Merge datasets to create a single flat DataFrame per company-year
    # ROCE is calculated
    df_roce_base = df_pl.merge(df_bs, on=['company_id', 'year'], how='inner')
    df_roce_base['roce'] = df_roce_base.apply(
        lambda r: calculate_roce(r['operating_profit'], r['depreciation'], r['equity_capital'], r['reserves'], r['borrowings']),
        axis=1
    )
    
    df_merged = df_ratios.merge(df_analysis, on='company_id', how='left', suffixes=('', '_analysis'))
    df_merged = df_merged.merge(df_mkt, on=['company_id', 'year'], how='left', suffixes=('', '_mkt'))
    df_merged = df_merged.merge(df_roce_base[['company_id', 'year', 'roce']], on=['company_id', 'year'], how='left')
    
    # Filter for companies that actually have peer group assignments
    df_merged = df_merged.merge(df_pg, on='company_id', how='inner')
    
    if df_merged.empty:
        logger.warning("No matched peer group companies found in time-series ratio tables.")
        return
        
    metrics_to_rank = [
        'net_profit_margin_pct', 'operating_profit_margin_pct', 'return_on_equity_pct',
        'debt_to_equity', 'interest_coverage', 'asset_turnover', 'free_cash_flow_cr',
        'capex_cr', 'earnings_per_share', 'book_value_per_share', 'dividend_payout_ratio_pct',
        'total_debt_cr', 'cash_from_operations_cr', 'revenue_5yr_cagr', 'pat_5yr_cagr',
        'eps_5yr_cagr', 'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield'
    ]
    
    records_to_insert = []
    
    # Group by peer group and year
    grouped = df_merged.groupby(['peer_group_name', 'year'])
    
    for (group_name, year), group_df in grouped:
        group_df = group_df.copy()
        
        # Calculate percentile ranks for all 20 metrics
        pr_cols = {}
        for m in metrics_to_rank:
            pr_cols[f"{m}_pr"] = compute_percent_rank(group_df[m])
            
        df_pr = pd.DataFrame(pr_cols, index=group_df.index)
        group_scored = pd.concat([group_df, df_pr], axis=1)
        
        # Calculate Best-in-Class and Watch List status
        # 10 core metrics for classification
        # For positive metrics (higher is better): top quartile means percentile >= 0.75, bottom <= 0.25
        # For negative metrics (lower is better, e.g. D/E): top quartile means percentile <= 0.25, bottom >= 0.75
        pos_metrics = [
            'return_on_equity_pct_pr', 'roce_pr', 'net_profit_margin_pct_pr',
            'free_cash_flow_cr_pr', 'revenue_5yr_cagr_pr', 'pat_5yr_cagr_pr',
            'eps_5yr_cagr_pr', 'asset_turnover_pr', 'interest_coverage_pr'
        ]
        
        # Note: ROCE percentile is based on ROCE
        # If roce was not direct, we check if roce_pr in columns
        group_scored['roce_pr'] = compute_percent_rank(group_df['roce'])
        
        for _, row in group_scored.iterrows():
            co = row['company_id']
            is_bench = int(row['is_benchmark'])
            
            top_count = 0
            bottom_count = 0
            metrics_count = 0
            
            # 1. Check positive metrics
            for pm in pos_metrics:
                val = row.get(pm)
                if pd.notna(val):
                    metrics_count += 1
                    if val >= 0.75:
                        top_count += 1
                    if val <= 0.25:
                        bottom_count += 1
                        
            # 2. Check negative metric: debt_to_equity
            de_pr = row.get('debt_to_equity_pr')
            if pd.notna(de_pr):
                metrics_count += 1
                if de_pr <= 0.25:  # lower is better -> top quartile
                    top_count += 1
                if de_pr >= 0.75:  # lower is better -> bottom quartile
                    bottom_count += 1
                    
            best_in_class = 1 if (top_count >= 6 and metrics_count >= 6) else 0
            watch_list = 1 if (bottom_count >= 4 and metrics_count >= 4) else 0
            
            records_to_insert.append({
                'company_id': co,
                'year': year,
                'peer_group_name': group_name,
                'is_benchmark': is_bench,
                'net_profit_margin_pct_pr': row.get('net_profit_margin_pct_pr'),
                'operating_profit_margin_pct_pr': row.get('operating_profit_margin_pct_pr'),
                'return_on_equity_pct_pr': row.get('return_on_equity_pct_pr'),
                'debt_to_equity_pr': row.get('debt_to_equity_pr'),
                'interest_coverage_pr': row.get('interest_coverage_pr'),
                'asset_turnover_pr': row.get('asset_turnover_pr'),
                'free_cash_flow_cr_pr': row.get('free_cash_flow_cr_pr'),
                'capex_cr_pr': row.get('capex_cr_pr'),
                'earnings_per_share_pr': row.get('earnings_per_share_pr'),
                'book_value_per_share_pr': row.get('book_value_per_share_pr'),
                'dividend_payout_ratio_pct_pr': row.get('dividend_payout_ratio_pct_pr'),
                'total_debt_cr_pr': row.get('total_debt_cr_pr'),
                'cash_from_operations_cr_pr': row.get('cash_from_operations_cr_pr'),
                'revenue_5yr_cagr_pr': row.get('revenue_5yr_cagr_pr'),
                'pat_5yr_cagr_pr': row.get('pat_5yr_cagr_pr'),
                'eps_5yr_cagr_pr': row.get('eps_5yr_cagr_pr'),
                'pe_ratio_pr': row.get('pe_ratio_pr'),
                'pb_ratio_pr': row.get('pb_ratio_pr'),
                'ev_ebitda_pr': row.get('ev_ebitda_pr'),
                'dividend_yield_pr': row.get('dividend_yield_pr'),
                'best_in_class': best_in_class,
                'watch_list': watch_list
            })
            
    # Save to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear old data
    cursor.execute("DELETE FROM peer_percentiles")
    
    insert_sql = """
        INSERT INTO peer_percentiles (
            company_id, year, peer_group_name, is_benchmark,
            net_profit_margin_pct_pr, operating_profit_margin_pct_pr, return_on_equity_pct_pr,
            debt_to_equity_pr, interest_coverage_pr, asset_turnover_pr,
            free_cash_flow_cr_pr, capex_cr_pr, earnings_per_share_pr,
            book_value_per_share_pr, dividend_payout_ratio_pct_pr, total_debt_cr_pr,
            cash_from_operations_cr_pr, revenue_5yr_cagr_pr, pat_5yr_cagr_pr,
            eps_5yr_cagr_pr, pe_ratio_pr, pb_ratio_pr, ev_ebitda_pr,
            dividend_yield_pr, best_in_class, watch_list
        ) VALUES (
            :company_id, :year, :peer_group_name, :is_benchmark,
            :net_profit_margin_pct_pr, :operating_profit_margin_pct_pr, :return_on_equity_pct_pr,
            :debt_to_equity_pr, :interest_coverage_pr, :asset_turnover_pr,
            :free_cash_flow_cr_pr, :capex_cr_pr, :earnings_per_share_pr,
            :book_value_per_share_pr, :dividend_payout_ratio_pct_pr, :total_debt_cr_pr,
            :cash_from_operations_cr_pr, :revenue_5yr_cagr_pr, :pat_5yr_cagr_pr,
            :eps_5yr_cagr_pr, :pe_ratio_pr, :pb_ratio_pr, :ev_ebitda_pr,
            :dividend_yield_pr, :best_in_class, :watch_list
        )
    """
    
    cursor.executemany(insert_sql, records_to_insert)
    conn.commit()
    conn.close()
    
    logger.info(f"Populated peer_percentiles in SQLite with {len(records_to_insert)} rows.")
