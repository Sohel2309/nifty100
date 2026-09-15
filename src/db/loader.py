"""
SQLite Database Loader for Nifty 100 Financial Intelligence Platform
Handles database initialization, data ingestion, data quality cleaning, and load auditing.
"""

import sqlite3
import pandas as pd
import numpy as np
import logging
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from src.etl.loader import ExcelLoader, normalize_year, normalize_ticker
from src.etl.validator import SchemaValidator, Severity

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# AUDIT DATA CLASS
# ============================================================

@dataclass
class LoadAuditRecord:
    """Represents a single load audit entry"""
    dataset: str
    rows_in: int
    rows_inserted: int
    rows_rejected: int
    rejection_reasons: Dict[str, int]
    load_duration_sec: float
    timestamp: str
    status: str  # 'SUCCESS' or 'PARTIAL' or 'FAILED'
    
    def to_dict(self):
        return {
            'dataset': self.dataset,
            'rows_in': self.rows_in,
            'rows_inserted': self.rows_inserted,
            'rows_rejected': self.rows_rejected,
            'rejection_reasons': json.dumps(self.rejection_reasons),
            'load_duration_sec': self.load_duration_sec,
            'timestamp': self.timestamp,
            'status': self.status,
        }


# ============================================================
# DATABASE LOADER CLASS
# ============================================================

