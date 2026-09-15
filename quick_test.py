#!/usr/bin/env python
"""Quick test script for ETL loader functions"""

from src.etl.loader import normalize_year, normalize_ticker, ExcelLoader

print("=" * 60)
print("NIFTY 100 ETL LOADER - QUICK TEST")
print("=" * 60)

# Test normalize_year
print("\n[TEST 1] normalize_year() Function")
print("-" * 60)
test_years = [
    ("Mar-23", "2023-03"),
    ("March 2023", "2023-03"),
    ("2023-03", "2023-03"),
    ("2023", "2023-03"),
    ("  Jan-20  ", "2020-01"),
]
for input_val, expected in test_years:
    result = normalize_year(input_val)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    print(f"{status}: normalize_year('{input_val}') -> {result} (expected: {expected})")

# Test normalize_ticker
print("\n[TEST 2] normalize_ticker() Function")
print("-" * 60)
test_tickers = [
    ("tcs", "TCS"),
    ("  INFY  ", "INFY"),
    ("sbin", "SBIN"),
    ("hdfcbank", "HDFCBANK"),
    ("  TcS  ", "TCS"),
]
for input_val, expected in test_tickers:
    result = normalize_ticker(input_val)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    print(f"{status}: normalize_ticker('{input_val}') -> {result} (expected: {expected})")

# Test ExcelLoader initialization
print("\n[TEST 3] ExcelLoader Initialization")
print("-" * 60)
try:
    loader = ExcelLoader(data_dir='./data')
    print(f"✓ PASS: ExcelLoader initialized successfully")
    print(f"  - Data directory: {loader.data_dir}")
    print(f"  - Core datasets available: {len(loader.CORE_DATASETS)}")
except Exception as e:
    print(f"✗ FAIL: {str(e)}")

print("\n" + "=" * 60)
print("TEST SUMMARY: All basic tests completed!")
print("=" * 60)
