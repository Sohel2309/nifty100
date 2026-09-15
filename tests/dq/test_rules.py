"""
Unit Tests for Data Quality Rules (DQ-01 to DQ-16)
Tests the SchemaValidator on synthetic data with specific violations
"""

import pytest
import pandas as pd
import numpy as np
from src.etl.validator import SchemaValidator, Severity, ValidationFailure

@pytest.fixture
def base_validator():
    """Returns a SchemaValidator configured with local path"""
    return SchemaValidator(data_dir='./data')

@pytest.fixture
def mock_companies():
    """Mock companies dataframe"""
    return pd.DataFrame({
        'id': ['TCS', 'INFY', 'SBIN'],
        'company_name': ['Tata Consultancy Services', 'Infosys Ltd', 'State Bank of India']
    })

def test_dq01_company_pk_uniqueness(base_validator):
    """DQ-01: Company PK Uniqueness critical check"""
    df_comp = pd.DataFrame({
        'id': ['TCS', 'TCS', 'INFY'],
        'company_name': ['Tata Consultancy Services', 'TCS Duplicate', 'Infosys Ltd']
    })
    failures = base_validator.validate_all({'companies': df_comp})
    
    dq01_fails = [f for f in failures if 'DQ-01' in f.issue]
    assert len(dq01_fails) > 0
    assert dq01_fails[0].severity == Severity.CRITICAL
    assert dq01_fails[0].company_id == 'TCS'

def test_dq02_annual_pk_uniqueness(base_validator, mock_companies):
    """DQ-02: Annual PK Uniqueness critical check on composite keys"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS', 'TCS', 'INFY'],
        'year': ['2023-03', '2023-03', '2023-03'],
        'sales': [100.0, 110.0, 80.0],
        'expenses': [70.0, 75.0, 60.0],
        'operating_profit': [30.0, 35.0, 20.0],
        'opm_percentage': [30.0, 31.8, 25.0]
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq02_fails = [f for f in failures if 'DQ-02' in f.issue]
    assert len(dq02_fails) > 0
    assert dq02_fails[0].severity == Severity.CRITICAL
    assert 'TCS' in [f.company_id for f in dq02_fails]

def test_dq03_fk_integrity(base_validator, mock_companies):
    """DQ-03: FK Integrity critical check for orphan rows"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS', 'RELIANCE'], # RELIANCE is not in mock_companies
        'year': ['2023-03', '2023-03'],
        'sales': [100.0, 200.0],
        'expenses': [70.0, 150.0],
        'operating_profit': [30.0, 50.0],
        'opm_percentage': [30.0, 25.0]
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq03_fails = [f for f in failures if 'DQ-03' in f.issue]
    assert len(dq03_fails) > 0
    assert dq03_fails[0].severity == Severity.CRITICAL
    assert dq03_fails[0].company_id == 'RELIANCE'

def test_dq04_bs_balance(base_validator, mock_companies):
    """DQ-04: Balance Sheet Balance warning (tolerance < 1%)"""
    # Test case matching specification: assets=1000, liab=1020 -> 2% diff -> DQ-04 warning triggered
    df_bs = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'total_assets': [1000.0],
        'total_liabilities': [1020.0]
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'balancesheet': df_bs
    })
    
    dq04_fails = [f for f in failures if 'DQ-04' in f.issue]
    assert len(dq04_fails) > 0
    assert dq04_fails[0].severity == Severity.WARNING

def test_dq05_opm_cross_check(base_validator, mock_companies):
    """DQ-05: OPM Cross-Check warning (mismatch >= 1%)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'sales': [100.0],
        'operating_profit': [30.0],
        'opm_percentage': [25.0] # Should be 30.0% -> 5% mismatch
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq05_fails = [f for f in failures if 'DQ-05' in f.issue]
    assert len(dq05_fails) > 0
    assert dq05_fails[0].severity == Severity.WARNING

def test_dq06_zero_sales(base_validator, mock_companies):
    """DQ-06: Positive Sales warning (sales <= 0 for non-bank company)"""
    # TCS is non-bank
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'sales': [0.0] # Zero sales
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq06_fails = [f for f in failures if 'DQ-06' in f.issue]
    assert len(dq06_fails) > 0
    assert dq06_fails[0].severity == Severity.WARNING

def test_dq07_year_format(base_validator, mock_companies):
    """DQ-07: Year Format critical check (matches YYYY-MM)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['invalid_year_str'],
        'sales': [100.0],
        'expenses': [70.0]
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq07_fails = [f for f in failures if 'DQ-07' in f.issue]
    assert len(dq07_fails) > 0
    assert dq07_fails[0].severity == Severity.CRITICAL

