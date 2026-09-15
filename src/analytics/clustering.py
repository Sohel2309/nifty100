"""
Statistical Analysis & Clustering Engine for Nifty 100 Financial Intelligence Platform
Uses scikit-learn KMeans for clustering, performs outlier detection, and correlation matrices.
"""

import os
import sqlite3
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

def run_clustering_analysis(db_path: str):
    """Run scikit-learn clustering and save statistical outputs"""
    logger.info(f"Connecting to database for Clustering analysis: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # 1. Load company info and financial metrics for latest year (2024-03)
    latest_year = "2024-03"
    df_co = pd.read_sql_query("SELECT id, company_name, sector FROM companies", conn)
    df_sec = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
    df_ratios = pd.read_sql_query(f"SELECT * FROM financial_ratios WHERE year = '{latest_year}'", conn)
    df_analysis = pd.read_sql_query("SELECT * FROM analysis", conn)
    df_mkt = pd.read_sql_query(f"SELECT * FROM market_cap WHERE year = '{latest_year}'", conn)
    
    conn.close()
    
    # Clean company IDs
    for df in [df_co, df_sec, df_ratios, df_analysis, df_mkt]:
        for col in ['company_id', 'id']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
                
    df_co.rename(columns={'id': 'company_id'}, inplace=True)
    df_co_sec = df_co.merge(df_sec, on='company_id', how='left')
    df_co_sec['broad_sector'] = df_co_sec['broad_sector'].fillna(df_co_sec['sector'])
    
    # Merge datasets to create a single flat DataFrame
    df_flat = df_co_sec.merge(df_ratios, on='company_id', how='left')
    df_flat = df_flat.merge(df_analysis, on='company_id', how='left', suffixes=('', '_analysis'))
    df_flat = df_flat.merge(df_mkt[['company_id', 'pe_ratio', 'pb_ratio', 'dividend_yield']], on='company_id', how='left')
    
    # ============================================================
    # 10.1: KMeans Clustering (5 clusters)
    # ============================================================
    # Features: ROE, D/E, Revenue CAGR (5yr), PAT CAGR (5yr), OPM
    features = ['return_on_equity_pct', 'debt_to_equity', 'revenue_5yr_cagr', 'pat_5yr_cagr', 'operating_profit_margin_pct']
    
    df_cluster_input = df_flat[['company_id', 'company_name'] + features].copy()
    
    # Impute missing values with column medians for KMeans stability
    for f in features:
        med = df_cluster_input[f].median()
        df_cluster_input[f] = df_cluster_input[f].fillna(med if pd.notna(med) else 0.0)
        
    X = df_cluster_input[features].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Run KMeans
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df_cluster_input['cluster_id'] = kmeans.fit_predict(X_scaled)
    
    # Programmatic mapping of cluster_id to descriptive labels based on ROE sorting
    cluster_means = df_cluster_input.groupby('cluster_id')['return_on_equity_pct'].mean().reset_index()
    # Sort clusters by mean ROE ascending
    cluster_means_sorted = cluster_means.sort_values('return_on_equity_pct').reset_index(drop=True)
    
    # Mapping
    labels = ['Distressed', 'Value Cyclicals', 'Emerging Growth', 'Defensive Dividend', 'High-Quality Growth']
    cluster_label_map = {row['cluster_id']: labels[i] for i, row in cluster_means_sorted.iterrows()}
    
    df_cluster_input['cluster_label'] = df_cluster_input['cluster_id'].map(cluster_label_map)
    
    # Save cluster_labels.csv
    Path("output").mkdir(exist_ok=True)
    df_cluster_input[['company_id', 'company_name', 'cluster_id', 'cluster_label']].to_csv("output/cluster_labels.csv", index=False)
    logger.info("Saved cluster_labels.csv to output/.")
    
    # ============================================================
    # 10.3: Pearson Correlation Heatmap
    # ============================================================
    corr_cols = [
        'return_on_equity_pct', 'net_profit_margin_pct', 'operating_profit_margin_pct',
        'debt_to_equity', 'interest_coverage', 'asset_turnover', 'free_cash_flow_cr',
        'pe_ratio', 'pb_ratio', 'dividend_yield'
    ]
    df_corr = df_flat[corr_cols].dropna()
    
    corr_matrix = df_corr.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    
    # Set ticks and labels
    ticks = np.arange(0, len(corr_cols), 1)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    # Rotate labels
    ax.set_xticklabels(corr_cols, rotation=90, fontsize=8, fontname='Times New Roman')
    ax.set_yticklabels(corr_cols, fontsize=8, fontname='Times New Roman')
    
    # Add text annotations
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha='center', va='center', color='black', size=8, fontname='Times New Roman')
            
    plt.title('Nifty 100 KPI Pearson Correlation Matrix (FY24)', fontsize=12, weight='bold', fontname='Times New Roman', y=1.2)
    plt.tight_layout()
    plt.savefig("output/correlation_heatmap.png", dpi=120)
    plt.close()
    logger.info("Saved correlation_heatmap.png to output/.")
    
    # ============================================================
    # 10.4: Z-Score Sector Outlier Detection
    # ============================================================
    outliers = []
    outlier_metrics = ['return_on_equity_pct', 'debt_to_equity', 'pe_ratio']
    
    # Group by broad sector
    for sec_name, sec_df in df_flat.groupby('broad_sector'):
        if len(sec_df) < 3:
            # Skip sectors with too few members for z-score stability
            continue
        for m in outlier_metrics:
            mean = sec_df[m].mean()
            std = sec_df[m].std()
            if pd.isna(std) or std <= 0:
                continue
            for _, row in sec_df.iterrows():
                val = row[m]
                if pd.notna(val):
                    z = (val - mean) / std
                    if abs(z) > 3.0:
                        outliers.append({
                            'company_id': row['company_id'],
                            'company_name': row['company_name'],
                            'broad_sector': sec_name,
                            'metric': m,
                            'value': round(val, 4),
                            'sector_mean': round(mean, 4),
                            'z_score': round(z, 4)
                        })
                        
    df_outliers = pd.DataFrame(outliers)
    if df_outliers.empty:
        df_outliers = pd.DataFrame(columns=['company_id', 'company_name', 'broad_sector', 'metric', 'value', 'sector_mean', 'z_score'])
    df_outliers.to_csv("output/outlier_report.csv", index=False)
    logger.info("Saved outlier_report.csv to output/.")
    
    # ============================================================
    # 10.5: Portfolio Percentile Statistics
    # ============================================================
    portfolio_metrics = ['return_on_equity_pct', 'debt_to_equity', 'pe_ratio']
    percentile_data = []
    
    for m in portfolio_metrics:
        series = df_flat[m].dropna()
        if not series.empty:
            percentile_data.append({
                'Metric': m,
                'Count': len(series),
                'P10': round(series.quantile(0.10), 4),
                'P25': round(series.quantile(0.25), 4),
                'P50': round(series.quantile(0.50), 4),
                'P75': round(series.quantile(0.75), 4),
                'P90': round(series.quantile(0.90), 4),
                'Min': round(series.min(), 4),
                'Max': round(series.max(), 4)
            })
            
    df_pct = pd.DataFrame(percentile_data)
    df_pct.to_csv("output/portfolio_stats.csv", index=False)
    logger.info("Saved portfolio_stats.csv to output/.")
    logger.info("Statistical Analysis and Clustering completed successfully!")

def main():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    run_clustering_analysis(db_path)

if __name__ == '__main__':
    main()