class DatabaseLoader:
    """Loads normalized DataFrames into SQLite database with validation and auditing"""
    
    # Target database table schema columns matching schema.sql
    TABLE_SCHEMAS = {
        'companies': [
            'id', 'company_name', 'sector', 'sub_sector', 'market_cap_2024', 'face_value',
            'website', 'nse_profile', 'bse_profile', 'company_logo', 'about_company',
            'chart_link', 'book_value', 'roce_percentage', 'roe_percentage'
        ],
        'profitandloss': [
            'company_id', 'year', 'sales', 'expenses', 'operating_profit', 'depreciation',
            'other_income', 'interest', 'tax', 'net_profit', 'eps', 'opm_percentage',
            'tax_percentage', 'dividend_payout'
        ],
        'balancesheet': [
            'company_id', 'year', 'equity_capital', 'reserves', 'total_equity', 'borrowings',
            'other_liabilities', 'total_liabilities', 'current_assets', 'fixed_assets',
            'total_assets', 'investments', 'cash_and_equivalents'
        ],
        'cashflow': [
            'company_id', 'year', 'operating_activity', 'depreciation_added_back',
            'working_capital_change', 'investing_activity', 'capital_expenditure',
            'acquisitions', 'financing_activity', 'dividends_paid', 'debt_raised',
            'debt_repaid', 'net_cash_flow'
        ],
        'analysis': [
            'company_id', 'revenue_3yr_cagr', 'revenue_5yr_cagr', 'revenue_10yr_cagr',
            'pat_3yr_cagr', 'pat_5yr_cagr', 'pat_10yr_cagr', 'eps_3yr_cagr',
            'eps_5yr_cagr', 'eps_10yr_cagr', 'roe_5yr_avg', 'roic_5yr_avg'
        ],
        'documents': [
            'company_id', 'year', 'document_name', 'document_url', 'document_type'
        ],
        'prosandcons': [
            'company_id', 'pros', 'cons'
        ],
        'sectors': [
            'company_id', 'broad_sector', 'sub_sector', 'peer_group'
        ],
        'stock_prices': [
            'company_id', 'date', 'open', 'high', 'low', 'close', 'volume'
        ],
        'market_cap': [
            'company_id', 'year', 'market_cap_cr', 'earnings_cr', 'book_value_cr',
            'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield'
        ],
        'financial_ratios': [
            'company_id', 'year', 'net_profit_margin_pct', 'operating_profit_margin_pct',
            'return_on_equity_pct', 'debt_to_equity', 'interest_coverage', 'asset_turnover',
            'free_cash_flow_cr', 'capex_cr', 'earnings_per_share', 'book_value_per_share',
            'dividend_payout_ratio_pct', 'total_debt_cr', 'cash_from_operations_cr'
        ],
        'peer_groups': [
            'peer_group_name', 'company_id', 'is_benchmark'
        ]
    }
    
    def __init__(self, db_path: str = './data/nifty100.db', schema_path: str = './src/db/schema.sql'):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.connection: Optional[sqlite3.Connection] = None
        self.audit_records: List[LoadAuditRecord] = []
        
        logger.info(f"DatabaseLoader initialized | DB: {self.db_path} | Schema: {self.schema_path}")
        
    def initialize_database(self, force_recreate: bool = False) -> bool:
        """Create database tables from schema.sql script"""
        try:
            if force_recreate and self.db_path.exists():
                logger.warning(f"Recreating database. Deleting old: {self.db_path}")
                self.close()
                self.db_path.unlink()
                
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema SQL script not found at {self.schema_path}")
                
            schema_sql = self.schema_path.read_text()
            
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.executescript(schema_sql)
            self.connection.commit()
            
            logger.info("✓ Database initialized successfully from schema.sql")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {str(e)}")
            return False
            
    def connect(self) -> bool:
        """Connect to the database and enable foreign keys"""
        try:
            if not self.db_path.exists():
                return self.initialize_database()
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {str(e)}")
            return False
            
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def load_dataframe(self, df: pd.DataFrame, table_name: str) -> LoadAuditRecord:
        """Load a cleaned DataFrame into a SQLite table inside a transaction"""
        start_time = datetime.now()
        rows_in = len(df)
        rows_inserted = 0
        rows_rejected = 0
        rejection_reasons = {}
        
        if not self.connection:
            raise RuntimeError("Database connection not open.")
            
        try:
            expected_cols = self.TABLE_SCHEMAS[table_name]
            
            # Make a copy to avoid SettingWithCopyWarning
            df = df.copy()
            
            # 1. Fill missing columns with None/NaN
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
                    
            # 2. Re-order to match expected columns
            df_to_load = df[expected_cols].copy()
            
            # 3. Clean and convert data types
            text_columns = {
                'id', 'company_id', 'company_name', 'sector', 'sub_sector', 'website',
                'nse_profile', 'bse_profile', 'company_logo', 'about_company', 'chart_link',
                'year', 'date', 'document_name', 'document_url', 'document_type', 'pros', 'cons',
                'broad_sector', 'peer_group', 'peer_group_name'
            }
            
            for col in df_to_load.columns:
                if col in text_columns:
                    df_to_load[col] = df_to_load[col].apply(lambda x: None if pd.isna(x) or str(x).strip() in ['None', 'nan', 'NaN', ''] else str(x).strip())
                else:
                    # Numeric column cleaning
                    if df_to_load[col].dtype == 'object':
                        df_to_load[col] = df_to_load[col].astype(str).str.replace(',', '', regex=False).str.strip()
                    df_to_load[col] = pd.to_numeric(df_to_load[col], errors='coerce')
            
            # Convert NaNs/NaTs to None for SQLite insertion
            df_to_load = df_to_load.astype(object).where(pd.notnull(df_to_load), None)
            
            # Use SQLite transaction
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {table_name}") # Clear existing
            
            placeholders = ",".join(["?" for _ in expected_cols])
            insert_query = f"INSERT INTO {table_name} ({','.join(expected_cols)}) VALUES ({placeholders})"
            
            # Insert row by row to catch FK and integrity constraint violations
            for idx, row in df_to_load.iterrows():
                try:
                    vals = list(row)
                    cursor.execute(insert_query, vals)
                    rows_inserted += 1
                except sqlite3.IntegrityError as e:
                    rows_rejected += 1
                    err_msg = str(e)
                    rejection_reasons[err_msg] = rejection_reasons.get(err_msg, 0) + 1
                    logger.warning(f"Row {idx} rejected in {table_name} due to IntegrityError: {err_msg}")
                    
            self.connection.commit()
            duration = (datetime.now() - start_time).total_seconds()
            status = 'SUCCESS' if rows_rejected == 0 else 'PARTIAL'
            
            audit = LoadAuditRecord(
                dataset=table_name,
                rows_in=rows_in,
                rows_inserted=rows_inserted,
                rows_rejected=rows_rejected,
                rejection_reasons=rejection_reasons,
                load_duration_sec=duration,
                timestamp=datetime.now().isoformat(),
                status=status
            )
            self.audit_records.append(audit)
            logger.info(f"Loaded table '{table_name}': {rows_inserted}/{rows_in} rows inserted ({rows_rejected} rejected)")
            return audit
            
        except Exception as e:
            self.connection.rollback()
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"✗ Load failed for table {table_name}: {str(e)}")
            audit = LoadAuditRecord(
                dataset=table_name,
                rows_in=rows_in,
                rows_inserted=0,
                rows_rejected=rows_in,
                rejection_reasons={'Exception': 1},
                load_duration_sec=duration,
                timestamp=datetime.now().isoformat(),
                status='FAILED'
            )
            self.audit_records.append(audit)
            return audit

    def export_audit_to_csv(self, output_path: str = 'output/load_audit.csv') -> str:
        """Export audit records to CSV"""
        audit_data = [r.to_dict() for r in self.audit_records]
        df_audit = pd.DataFrame(audit_data)
        df_audit.to_csv(output_path, index=False)
        logger.info(f"Load audit log exported to: {output_path}")
        return output_path

    def print_summary(self):
        """Print database summary report"""
        print("\n" + "="*80)
        print("DATABASE LOAD PROCESS SUMMARY")
        print("="*80)
        total_in = sum(r.rows_in for r in self.audit_records)
        total_ins = sum(r.rows_inserted for r in self.audit_records)
        total_rej = sum(r.rows_rejected for r in self.audit_records)
        
        print(f"Total rows read:      {total_in}")
        print(f"Total rows inserted:  {total_ins}")
        print(f"Total rows rejected:  {total_rej}")
        print(f"Overall Success Rate: {(total_ins/total_in*100):.2f}%" if total_in > 0 else "N/A")
        print("-"*80)
        print(f"{'Table Name':20} | {'Read':8} | {'Loaded':8} | {'Rejected':8} | {'Status':8}")
        print("-"*80)
        for r in self.audit_records:
            print(f"{r.dataset:20} | {r.rows_in:8d} | {r.rows_inserted:8d} | {r.rows_rejected:8d} | {r.status:8}")
        print("="*80 + "\n")


