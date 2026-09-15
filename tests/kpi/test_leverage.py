"""
Unit Tests for Leverage and Efficiency Ratios (D/E, ICR, Asset Turnover, Book Value Per Share)
"""

import pytest
from src.analytics.ratios import (
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_asset_turnover,
    calculate_book_value_per_share
)

def test_calculate_debt_to_equity():
    """Test Debt-to-Equity calculations, including debt-free and negative equity"""
    # Normal case
    assert calculate_debt_to_equity(50.0, 50.0, 50.0) == 0.5  # borrowings=50, equity=100
    # Debt-free case (borrowings = 0)
    assert calculate_debt_to_equity(0.0, 50.0, 50.0) == 0.0
    # Total equity = 0
    assert calculate_debt_to_equity(50.0, 50.0, -50.0) is None
    # Total equity < 0
    assert calculate_debt_to_equity(50.0, 50.0, -60.0) is None
    # Missing inputs
    assert calculate_debt_to_equity(None, 50.0, 50.0) is None
    assert calculate_debt_to_equity(50.0, None, 50.0) is None

def test_calculate_interest_coverage():
    """Test Interest Coverage Ratio, including interest = 0 (Debt Free)"""
    # Normal case
    assert calculate_interest_coverage(20.0, 5.0, 5.0) == 5.0
    # Interest = 0 (debt free)
    assert calculate_interest_coverage(20.0, 5.0, 0.0) is None
    # Negative interest
    assert calculate_interest_coverage(20.0, 5.0, -2.0) is None
    # Missing interest
    assert calculate_interest_coverage(20.0, 5.0, None) is None
    # Handle missing operating profit or other income (defaults to 0.0)
    assert calculate_interest_coverage(None, 5.0, 5.0) == 1.0  # (0 + 5) / 5
    assert calculate_interest_coverage(20.0, None, 5.0) == 4.0  # (20 + 0) / 5

def test_calculate_asset_turnover():
    """Test Asset Turnover calculations"""
    # Normal case
    assert calculate_asset_turnover(100.0, 50.0) == 2.0
    # Assets = 0 or negative
    assert calculate_asset_turnover(100.0, 0.0) is None
    assert calculate_asset_turnover(100.0, -10.0) is None
    # Missing inputs
    assert calculate_asset_turnover(None, 50.0) is None
    assert calculate_asset_turnover(100.0, None) is None

def test_calculate_book_value_per_share():
    """Test Book Value Per Share calculations"""
    # Normal case (ABB 2012-12: eq_cap=21, reserves=626, face=10)
    # total_eq = 647. Computed = (647 / 21) * (10 / 100) = 3.08095 -> rounds to 3.081
    assert calculate_book_value_per_share(21.0, 626.0, 10.0) == 3.081
    # Eq_cap <= 0
    assert calculate_book_value_per_share(0.0, 100.0, 10.0) is None
    assert calculate_book_value_per_share(-1.0, 100.0, 10.0) is None
    # Missing inputs
    assert calculate_book_value_per_share(21.0, None, 10.0) is None
    assert calculate_book_value_per_share(21.0, 626.0, None) is None
