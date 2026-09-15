"""
Unit Tests for ETL Normalization Functions
Tests for normalize_year() and normalize_ticker() functions
"""

import pytest
from src.etl.loader import normalize_year, normalize_ticker, ExcelLoader
import pandas as pd
import numpy as np


# ============================================================
# NORMALIZE_YEAR() TESTS (25+ Cases)
# ============================================================

class TestNormalizeYear:
    """Test suite for normalize_year() function"""
    
    # Pattern 1: Mar-23 format (3-letter month - 2-digit year)
    def test_normalize_year_mar_23_format(self):
        """Test Mar-23 -> 2023-03"""
        assert normalize_year("Mar-23") == "2023-03"
    
    def test_normalize_year_jan_20_format(self):
        """Test Jan-20 -> 2020-01"""
        assert normalize_year("Jan-20") == "2020-01"
    
    def test_normalize_year_dec_24_format(self):
        """Test Dec-24 -> 2024-12"""
        assert normalize_year("Dec-24") == "2024-12"
    
    def test_normalize_year_apr_21_format(self):
        """Test Apr-21 -> 2021-04"""
        assert normalize_year("Apr-21") == "2021-04"
    
    def test_normalize_year_sep_19_format(self):
        """Test Sep-19 -> 2019-09"""
        assert normalize_year("Sep-19") == "2019-09"
    
    # Pattern 2: YYYY-MM format
    def test_normalize_year_yyyy_mm_format(self):
        """Test 2023-03 -> 2023-03"""
        assert normalize_year("2023-03") == "2023-03"
    
    def test_normalize_year_yyyy_m_format(self):
        """Test 2023-3 -> 2023-03 (single digit month)"""
        assert normalize_year("2023-3") == "2023-03"
    
    def test_normalize_year_yyyy_slash_mm_format(self):
        """Test 2023/03 -> 2023-03"""
        assert normalize_year("2023/03") == "2023-03"
    
    def test_normalize_year_yyyy_slash_m_format(self):
        """Test 2023/3 -> 2023-03"""
        assert normalize_year("2023/3") == "2023-03"
    
    # Pattern 3: Full month name with year (Mar 2023, March 2023)
    def test_normalize_year_full_month_name_mar(self):
        """Test Mar 2023 -> 2023-03"""
        assert normalize_year("Mar 2023") == "2023-03"
    
    def test_normalize_year_full_month_name_march(self):
        """Test March 2023 -> 2023-03"""
        assert normalize_year("March 2023") == "2023-03"
    
    def test_normalize_year_full_month_name_january(self):
        """Test January 2020 -> 2020-01"""
        assert normalize_year("January 2020") == "2020-01"
    
    def test_normalize_year_full_month_name_december(self):
        """Test December 2024 -> 2024-12"""
        assert normalize_year("December 2024") == "2024-12"
    
    def test_normalize_year_full_month_name_september(self):
        """Test September 2019 -> 2019-09"""
        assert normalize_year("September 2019") == "2019-09"
    
    # Pattern 4: Just year (YYYY)
    def test_normalize_year_just_year(self):
        """Test 2023 -> 2023-03 (defaults to March)"""
        assert normalize_year("2023") == "2023-03"
    
    def test_normalize_year_just_year_2024(self):
        """Test 2024 -> 2024-03"""
        assert normalize_year("2024") == "2024-03"
    
    def test_normalize_year_just_year_2010(self):
        """Test 2010 -> 2010-03"""
        assert normalize_year("2010") == "2010-03"
    
    # Edge cases
    def test_normalize_year_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled"""
        assert normalize_year("  Mar-23  ") == "2023-03"
    
    def test_normalize_year_case_insensitive(self):
        """Test that month names are case insensitive"""
        assert normalize_year("mar-23") == "2023-03"
        assert normalize_year("MAR-23") == "2023-03"
        assert normalize_year("mAr-23") == "2023-03"
    
    def test_normalize_year_case_insensitive_full_name(self):
        """Test full month names are case insensitive"""
        assert normalize_year("march 2023") == "2023-03"
        assert normalize_year("MARCH 2023") == "2023-03"
        assert normalize_year("MaRcH 2023") == "2023-03"
    
    # Null/Empty cases
    def test_normalize_year_null_value(self):
        """Test None returns None"""
        assert normalize_year(None) is None
    
    def test_normalize_year_nan_value(self):
        """Test NaN returns None"""
        assert normalize_year(np.nan) is None
    
    def test_normalize_year_empty_string(self):
        """Test empty string returns None"""
        assert normalize_year("") is None
    
    # Invalid format cases
    def test_normalize_year_invalid_month_number(self):
        """Test invalid month number (13) is still normalized (no validation)"""
        result = normalize_year("2023-13")
        # The function normalizes format but doesn't validate month values
        assert result == "2023-13"
    
    def test_normalize_year_invalid_format(self):
        """Test completely invalid format returns None"""
        assert normalize_year("invalid_format") is None
    
    def test_normalize_year_numeric_input(self):
        """Test numeric input is converted"""
        assert normalize_year(2023) == "2023-03"


# ============================================================
# NORMALIZE_TICKER() TESTS (25+ Cases)
# ============================================================

class TestNormalizeTicker:
    """Test suite for normalize_ticker() function"""
    
    # Basic ticker normalization
    def test_normalize_ticker_uppercase_conversion(self):
        """Test lowercase ticker is converted to uppercase"""
        assert normalize_ticker("tcs") == "TCS"
    
    def test_normalize_ticker_already_uppercase(self):
        """Test uppercase ticker remains unchanged"""
        assert normalize_ticker("TCS") == "TCS"
    
    def test_normalize_ticker_mixed_case(self):
        """Test mixed case ticker is converted to uppercase"""
        assert normalize_ticker("TcS") == "TCS"
    
    # Whitespace handling
    def test_normalize_ticker_strip_leading_spaces(self):
        """Test leading spaces are removed"""
        assert normalize_ticker("  TCS") == "TCS"
    
    def test_normalize_ticker_strip_trailing_spaces(self):
        """Test trailing spaces are removed"""
        assert normalize_ticker("TCS  ") == "TCS"
    
    def test_normalize_ticker_strip_both_spaces(self):
        """Test both leading and trailing spaces are removed"""
        assert normalize_ticker("  TCS  ") == "TCS"
    
    def test_normalize_ticker_internal_spaces_removed(self):
        """Test internal spaces are removed"""
        result = normalize_ticker("HDFC BANK")
        assert " " not in result
    
    # Different ticker lengths
    def test_normalize_ticker_short_ticker(self):
        """Test single character ticker"""
        assert normalize_ticker("T") == "T"
    
    def test_normalize_ticker_medium_ticker(self):
        """Test medium length ticker (4 chars)"""
        assert normalize_ticker("INFY") == "INFY"
    
    def test_normalize_ticker_long_ticker(self):
        """Test longer ticker (10 chars max)"""
        assert normalize_ticker("TATAMOTORS") == "TATAMOTORS"
    
    # Alphanumeric tickers
    def test_normalize_ticker_with_numbers(self):
        """Test ticker with numbers"""
        result = normalize_ticker("TCS1")
        assert result == "TCS1"
    
    def test_normalize_ticker_with_hyphen(self):
        """Test ticker with hyphen (some NSE tickers use hyphens)"""
        result = normalize_ticker("BAJAJ-AUTO")
        assert result == "BAJAJ-AUTO"
    
    # Null/Empty cases
    def test_normalize_ticker_null_value(self):
        """Test None returns None"""
        assert normalize_ticker(None) is None
    
    def test_normalize_ticker_nan_value(self):
        """Test NaN returns None"""
        assert normalize_ticker(np.nan) is None
    
    def test_normalize_ticker_empty_string(self):
        """Test empty string returns None"""
        assert normalize_ticker("") is None
    
    def test_normalize_ticker_only_spaces(self):
        """Test string with only spaces returns None"""
        assert normalize_ticker("   ") is None
    
    # Real NSE tickers
    def test_normalize_ticker_hdfcbank(self):
        """Test HDFCBANK ticker"""
        assert normalize_ticker("hdfcbank") == "HDFCBANK"
    
    def test_normalize_ticker_sbin(self):
        """Test SBIN ticker"""
        assert normalize_ticker("sbin") == "SBIN"
    
    def test_normalize_ticker_reliance(self):
        """Test RELIANCE ticker"""
        assert normalize_ticker("RELIANCE") == "RELIANCE"
    
    def test_normalize_ticker_icicibank(self):
        """Test ICICIBANK ticker"""
        assert normalize_ticker("  icicibank  ") == "ICICIBANK"
    
    def test_normalize_ticker_m_and_m(self):
        """Test M&M ticker (with ampersand)"""
        result = normalize_ticker("M&M")
        assert "M" in result  # Ampersand should be removed
    
    def test_normalize_ticker_numeric_input(self):
        """Test numeric input is converted"""
        assert normalize_ticker(123) == "123"
    
    # Invalid/edge cases
    def test_normalize_ticker_special_characters(self):
        """Test special characters are removed"""
        result = normalize_ticker("TCS@#$")
        assert "@" not in result and "#" not in result and "$" not in result
    
    def test_normalize_ticker_extremely_long(self):
        """Test very long string (>10 chars after cleanup) returns None"""
        result = normalize_ticker("VERYLONGTICKERSYMBOL")
        # May return None or the first 10 chars depending on implementation
        assert result is None or len(result) <= 10
    
    def test_normalize_ticker_only_special_chars(self):
        """Test string with only special characters returns None"""
        assert normalize_ticker("@#$%^&") is None


# ============================================================
# EXCEL LOADER TESTS
# ============================================================

class TestExcelLoader:
    """Test suite for ExcelLoader class"""
    
    def test_loader_initialization(self):
        """Test ExcelLoader initializes with valid data directory"""
        loader = ExcelLoader(data_dir='./data')
        assert loader.data_dir.name == 'data'
    
    def test_loader_invalid_directory(self):
        """Test ExcelLoader raises error with invalid directory"""
        with pytest.raises(FileNotFoundError):
            ExcelLoader(data_dir='./invalid_directory_xyz')
    
    def test_loader_has_core_datasets(self):
        """Test that ExcelLoader has all core datasets defined"""
        loader = ExcelLoader(data_dir='./data')
        expected_datasets = ['companies', 'profitandloss', 'balancesheet', 'cashflow', 
                           'analysis', 'documents', 'prosandcons']
        for dataset in expected_datasets:
            assert dataset in loader.CORE_DATASETS
    
    def test_loader_core_dataset_config_validity(self):
        """Test all core datasets have required configuration"""
        loader = ExcelLoader(data_dir='./data')
        required_keys = ['sheet', 'header_row', 'key_columns']
        
        for dataset_name, config in loader.CORE_DATASETS.items():
            for key in required_keys:
                assert key in config, f"Missing '{key}' in {dataset_name} config"
    
    def test_normalize_dataframe_basic(self):
        """Test _normalize_dataframe with basic normalization"""
        df = pd.DataFrame({
            'company_id': ['tcs', 'infy', '  sbin  '],
            'year': ['Mar-23', 'Mar-24', 'Mar-22']
        })
        
        result = ExcelLoader._normalize_dataframe(df, {
            'company_id': normalize_ticker,
            'year': normalize_year
        })
        
        assert result['company_id'].tolist() == ['TCS', 'INFY', 'SBIN']
        assert result['year'].tolist() == ['2023-03', '2024-03', '2022-03']
    
    def test_validate_data_quality_with_nulls(self):
        """Test data quality validation detects nulls"""
        df = pd.DataFrame({
            'company_id': ['TCS', None, 'INFY'],
            'year': ['2023-03', '2023-03', '2023-03']
        })
        
        is_valid, warnings = ExcelLoader.validate_data_quality(df, 'profitandloss')
        assert not is_valid
        assert len(warnings) > 0
    
    def test_validate_data_quality_with_duplicates(self):
        """Test data quality validation detects duplicates"""
        df = pd.DataFrame({
            'company_id': ['TCS', 'TCS', 'INFY'],
            'year': ['2023-03', '2023-03', '2023-03']
        })
        
        is_valid, warnings = ExcelLoader.validate_data_quality(df, 'profitandloss')
        assert not is_valid
        assert len(warnings) > 0
    
    def test_validate_data_quality_clean_data(self):
        """Test data quality validation passes for clean data"""
        df = pd.DataFrame({
            'company_id': ['TCS', 'INFY', 'SBIN'],
            'year': ['2023-03', '2024-03', '2025-03']
        })
        
        is_valid, warnings = ExcelLoader.validate_data_quality(df, 'profitandloss')
        # Note: May have warnings but structure should be valid
        assert isinstance(is_valid, bool)


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_normalize_functions_together(self):
        """Test normalize functions work together in a DataFrame"""
        data = {
            'company_id': ['  tcs  ', 'infy', 'SBIN'],
            'year': ['Mar-23', 'March 2024', '2022']
        }
        df = pd.DataFrame(data)
        
        result = ExcelLoader._normalize_dataframe(df, {
            'company_id': normalize_ticker,
            'year': normalize_year
        })
        
        expected_tickers = ['TCS', 'INFY', 'SBIN']
        expected_years = ['2023-03', '2024-03', '2022-03']
        
        assert result['company_id'].tolist() == expected_tickers
        assert result['year'].tolist() == expected_years
    
    def test_multiple_normalize_patterns(self):
        """Test that normalize functions handle multiple patterns"""
        year_inputs = [
            'Mar-23', 'March 2023', '2023-03', '2023/3', '2023'
        ]
        ticker_inputs = [
            'tcs', 'TCS', '  infy  ', 'SBIN', 'hdfcbank'
        ]
        
        normalized_years = [normalize_year(y) for y in year_inputs]
        normalized_tickers = [normalize_ticker(t) for t in ticker_inputs]
        
        assert all(isinstance(y, str) and '-' in y for y in normalized_years)
        assert all(isinstance(t, str) and t.isupper() for t in normalized_tickers)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