# ============================================================
# HELPER PARSER FUNCTIONS
# ============================================================

def parse_cagr_text(text: str, years: int) -> Optional[float]:
    """Parse CAGR text like '10 Years: 21%' or '5 Years: 18%'"""
    if pd.isna(text):
        return None
    matches = re.findall(r'(\d+)\s*Years?:?\s*(-?[\d.]+)%', str(text))
    for y_str, val_str in matches:
        if int(y_str) == years:
            return float(val_str)
    return None


# ============================================================
# ORCHESTRATION PIPELINE
# ============================================================

def run_etl_load(db_path: str = './data/nifty100.db', schema_path: str = './src/db/schema.sql', data_dir: str = './data'):
    """Run full ETL ingestion and loading pipeline"""
    logger.info("Starting Nifty 100 ETL Load Ingestion...")
    
    loader = ExcelLoader(data_dir=data_dir)
    db = DatabaseLoader(db_path=db_path, schema_path=schema_path)
    
    # 1. Initialize DB schema
    if not db.initialize_database(force_recreate=True):
        logger.error("DB Initialization failed. Exiting.")
        return
        
    # 2. Ingest 7 Core DataFrames
    core_dfs = loader.load_all_core_datasets()
    
    # 3. Load supplementary Excel files
    logger.info("Loading supplementary datasets...")
    df_sectors = pd.read_excel(Path(data_dir) / "supporting datasets" / "sectors.xlsx")
    df_prices = pd.read_excel(Path(data_dir) / "supporting datasets" / "stock_prices.xlsx")
    df_mktcap = pd.read_excel(Path(data_dir) / "supporting datasets" / "market_cap.xlsx")
    df_peer = pd.read_excel(Path(data_dir) / "supporting datasets" / "peer_groups.xlsx")
    df_ratios = pd.read_excel(Path(data_dir) / "supporting datasets" / "financial_ratios.xlsx")
    
    # 4. Normalize supplementary company_ids and dates/years
    for df in [df_sectors, df_prices, df_mktcap, df_peer, df_ratios]:
        if 'company_id' in df.columns:
            df['company_id'] = df['company_id'].apply(normalize_ticker)
            
    if 'date' in df_prices.columns:
        df_prices['date'] = df_prices['date'].astype(str).str.strip()
        
    if 'year' in df_mktcap.columns:
        # market_cap.xlsx uses integer years like 2024. Standardize to string
        df_mktcap['year'] = df_mktcap['year'].astype(str).str.strip()

    if 'year' in df_ratios.columns:
        df_ratios['year'] = df_ratios['year'].apply(normalize_year)

    if 'is_benchmark' in df_peer.columns:
        # Standardize is_benchmark boolean to 0 or 1 for SQLite CHECK constraint
        df_peer['is_benchmark'] = df_peer['is_benchmark'].astype(int)

    # 5. Apply DQ Checks and Actions BEFORE Load
    # We validate raw data first
    validator = SchemaValidator(data_dir=data_dir)
    all_dfs = core_dfs.copy()
    all_dfs['sectors'] = df_sectors
    all_dfs['stock_prices'] = df_prices
    all_dfs['market_cap'] = df_mktcap
    all_dfs['financial_ratios'] = df_ratios
    all_dfs['peer_groups'] = df_peer
    validator.validate_all(all_dfs)
    validator.export_failures_to_csv('output/validation_failures.csv')
    
    # DQ-01: Companies PK Uniqueness check. Companies master list:
    df_co = core_dfs['companies'].copy()
    df_co['id'] = df_co['id'].apply(normalize_ticker)
    
    # DQ-02: deduplicate companies
    df_co = df_co.drop_duplicates(subset=['id'], keep='last')
    companies_ids = set(df_co['id'].dropna().unique())
    
    # Enrich companies table with Sector and latest Market Cap
    # sector column from sectors.xlsx (broad_sector)
    df_sec_norm = df_sectors.copy()
    df_sec_norm['company_id'] = df_sec_norm['company_id'].apply(normalize_ticker)
    
    # Merge sector information
    df_co = df_co.merge(df_sec_norm[['company_id', 'broad_sector', 'sub_sector']], left_on='id', right_on='company_id', how='left')
    df_co['sector'] = df_co['broad_sector'].fillna('Other')
    df_co['sub_sector'] = df_co['sub_sector'].fillna('Other')
    df_co = df_co.drop(columns=['company_id', 'broad_sector'])
    
    # Merge market cap for 2024
    df_mkt_2024 = df_mktcap[df_mktcap['year'].astype(str) == '2024'].copy()
    df_mkt_2024['company_id'] = df_mkt_2024['company_id'].apply(normalize_ticker)
    df_co = df_co.merge(df_mkt_2024[['company_id', 'market_cap_crore']], left_on='id', right_on='company_id', how='left')
    df_co['market_cap_2024'] = df_co['market_cap_crore']
    df_co = df_co.drop(columns=['company_id', 'market_cap_crore'])
    
    # Load companies table first so FK constraints work
    db.load_dataframe(df_co, 'companies')

    # Merge core dfs and new supplementary dataframes for uniform processing
    dfs_to_process = core_dfs.copy()
    dfs_to_process['financial_ratios'] = df_ratios
    dfs_to_process['peer_groups'] = df_peer

    # For other tables, apply rejections/cleanups based on DQ constraints
    for name in ['profitandloss', 'balancesheet', 'cashflow', 'analysis', 'documents', 'prosandcons', 'financial_ratios', 'peer_groups']:
        df = dfs_to_process[name].copy()
        
        # DQ-08: normalise ticker and check length
        ticker_col = 'company_id'
        df[ticker_col] = df[ticker_col].apply(normalize_ticker)
        df = df[df[ticker_col].notna() & (df[ticker_col].astype(str).str.len() >= 2) & (df[ticker_col].astype(str).str.len() <= 12)]
        
        # DQ-03: FK Integrity (Reject orphan rows)
        df = df[df[ticker_col].isin(companies_ids)]
        
        # Standardize year formatting if present
        if 'year' in df.columns or 'Year' in df.columns:
            year_col = 'Year' if 'Year' in df.columns else 'year'
            df[year_col] = df[year_col].apply(normalize_year)
            df = df[df[year_col].notna()]
            if year_col == 'Year':
                df = df.rename(columns={'Year': 'year'})
                
        # DQ-02: deduplicate composite keys (keep last)
        if 'year' in df.columns:
            df = df.drop_duplicates(subset=['company_id', 'year'], keep='last')
        elif name == 'peer_groups':
            df = df.drop_duplicates(subset=['peer_group_name', 'company_id'], keep='last')
            
        # DQ-10: non-negative fixed assets coercion in Balance Sheet
        if name == 'balancesheet' and 'fixed_assets' in df.columns:
            df.loc[df['fixed_assets'] < 0, 'fixed_assets'] = 0.0
            
        # Compute total_equity for balancesheet
        if name == 'balancesheet' and 'equity_capital' in df.columns and 'reserves' in df.columns:
            df['total_equity'] = df['equity_capital'] + df['reserves']
            df['current_assets'] = df['other_asset']
            
        # Compute tax for profitandloss
        if name == 'profitandloss' and 'profit_before_tax' in df.columns and 'net_profit' in df.columns:
            df['tax'] = df['profit_before_tax'] - df['net_profit']
            
        # Parse analysis text for CAGR
        if name == 'analysis':
            df = df.drop_duplicates(subset=['company_id'], keep='last')
            df['revenue_3yr_cagr'] = df['compounded_sales_growth'].apply(lambda x: parse_cagr_text(x, 3))
            df['revenue_5yr_cagr'] = df['compounded_sales_growth'].apply(lambda x: parse_cagr_text(x, 5))
            df['revenue_10yr_cagr'] = df['compounded_sales_growth'].apply(lambda x: parse_cagr_text(x, 10))
            df['pat_3yr_cagr'] = df['compounded_profit_growth'].apply(lambda x: parse_cagr_text(x, 3))
            df['pat_5yr_cagr'] = df['compounded_profit_growth'].apply(lambda x: parse_cagr_text(x, 5))
            df['pat_10yr_cagr'] = df['compounded_profit_growth'].apply(lambda x: parse_cagr_text(x, 10))
            df['roe_5yr_avg'] = df['roe'].apply(lambda x: parse_cagr_text(x, 5))
            
        # Map documents columns
        if name == 'documents':
            df['document_url'] = df['Annual_Report']
            df['document_name'] = df['company_id'] + " Annual Report " + df['year'].astype(str).str[:4]
            df['document_type'] = "Annual Report"
            
        # Group pros and cons by company_id for prosandcons
        if name == 'prosandcons':
            df = df.groupby('company_id').agg({
                'pros': lambda x: '\n'.join(x.dropna().astype(str).unique()),
                'cons': lambda x: '\n'.join(x.dropna().astype(str).unique())
            }).reset_index()
            
        # Load core table
        db.load_dataframe(df, name)
        
    # 6. Process and load supplementary tables
    # Sectors Table: merge broad_sector and peer_group
    df_sec_to_load = df_sectors.copy()
    df_sec_to_load['company_id'] = df_sec_to_load['company_id'].apply(normalize_ticker)
    df_sec_to_load = df_sec_to_load[df_sec_to_load['company_id'].isin(companies_ids)]
    
    # Merge peer group name
    df_peer_norm = df_peer.copy()
    df_peer_norm['company_id'] = df_peer_norm['company_id'].apply(normalize_ticker)
    df_sec_to_load = df_sec_to_load.merge(df_peer_norm[['company_id', 'peer_group_name']], on='company_id', how='left')
    df_sec_to_load['peer_group'] = df_sec_to_load['peer_group_name']
    
    # Load sectors
    db.load_dataframe(df_sec_to_load, 'sectors')
    
    # Stock prices table
    df_prices_to_load = df_prices.copy()
    df_prices_to_load['company_id'] = df_prices_to_load['company_id'].apply(normalize_ticker)
    df_prices_to_load = df_prices_to_load[df_prices_to_load['company_id'].isin(companies_ids)]
    df_prices_to_load['open'] = df_prices_to_load['open_price']
    df_prices_to_load['high'] = df_prices_to_load['high_price']
    df_prices_to_load['low'] = df_prices_to_load['low_price']
    df_prices_to_load['close'] = df_prices_to_load['close_price']
    df_prices_to_load = df_prices_to_load.drop_duplicates(subset=['company_id', 'date'], keep='last')
    db.load_dataframe(df_prices_to_load, 'stock_prices')
    
    # Market Cap table
    df_mktcap_to_load = df_mktcap.copy()
    df_mktcap_to_load['company_id'] = df_mktcap_to_load['company_id'].apply(normalize_ticker)
    df_mktcap_to_load = df_mktcap_to_load[df_mktcap_to_load['company_id'].isin(companies_ids)]
    df_mktcap_to_load['market_cap_cr'] = df_mktcap_to_load['market_cap_crore']
    df_mktcap_to_load['dividend_yield'] = df_mktcap_to_load['dividend_yield_pct']
    # Normalize year as string YYYY-MM (defaults to March for annual cap data)
    df_mktcap_to_load['year'] = df_mktcap_to_load['year'].apply(lambda y: f"{y}-03" if '-' not in str(y) else y)
    df_mktcap_to_load = df_mktcap_to_load.drop_duplicates(subset=['company_id', 'year'], keep='last')
    db.load_dataframe(df_mktcap_to_load, 'market_cap')
    
    # 7. Close DB connection, export audit log, print summary
    db.export_audit_to_csv('output/load_audit.csv')
    db.print_summary()
    db.close()


def get_loader(db_path: str = './data/nifty100.db', schema_path: str = './src/db/schema.sql') -> DatabaseLoader:
    """Factory function to create a DatabaseLoader instance"""
    return DatabaseLoader(db_path=db_path, schema_path=schema_path)


if __name__ == '__main__':
    run_etl_load()
