"""
Stock Screener and Filter Engine for Nifty 100 Financial Intelligence Platform
Implements custom stock filters, composite scoring, preset screeners, and trend checks.
"""

import os
import sqlite3
import yaml
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

def load_screener_config(config_path: str = "config/screener_config.yaml") -> dict:
    """Load stock screener threshold configurations"""
    if not os.path.exists(config_path):
        logger.error(f"Screener config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_screener_data(db_path: str, year: str) -> pd.DataFrame:
    """
    Load and join all required statements (companies, profitandloss, balancesheet,
    cashflow, analysis, market_cap, financial_ratios) for the given year.
    """
    conn = sqlite3.connect(db_path)
    
    # 1. Fetch tables
    df_pl = pd.read_sql_query(f"SELECT * FROM profitandloss WHERE year = '{year}'", conn)
    df_bs = pd.read_sql_query(f"SELECT * FROM balancesheet WHERE year = '{year}'", conn)
    df_cf = pd.read_sql_query(f"SELECT * FROM cashflow WHERE year = '{year}'", conn)
    df_ratios = pd.read_sql_query(f"SELECT * FROM financial_ratios WHERE year = '{year}'", conn)
    df_mkt = pd.read_sql_query(f"SELECT * FROM market_cap WHERE year = '{year}'", conn)
    
    # Load analysis and company sector metadata (which are latest or constant)
    df_analysis = pd.read_sql_query("SELECT * FROM analysis", conn)
    df_co = pd.read_sql_query("SELECT id, company_name, sector, face_value FROM companies", conn)
    df_sec = pd.read_sql_query("SELECT company_id, broad_sector, sub_sector FROM sectors", conn)
    
    conn.close()
    
    # Clean tickers
    for df in [df_pl, df_bs, df_cf, df_ratios, df_mkt, df_analysis, df_co, df_sec]:
        if not df.empty:
            for col in ['company_id', 'id']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.upper()
                    
    # Standardize column names for merge
    if not df_co.empty:
        df_co.rename(columns={'id': 'company_id'}, inplace=True)
        
    # Merge datasets
    merged = df_co.merge(df_sec, on='company_id', how='left')
    merged = merged.merge(df_pl, on='company_id', how='left', suffixes=('', '_pl'))
    merged = merged.merge(df_bs, on='company_id', how='left', suffixes=('', '_bs'))
    merged = merged.merge(df_cf, on='company_id', how='left', suffixes=('', '_cf'))
    merged = merged.merge(df_ratios, on='company_id', how='left', suffixes=('', '_ratio'))
    merged = merged.merge(df_analysis, on='company_id', how='left', suffixes=('', '_analysis'))
    
    # Join market cap details
    if not df_mkt.empty:
        merged = merged.merge(df_mkt[['company_id', 'market_cap_cr', 'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield']], on='company_id', how='left')
    else:
        # Create empty columns if market cap table is empty for that year
        for col in ['market_cap_cr', 'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield']:
            merged[col] = np.nan
            
    # Compute FCF yield as a custom column: FCF / Market Cap * 100
    merged['fcf_yield'] = merged.apply(
        lambda r: (r['free_cash_flow_cr'] / r['market_cap_cr'] * 100) if (pd.notna(r['free_cash_flow_cr']) and pd.notna(r['market_cap_cr']) and r['market_cap_cr'] > 0) else np.nan,
        axis=1
    )
    
    return merged

def winsorise_and_scale(series: pd.Series) -> pd.Series:
    """Winsorise series at P10/P90 and scale linearly from 0 to 100"""
    series_clean = series.dropna()
    if series_clean.empty:
        return pd.Series(0.0, index=series.index)
    p10 = series_clean.quantile(0.10)
    p90 = series_clean.quantile(0.90)
    if p90 == p10:
        return pd.Series(100.0, index=series.index)
    
    clipped = series.clip(lower=p10, upper=p90)
    scaled = (clipped - p10) / (p90 - p10) * 100
    # Fill NaN values with 0
    return scaled.fillna(0.0)

def score_de(de: Optional[float]) -> float:
    """Score Debt-to-Equity (10% weight) based on rules"""
    if de is None or pd.isna(de):
        return 0.0
    if de <= 0:
        return 100.0
    elif de <= 0.5:
        return 100.0 - (de / 0.5) * 15
    elif de <= 1.0:
        return 85.0 - ((de - 0.5) / 0.5) * 15
    elif de <= 2.0:
        return 70.0 - ((de - 1.0) / 1.0) * 20
    elif de <= 5.0:
        return 50.0 - ((de - 2.0) / 3.0) * 50
    else:
        return 0.0

def score_icr(icr: Optional[float]) -> float:
    """Score Interest Coverage Ratio (5% weight) based on rules"""
    if icr is None or pd.isna(icr):
        return 100.0  # None represents interest=0 (debt-free) -> score = 100
    if icr <= 1.5:
        return 0.0
    elif icr <= 3.0:
        return ((icr - 1.5) / 1.5) * 50
    elif icr <= 5.0:
        return 50.0 + ((icr - 3.0) / 2.0) * 25
    elif icr <= 10.0:
        return 75.0 + ((icr - 5.0) / 5.0) * 25
    else:
        return 100.0

def calculate_composite_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate global Composite Scores (0-100 range) using specified weights.
    Returns the input DataFrame with a new 'composite_score' column.
    """
    df_scores = df.copy()
    
    # 1. Profitability (35%)
    # EBIT = operating_profit - depreciation
    df_scores['ebit'] = df_scores['operating_profit'] - df_scores['depreciation']
    # Capital Employed = equity_capital + reserves + borrowings
    df_scores['capital_employed'] = df_scores['equity_capital'] + df_scores['reserves'] + df_scores['borrowings']
    df_scores['roce'] = df_scores.apply(
        lambda r: (r['ebit'] / r['capital_employed'] * 100) if (pd.notna(r['ebit']) and pd.notna(r['capital_employed']) and r['capital_employed'] > 0) else np.nan,
        axis=1
    )
    
    # Winsorise and scale profitability dimensions
    s_roe = winsorise_and_scale(df_scores['return_on_equity_pct'])
    s_roce = winsorise_and_scale(df_scores['roce'])
    s_npm = winsorise_and_scale(df_scores['net_profit_margin_pct'])
    
    # 2. Cash Quality (30%)
    # Let's check for FCF 5yr CAGR or use PAT 5yr CAGR as a proxy for growth dimension,
    # and calculate FCF 5yr CAGR if we have the data series.
    # To keep it robust, we'll winsorise and scale the pat_5yr_cagr as the FCF CAGR proxy if FCF CAGR is not direct,
    # or calculate it. Let's winsorise pat_5yr_cagr.
    s_fcf_cagr = winsorise_and_scale(df_scores['pat_5yr_cagr']) # proxy
    
    # CFO/PAT ratio
    df_scores['cfo_pat_ratio'] = df_scores.apply(
        lambda r: (r['cash_from_operations_cr'] / r['net_profit']) if (pd.notna(r['cash_from_operations_cr']) and pd.notna(r['net_profit']) and r['net_profit'] > 0) else np.nan,
        axis=1
    )
    s_cfo_pat = winsorise_and_scale(df_scores['cfo_pat_ratio'])
    s_fcf_pos = df_scores['free_cash_flow_cr'].apply(lambda x: 100.0 if (pd.notna(x) and x > 0) else 0.0)
    
    # 3. Growth (20%)
    # For growth CAGR, set score to 0 if CAGR is None (which represents turnaround or undefined growth)
    s_rev_cagr = df_scores['revenue_5yr_cagr'].apply(lambda x: 0.0 if pd.isna(x) else x)
    s_rev_cagr = winsorise_and_scale(s_rev_cagr)
    
    s_pat_cagr = df_scores['pat_5yr_cagr'].apply(lambda x: 0.0 if pd.isna(x) else x)
    s_pat_cagr = winsorise_and_scale(s_pat_cagr)
    
    # 4. Leverage (15%)
    s_de = df_scores['debt_to_equity'].apply(score_de)
    s_icr = df_scores['interest_coverage'].apply(score_icr)
    
    # 5. Composite Score Calculation
    df_scores['composite_score'] = (
        s_roe * 0.15 + s_roce * 0.10 + s_npm * 0.10 +
        s_fcf_cagr * 0.15 + s_cfo_pat * 0.10 + s_fcf_pos * 0.05 +
        s_rev_cagr * 0.10 + s_pat_cagr * 0.10 +
        s_de * 0.10 + s_icr * 0.05
    )
    
    df_scores['composite_score'] = df_scores['composite_score'].round(4)
    return df_scores

def run_preset_screener(df: pd.DataFrame, preset_name: str, config: dict, db_path: str = None) -> pd.DataFrame:
    """
    Run stock screener based on a preset name and config.
    Applies filters, rankings, and custom turnaround conditions.
    """
    presets = config.get('presets', {})
    if preset_name not in presets:
        logger.error(f"Preset '{preset_name}' not defined in config.")
        raise ValueError(f"Preset '{preset_name}' not defined in config.")
        
    preset = presets[preset_name]
    filters = preset.get('filters', {})
    rank_by = preset.get('rank_by', 'composite_score')
    order = preset.get('order', 'desc')
    
    filtered_df = df.copy()
    
    # Apply standard filters
    for field, rule in filters.items():
        if field in ['fcf_improving', 'de_declining']:
            # Custom trend checks will be handled separately
            continue
            
        if 'min' in rule:
            filtered_df = filtered_df[filtered_df[field] >= rule['min']]
        if 'max' in rule:
            filtered_df = filtered_df[filtered_df[field] <= rule['max']]
            
    # Apply custom turnaround checks for "Turnaround Watch"
    if preset_name == "Turnaround Watch" and db_path is not None:
        valid_tickers = []
        conn = sqlite3.connect(db_path)
        
        # Load FCF and DE history for trend check
        # We need the last 2 years for each company
        df_history = pd.read_sql_query("SELECT company_id, year, free_cash_flow_cr, debt_to_equity FROM financial_ratios", conn)
        conn.close()
        
        df_history['company_id'] = df_history['company_id'].str.strip().str.upper()
        df_history['year'] = df_history['year'].str.strip()
        
        for ticker in filtered_df['company_id'].unique():
            co_hist = df_history[df_history['company_id'] == ticker].sort_values('year')
            if len(co_hist) >= 2:
                # FCF improving: latest FCF > previous FCF
                fcf_hist = co_hist['free_cash_flow_cr'].tolist()
                fcf_ok = fcf_hist[-1] > fcf_hist[-2]
                
                # D/E declining: latest D/E < previous D/E
                de_hist = co_hist['debt_to_equity'].tolist()
                # Handle None values
                if de_hist[-1] is not None and de_hist[-2] is not None:
                    de_ok = de_hist[-1] < de_hist[-2]
                elif de_hist[-1] == 0.0 and de_hist[-2] is not None and de_hist[-2] > 0.0:
                    de_ok = True
                else:
                    de_ok = False
                    
                if fcf_ok and de_ok:
                    valid_tickers.append(ticker)
            else:
                # If only 1 year of data, cannot compute trend
                pass
                
        filtered_df = filtered_df[filtered_df['company_id'].isin(valid_tickers)]
        
    # Sort results
    ascending = (order == 'asc')
    filtered_df = filtered_df.sort_values(rank_by, ascending=ascending)
    
    return filtered_df

def apply_multi_year_trend_filter(db_path: str, metric: str, consecutive_years: int) -> List[str]:
    """
    Returns a list of company_ids where the specified metric improved consecutively
    for `consecutive_years` years.
    Supported metrics are columns in profitandloss or balancesheet tables.
    """
    conn = sqlite3.connect(db_path)
    
    # Query database based on which table has the metric
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(profitandloss)")
    pl_cols = [r[1] for r in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(balancesheet)")
    bs_cols = [r[1] for r in cursor.fetchall()]
    
    conn.close()
    
    query = ""
    if metric in pl_cols:
        query = f"SELECT company_id, year, {metric} FROM profitandloss"
    elif metric in bs_cols:
        query = f"SELECT company_id, year, {metric} FROM balancesheet"
    else:
        logger.error(f"Metric '{metric}' not found in time-series tables.")
        return []
        
    conn = sqlite3.connect(db_path)
    df_hist = pd.read_sql_query(query, conn)
    conn.close()
    
    df_hist['company_id'] = df_hist['company_id'].str.strip().str.upper()
    df_hist['year'] = df_hist['year'].str.strip()
    
    matching_companies = []
    
    for ticker in df_hist['company_id'].unique():
        co_hist = df_hist[df_hist['company_id'] == ticker].sort_values('year')
        vals = co_hist[metric].dropna().tolist()
        
        if len(vals) < consecutive_years + 1:
            continue
            
        recent = vals[-(consecutive_years + 1):]
        # Check if strictly increasing
        improved = True
        for i in range(1, len(recent)):
            if recent[i] <= recent[i-1]:
                improved = False
                break
        if improved:
            matching_companies.append(ticker)
            
    return matching_companies