def test_dq08_ticker_format(base_validator):
    """DQ-08: Ticker Format critical check (length must be 2-12)"""
    df_comp = pd.DataFrame({
        'id': ['A', 'SUPERLONGCCOMPANNYNAME'], # 1 char and 21 chars respectively
        'company_name': ['Company A', 'Company Long']
    })
    
    failures = base_validator.validate_all({'companies': df_comp})
    
    dq08_fails = [f for f in failures if 'DQ-08' in f.issue]
    assert len(dq08_fails) == 2
    assert dq08_fails[0].severity == Severity.CRITICAL

def test_dq09_net_cash_check(base_validator, mock_companies):
    """DQ-09: Net Cash Check warning (CFO+CFI+CFF difference > 10 Cr)"""
    df_cf = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'operating_activity': [100.0],
        'investing_activity': [-50.0],
        'financing_activity': [-30.0],
        'net_cash_flow': [40.0] # Should be 20.0 (100 - 50 - 30) -> mismatch is 20 Cr
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'cashflow': df_cf
    })
    
    dq09_fails = [f for f in failures if 'DQ-09' in f.issue]
    assert len(dq09_fails) > 0
    assert dq09_fails[0].severity == Severity.WARNING

def test_dq10_non_negative_fixed_assets(base_validator, mock_companies):
    """DQ-10: Non-Negative Fixed Assets warning"""
    df_bs = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'total_assets': [500.0],
        'total_liabilities': [500.0],
        'fixed_assets': [-5.0] # Negative fixed assets
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'balancesheet': df_bs
    })
    
    dq10_fails = [f for f in failures if 'DQ-10' in f.issue]
    assert len(dq10_fails) > 0
    assert dq10_fails[0].severity == Severity.WARNING

def test_dq11_tax_rate_range(base_validator, mock_companies):
    """DQ-11: Tax Rate Range warning ([0, 60] range)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'sales': [100.0],
        'tax_percentage': [65.0] # Out of range
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq11_fails = [f for f in failures if 'DQ-11' in f.issue]
    assert len(dq11_fails) > 0
    assert dq11_fails[0].severity == Severity.WARNING

def test_dq12_dividend_payout_cap(base_validator, mock_companies):
    """DQ-12: Dividend Payout Cap warning (<= 200%)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'sales': [100.0],
        'dividend_payout': [250.0] # Exceeds 200
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq12_fails = [f for f in failures if 'DQ-12' in f.issue]
    assert len(dq12_fails) > 0
    assert dq12_fails[0].severity == Severity.WARNING

def test_dq14_eps_sign_consistency(base_validator, mock_companies):
    """DQ-14: EPS Sign Consistency warning (eps > 0 if net_profit > 0)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'sales': [100.0],
        'net_profit': [25.0], # Positive profit
        'eps': [-1.0] # Non-positive EPS
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq14_fails = [f for f in failures if 'DQ-14' in f.issue]
    assert len(dq14_fails) > 0
    assert dq14_fails[0].severity == Severity.WARNING

def test_dq15_strict_balance(base_validator, mock_companies):
    """DQ-15: BSE/ASE Balance (strict equal) check with INFO level"""
    df_bs = pd.DataFrame({
        'company_id': ['TCS'],
        'year': ['2023-03'],
        'total_assets': [500.0],
        'total_liabilities': [500.1] # Mismatch but within 1% (so no DQ-04 warning)
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'balancesheet': df_bs
    })
    
    # Check that it triggered DQ-15 info and NOT DQ-04 warning
    dq15_fails = [f for f in failures if 'DQ-15' in f.issue]
    dq04_fails = [f for f in failures if 'DQ-04' in f.issue]
    
    assert len(dq15_fails) > 0
    assert dq15_fails[0].severity == Severity.INFO
    assert len(dq04_fails) == 0

def test_dq16_coverage_check(base_validator, mock_companies):
    """DQ-16: Coverage Check warning (< 5 years of records)"""
    df_pl = pd.DataFrame({
        'company_id': ['TCS', 'TCS', 'TCS'], # Only 3 years of history
        'year': ['2021-03', '2022-03', '2023-03'],
        'sales': [100.0, 110.0, 120.0]
    })
    
    failures = base_validator.validate_all({
        'companies': mock_companies,
        'profitandloss': df_pl
    })
    
    dq16_fails = [f for f in failures if 'DQ-16' in f.issue]
    assert len(dq16_fails) > 0
    assert dq16_fails[0].severity == Severity.WARNING
    assert dq16_fails[0].company_id == 'TCS'
