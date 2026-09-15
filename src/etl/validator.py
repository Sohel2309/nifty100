"""
Data Quality Validator Module for Nifty 100 ETL Pipeline
Implements the 16 DQ rules from project.md Section 10
"""

import pandas as pd
import numpy as np
import logging
import re
import requests
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from src.etl.loader import ExcelLoader, normalize_year, normalize_ticker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# SEVERITY DEFINITIONS
# ============================================================

class Severity:
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationFailure:
    """Represents a single DQ validation failure, matching AC-19 requirements"""
    company_id: str
    dataset: str
    field: str
    issue: str
    severity: str
    value: str
    details: str
    timestamp: str = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'company_id': self.company_id,
            'dataset': self.dataset,
            'field': self.field,
            'issue': self.issue,
            'severity': self.severity,
            'value': self.value,
            'details': self.details,
            'timestamp': self.timestamp
        }


# ============================================================
# SCHEMA VALIDATOR CLASS
# ============================================================

class SchemaValidator:
    """Orchestrates the 16 Data Quality rules on the Nifty 100 datasets"""
    
    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.failures: List[ValidationFailure] = []
        self.financial_tickers = set()
        self._load_financial_sectors()
        
    def _load_financial_sectors(self):
        """Pre-load sector mapping to identify financial companies (Banks/NBFCs) for DQ-06"""
        try:
            sectors_path = self.data_dir / "supporting datasets" / "sectors.xlsx"
            if sectors_path.exists():
                df_sec = pd.read_excel(sectors_path)
                # Ticker column in sectors.xlsx is 'company_id' or 'id'
                ticker_col = 'company_id' if 'company_id' in df_sec.columns else 'id'
                
                # Check for broad_sector column
                sec_col = 'broad_sector' if 'broad_sector' in df_sec.columns else 'Broad Sector'
                if ticker_col in df_sec.columns and sec_col in df_sec.columns:
                    financial_df = df_sec[df_sec[sec_col].astype(str).str.lower().str.contains('financial')]
                    self.financial_tickers = set(financial_df[ticker_col].dropna().apply(normalize_ticker).unique())
                    logger.info(f"Loaded {len(self.financial_tickers)} financial companies from sectors.xlsx")
            else:
                logger.warning("sectors.xlsx not found, sector-specific validation will fall back to name matching")
        except Exception as e:
            logger.error(f"Error loading sectors.xlsx for financial check: {str(e)}")

    def is_financial(self, company_id: str, company_name: Optional[str] = None) -> bool:
        """Check if a company is a Bank/NBFC/Financials"""
        if company_id in self.financial_tickers:
            return True
        if company_name:
            name_lower = str(company_name).lower()
            if any(keyword in name_lower for keyword in ['bank', 'insurance', 'finance', 'nbfc', 'ltd &']):
                return True
        return False

    def validate_all(self, dfs: Dict[str, pd.DataFrame]) -> List[ValidationFailure]:
        """Run all 16 DQ rules on the loaded datasets"""
        self.failures = []
        
        # Ensure we have companies master list for foreign key checks
        df_companies = dfs.get('companies')
        companies_ids = set()
        if df_companies is not None and 'id' in df_companies.columns:
            companies_ids = set(df_companies['id'].dropna().unique())

        # --------------------------------------------------------
        # DQ-01: Company PK Uniqueness
        # --------------------------------------------------------
        if df_companies is not None:
            if 'id' in df_companies.columns:
                dups = df_companies[df_companies.duplicated(subset=['id'], keep=False)]
                if len(dups) > 0:
                    for ticker in dups['id'].unique():
                        self.failures.append(ValidationFailure(
                            company_id=str(ticker),
                            dataset='companies',
                            field='id',
                            issue='DQ-01: Company PK Uniqueness Violation',
                            severity=Severity.CRITICAL,
                            value=str(ticker),
                            details=f"Ticker '{ticker}' is duplicated in companies.xlsx"
                        ))
            else:
                self.failures.append(ValidationFailure(
                    company_id='ALL',
                    dataset='companies',
                    field='id',
                    issue='DQ-01: Missing PK column',
                    severity=Severity.CRITICAL,
                    value='id',
                    details="companies sheet is missing the 'id' column"
                ))

        # --------------------------------------------------------
        # DQ-02: Annual PK Uniqueness
        # --------------------------------------------------------
        for name in ['profitandloss', 'balancesheet', 'cashflow']:
            df = dfs.get(name)
            if df is not None:
                if 'company_id' in df.columns and 'year' in df.columns:
                    dups = df[df.duplicated(subset=['company_id', 'year'], keep=False)]
                    if len(dups) > 0:
                        for _, row in dups.iterrows():
                            self.failures.append(ValidationFailure(
                                company_id=str(row['company_id']),
                                dataset=name,
                                field='company_id,year',
                                issue='DQ-02: Annual PK Uniqueness Violation',
                                severity=Severity.CRITICAL,
                                value=f"{row['company_id']}_{row['year']}",
                                details=f"Duplicate year records for company in {name}"
                            ))

        # --------------------------------------------------------
        # DQ-03: FK Integrity
        # --------------------------------------------------------
        child_tables = ['profitandloss', 'balancesheet', 'cashflow', 'analysis', 'documents', 'prosandcons', 'sectors', 'stock_prices', 'market_cap', 'financial_ratios', 'peer_groups']
        for name in child_tables:
            df = dfs.get(name)
            if df is not None and 'company_id' in df.columns:
                orphans = df[~df['company_id'].isin(companies_ids)]
                if len(orphans) > 0:
                    for _, row in orphans.iterrows():
                        self.failures.append(ValidationFailure(
                            company_id=str(row['company_id']),
                            dataset=name,
                            field='company_id',
                            issue='DQ-03: FK Integrity Violation',
                            severity=Severity.CRITICAL,
                            value=str(row['company_id']),
                            details=f"Company ID '{row['company_id']}' in {name} does not exist in companies master sheet"
                        ))

        # --------------------------------------------------------
        # DQ-04: Balance Sheet Balance
        # --------------------------------------------------------
        df_bs = dfs.get('balancesheet')
        if df_bs is not None:
            required_cols = ['company_id', 'year', 'total_assets', 'total_liabilities']
            if all(c in df_bs.columns for c in required_cols):
                for idx, row in df_bs.iterrows():
                    assets = float(row['total_assets']) if not pd.isna(row['total_assets']) else 0.0
                    liabs = float(row['total_liabilities']) if not pd.isna(row['total_liabilities']) else 0.0
                    if assets != 0.0:
                        diff_pct = abs(assets - liabs) / assets
                        if diff_pct >= 0.01:
                            self.failures.append(ValidationFailure(
                                company_id=str(row['company_id']),
                                dataset='balancesheet',
                                field='total_assets/total_liabilities',
                                issue='DQ-04: Balance Sheet Balance Violation',
                                severity=Severity.WARNING,
                                value=f"Assets: {assets}, Liabs: {liabs}",
                                details=f"Balance sheet out of balance by {diff_pct*100:.2f}% (tolerance is <1%) at index {idx}"
                            ))

        # --------------------------------------------------------
        # DQ-05: OPM Cross-Check
        # --------------------------------------------------------
        df_pl = dfs.get('profitandloss')
        if df_pl is not None:
            required_cols = ['company_id', 'year', 'sales', 'operating_profit', 'opm_percentage']
            if all(c in df_pl.columns for c in required_cols):
                for idx, row in df_pl.iterrows():
                    sales = float(row['sales']) if not pd.isna(row['sales']) else 0.0
                    op = float(row['operating_profit']) if not pd.isna(row['operating_profit']) else 0.0
                    opm = float(row['opm_percentage']) if not pd.isna(row['opm_percentage']) else 0.0
                    if sales > 0:
                        computed_opm = (op / sales) * 100
                        if abs(opm - computed_opm) >= 1.0:
                            self.failures.append(ValidationFailure(
                                company_id=str(row['company_id']),
                                dataset='profitandloss',
                                field='opm_percentage',
                                issue='DQ-05: OPM Cross-Check Violation',
                                severity=Severity.WARNING,
                                value=f"Reported OPM: {opm}%, Computed OPM: {computed_opm:.2f}%",
                                details=f"OPM mismatch >= 1% at index {idx}"
                            ))

        # --------------------------------------------------------
        # DQ-06: Positive Sales (Non-Bank Companies)
        # --------------------------------------------------------
        if df_pl is not None:
            required_cols = ['company_id', 'year', 'sales']
            if all(c in df_pl.columns for c in required_cols):
                for idx, row in df_pl.iterrows():
                    ticker = str(row['company_id'])
                    sales = float(row['sales']) if not pd.isna(row['sales']) else 0.0
                    
                    # Fetch company name from master if available for fallback check
                    co_name = None
                    if df_companies is not None and 'company_name' in df_companies.columns:
                        co_row = df_companies[df_companies['id'] == ticker]
                        if len(co_row) > 0:
                            co_name = co_row.iloc[0]['company_name']
                            
                    if not self.is_financial(ticker, co_name):
                        if sales <= 0:
                            self.failures.append(ValidationFailure(
                                company_id=ticker,
                                dataset='profitandloss',
                                field='sales',
                                issue='DQ-06: Non-Positive Sales Violation',
                                severity=Severity.WARNING,
                                value=str(sales),
                                details=f"Non-bank company '{ticker}' has sales <= 0 (sales: {sales}) in year {row['year']}"
                            ))

        # --------------------------------------------------------
        # DQ-07: Year Format
        # --------------------------------------------------------
        year_pattern = r'^\d{4}-\d{2}$'
        for name in ['profitandloss', 'balancesheet', 'cashflow', 'documents', 'financial_ratios']:
            df = dfs.get(name)
            if df is not None:
                # In documents table in Excel, column is named 'Year' or 'year'
                year_col = 'Year' if 'Year' in df.columns else 'year'
                if year_col in df.columns:
                    for idx, row in df.iterrows():
                        year_val = row[year_col]
                        if pd.isna(year_val):
                            continue
                        normalized = normalize_year(year_val)
                        if not normalized or not re.match(year_pattern, normalized):
                            ticker = str(row['company_id']) if 'company_id' in row else 'UNKNOWN'
                            self.failures.append(ValidationFailure(
                                company_id=ticker,
                                dataset=name,
                                field=year_col,
                                issue='DQ-07: Year Format Violation',
                                severity=Severity.CRITICAL,
                                value=str(year_val),
                                details=f"Year value '{year_val}' could not be normalized to YYYY-MM"
                            ))

        # --------------------------------------------------------
        # DQ-08: Ticker Format
        # --------------------------------------------------------
        for name, df in dfs.items():
            ticker_col = 'id' if name == 'companies' else 'company_id'
            if df is not None and ticker_col in df.columns:
                for idx, row in df.iterrows():
                    ticker_val = row[ticker_col]
                    if pd.isna(ticker_val):
                        continue
                    normalized = normalize_ticker(ticker_val)
                    if not normalized or len(normalized) < 2 or len(normalized) > 12:
                        self.failures.append(ValidationFailure(
                            company_id=str(ticker_val),
                            dataset=name,
                            field=ticker_col,
                            issue='DQ-08: Ticker Format Violation',
                            severity=Severity.CRITICAL,
                            value=str(ticker_val),
                            details=f"Ticker '{ticker_val}' is invalid (length must be 2-12 chars)"
                        ))

        # --------------------------------------------------------
        # DQ-09: Net Cash Check
        # --------------------------------------------------------
        df_cf = dfs.get('cashflow')
        if df_cf is not None:
            required_cols = ['company_id', 'year', 'operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']
            if all(c in df_cf.columns for c in required_cols):
                for idx, row in df_cf.iterrows():
                    cfo = float(row['operating_activity']) if not pd.isna(row['operating_activity']) else 0.0
                    cfi = float(row['investing_activity']) if not pd.isna(row['investing_activity']) else 0.0
                    cff = float(row['financing_activity']) if not pd.isna(row['financing_activity']) else 0.0
                    ncf = float(row['net_cash_flow']) if not pd.isna(row['net_cash_flow']) else 0.0
                    expected_ncf = cfo + cfi + cff
                    if abs(ncf - expected_ncf) > 10.0:
                        self.failures.append(ValidationFailure(
                            company_id=str(row['company_id']),
                            dataset='cashflow',
                            field='net_cash_flow',
                            issue='DQ-09: Net Cash Flow Consistency Violation',
                            severity=Severity.WARNING,
                            value=f"Reported NCF: {ncf}, CFO+CFI+CFF: {expected_ncf}",
                            details=f"Net Cash Flow mismatch > 10 Cr at index {idx}"
                        ))

        # --------------------------------------------------------
        # DQ-10: Non-Negative Fixed Assets
        # --------------------------------------------------------
        if df_bs is not None and 'fixed_assets' in df_bs.columns:
            for idx, row in df_bs.iterrows():
                fa = float(row['fixed_assets']) if not pd.isna(row['fixed_assets']) else 0.0
                if fa < 0:
                    self.failures.append(ValidationFailure(
                        company_id=str(row['company_id']),
                        dataset='balancesheet',
                        field='fixed_assets',
                        issue='DQ-10: Negative Fixed Assets Violation',
                        severity=Severity.WARNING,
                        value=str(fa),
                        details=f"Negative fixed assets coerced to 0 at index {idx}"
                    ))

        # --------------------------------------------------------
        # DQ-11: Tax Rate Range
        # --------------------------------------------------------
        if df_pl is not None and 'tax_percentage' in df_pl.columns:
            for idx, row in df_pl.iterrows():
                tax_pct = float(row['tax_percentage']) if not pd.isna(row['tax_percentage']) else 0.0
                if tax_pct < 0 or tax_pct > 60:
                    self.failures.append(ValidationFailure(
                        company_id=str(row['company_id']),
                        dataset='profitandloss',
                        field='tax_percentage',
                        issue='DQ-11: Tax Rate Out of Range',
                        severity=Severity.WARNING,
                        value=str(tax_pct),
                        details=f"Tax percentage {tax_pct}% is outside [0, 60] range at index {idx}"
                    ))

        # --------------------------------------------------------
        # DQ-12: Dividend Payout Cap
        # --------------------------------------------------------
        if df_pl is not None and 'dividend_payout' in df_pl.columns:
            for idx, row in df_pl.iterrows():
                div_payout = float(row['dividend_payout']) if not pd.isna(row['dividend_payout']) else 0.0
                if div_payout > 200:
                    self.failures.append(ValidationFailure(
                        company_id=str(row['company_id']),
                        dataset='profitandloss',
                        field='dividend_payout',
                        issue='DQ-12: Dividend Payout Exceeds Cap',
                        severity=Severity.WARNING,
                        value=str(div_payout),
                        details=f"Dividend payout {div_payout}% exceeds 200% at index {idx}"
                    ))

        # --------------------------------------------------------
        # DQ-13: URL Validity (documents)
        # --------------------------------------------------------
        df_docs = dfs.get('documents')
        if df_docs is not None and 'Annual_Report' in df_docs.columns:
            # Check a random sample of 10 rows to avoid slowing down pipeline
            valid_urls = df_docs['Annual_Report'].dropna().tolist()
            sample_size = min(10, len(valid_urls))
            if sample_size > 0:
                sampled_urls = random.sample(valid_urls, sample_size)
                for url in sampled_urls:
                    # Find associated company id
                    ticker = df_docs[df_docs['Annual_Report'] == url]['company_id'].iloc[0]
                    try:
                        # Set a short timeout (1 sec) to keep it fast
                        resp = requests.head(url, timeout=1.0, allow_redirects=True)
                        if resp.status_code != 200:
                            self.failures.append(ValidationFailure(
                                company_id=str(ticker),
                                dataset='documents',
                                field='Annual_Report',
                                issue='DQ-13: URL Validity Violation',
                                severity=Severity.WARNING,
                                value=str(url),
                                details=f"Annual report PDF link returned status {resp.status_code}"
                            ))
                    except Exception as e:
                        self.failures.append(ValidationFailure(
                            company_id=str(ticker),
                            dataset='documents',
                            field='Annual_Report',
                            issue='DQ-13: URL Validity Connection Failure',
                            severity=Severity.WARNING,
                            value=str(url),
                            details=f"Annual report URL check threw exception: {str(e)}"
                        ))

        # --------------------------------------------------------
        # DQ-14: EPS Sign Consistency
        # --------------------------------------------------------
        if df_pl is not None:
            required_cols = ['company_id', 'year', 'net_profit', 'eps']
            if all(c in df_pl.columns for c in required_cols):
                for idx, row in df_pl.iterrows():
                    np_val = float(row['net_profit']) if not pd.isna(row['net_profit']) else 0.0
                    eps_val = float(row['eps']) if not pd.isna(row['eps']) else 0.0
                    if np_val > 0.0 and eps_val <= 0.0:
                        self.failures.append(ValidationFailure(
                            company_id=str(row['company_id']),
                            dataset='profitandloss',
                            field='eps',
                            issue='DQ-14: EPS Sign Consistency Violation',
                            severity=Severity.WARNING,
                            value=f"Net Profit: {np_val}, EPS: {eps_val}",
                            details=f"Positive net profit but non-positive EPS at index {idx}"
                        ))

        # --------------------------------------------------------
        # DQ-15: BSE/ASE Balance (ext.)
        # --------------------------------------------------------
        if df_bs is not None:
            required_cols = ['company_id', 'year', 'total_assets', 'total_liabilities']
            if all(c in df_bs.columns for c in required_cols):
                for idx, row in df_bs.iterrows():
                    assets = float(row['total_assets']) if not pd.isna(row['total_assets']) else 0.0
                    liabs = float(row['total_liabilities']) if not pd.isna(row['total_liabilities']) else 0.0
                    if assets != liabs:
                        self.failures.append(ValidationFailure(
                            company_id=str(row['company_id']),
                            dataset='balancesheet',
                            field='total_assets/total_liabilities',
                            issue='DQ-15: BSE/ASE Balance Mismatch (Strict)',
                            severity=Severity.INFO,
                            value=f"Assets: {assets}, Liabs: {liabs}",
                            details=f"Assets ({assets}) does not equal Liabilities ({liabs}) strictly at index {idx}"
                        ))

        # --------------------------------------------------------
        # DQ-16: Coverage Check
        # --------------------------------------------------------
        for name in ['profitandloss', 'balancesheet', 'cashflow', 'financial_ratios']:
            df = dfs.get(name)
            if df is not None and 'company_id' in df.columns:
                counts = df['company_id'].value_counts()
                for ticker, count in counts.items():
                    if count < 5:
                        self.failures.append(ValidationFailure(
                            company_id=str(ticker),
                            dataset=name,
                            field='company_id',
                            issue='DQ-16: Insufficient Years Coverage Violation',
                            severity=Severity.WARNING,
                            value=str(count),
                            details=f"Company '{ticker}' has only {count} years of history in {name} (required >=5)"
                        ))

        return self.failures

    def export_failures_to_csv(self, output_path: str = 'output/validation_failures.csv') -> str:
        """Export all validation failures to CSV file matching AC-19 layout"""
        failures_data = [f.to_dict() for f in self.failures]
        df_failures = pd.DataFrame(failures_data)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_failures.to_csv(output_path, index=False)
        logger.info(f"Validation failures exported to: {output_path} ({len(self.failures)} records)")
        return str(output_path)

    def print_report(self):
        """Print a summary report to console"""
        criticals = [f for f in self.failures if f.severity == Severity.CRITICAL]
        warnings = [f for f in self.failures if f.severity == Severity.WARNING]
        infos = [f for f in self.failures if f.severity == Severity.INFO]
        
        print("\n" + "="*80)
        print("DATA QUALITY SCHEMA VALIDATION REPORT")
        print("="*80)
        print(f"Total Violations: {len(self.failures)}")
        print(f"  - CRITICAL (Must fix to load): {len(criticals)}")
        print(f"  - WARNING (Flag and load):    {len(warnings)}")
        print(f"  - INFO (Audit log only):      {len(infos)}")
        print("="*80)
        
        if len(self.failures) > 0:
            print("\nViolations Breakdown by Rule:")
            print("-"*80)
            # Group by issue/rule
            grouped_failures = {}
            for f in self.failures:
                grouped_failures[f.issue] = grouped_failures.get(f.issue, 0) + 1
            for issue, count in grouped_failures.items():
                print(f"  * {issue:45} : {count:4} violations")
                
            print("\nSample of Critical Failures:")
            print("-"*80)
            for f in criticals[:5]:
                print(f"  [{f.severity}] Dataset: {f.dataset} | Co: {f.company_id} | Field: {f.field}")
                print(f"  Details: {f.details} | Value: {f.value}\n")
        else:
            print("\n✓ ALL DATA QUALITY RULES PASSED SUCCESSFULLY!")
        print("="*80 + "\n")


# ============================================================
# MAIN CLI ENTRYPOINT
# ============================================================

if __name__ == '__main__':
    # Initialize ExcelLoader
    loader = ExcelLoader(data_dir='./data')
    
    print("Ingesting all 7 core Excel files...")
    core_datasets = loader.load_all_core_datasets()
    
    print("Initializing SchemaValidator...")
    validator = SchemaValidator(data_dir='./data')
    
    print("Running validation rules...")
    failures = validator.validate_all(core_datasets)
    
    print("Exporting validation failures to validation_failures.csv...")
    validator.export_failures_to_csv('output/validation_failures.csv')
    
    validator.print_report()
