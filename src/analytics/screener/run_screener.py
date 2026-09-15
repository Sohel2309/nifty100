"""
Orchestration Script to Run the 6 Stock Screener Presets
Computes composite scores and exports results to output/screener_output.xlsx.
"""

import os
import logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from src.analytics.screener.engine import (
    load_screener_config,
    load_screener_data,
    calculate_composite_scores,
    run_preset_screener
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    db_path = os.getenv("DB_PATH", "./data/nifty100.db")
    config_path = "config/screener_config.yaml"
    output_path = "output/screener_output.xlsx"
    
    logger.info(f"Using database: {db_path}")
    logger.info(f"Using config: {config_path}")
    
    # 1. Load data
    df_data = load_screener_data(db_path, "2024-03")
    
    # 2. Compute composite scores
    df_scored = calculate_composite_scores(df_data)
    
    # 3. Load config
    config = load_screener_config(config_path)
    presets = config.get('presets', {})
    
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)
    
    # Write to Excel with ExcelWriter
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for preset_name in presets.keys():
            logger.info(f"Running screener preset: {preset_name}")
            
            # Execute preset
            res = run_preset_screener(df_scored, preset_name, config, db_path)
            
            # Select columns to display in excel based on preset filters and rankings
            cols_to_keep = [
                'company_id', 'company_name', 'sector', 'broad_sector', 'composite_score',
                'return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 'pe_ratio',
                'pb_ratio', 'dividend_yield', 'fcf_yield', 'revenue_5yr_cagr', 'pat_5yr_cagr'
            ]
            # Keep only columns that exist
            cols_to_keep = [c for c in cols_to_keep if c in res.columns]
            
            preset_export = res[cols_to_keep].copy()
            
            # Save sheet
            sheet_name = preset_name[:31]  # Excel sheet name limit is 31 chars
            preset_export.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"Saved {len(preset_export)} companies for preset '{preset_name}' into sheet '{sheet_name}'.")
            
    logger.info(f"Stock screener outputs successfully exported to: {output_path}")

if __name__ == '__main__':
    main()
