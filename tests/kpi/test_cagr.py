"""
Unit Tests for CAGR Growth Calculations and Multi-Year Averages
"""

import pytest
from src.analytics.cagr import (
    calculate_cagr,
    calculate_cagr_for_company,
    calculate_average_metric
)

def test_calculate_cagr_normal():
    """Test CAGR under normal positive conditions"""
    # 3-year growth from 100 to 133.1 -> CAGR = 10%
    cagr, turnaround = calculate_cagr(100.0, 133.1, 3)
    assert cagr == 10.0
    assert turnaround is False
    
    # 5-year growth from 100 to 200 -> CAGR = 14.8698%
    cagr, turnaround = calculate_cagr(100.0, 200.0, 5)
    assert cagr == 14.8698
    assert turnaround is False

def test_calculate_cagr_turnaround_and_negative():
    """Test CAGR when base value is negative (turnaround scenario) or end is negative"""
    # Turnaround (base < 0, end > 0)
    cagr, turnaround = calculate_cagr(-50.0, 100.0, 3)
    assert cagr is None
    assert turnaround is True
    
    # Base < 0, End < 0 (not a turnaround, but base is negative)
    cagr, turnaround = calculate_cagr(-50.0, -100.0, 3)
    assert cagr is None
    assert turnaround is False
    
    # Base > 0, End < 0 (end value is negative)
    cagr, turnaround = calculate_cagr(100.0, -20.0, 3)
    assert cagr is None
    assert turnaround is False
    
    # Base = 0
    cagr, turnaround = calculate_cagr(0.0, 100.0, 3)
    assert cagr is None
    assert turnaround is False

def test_calculate_cagr_for_company():
    """Test CAGR calculation for a company over historical dict data"""
    years_data = {
        "2021-03": 100.0,
        "2022-03": 110.0,
        "2023-03": 121.0,
        "2024-03": 133.1
    }
    
    # 3-year CAGR ending at 2024-03
    cagr, turnaround = calculate_cagr_for_company(years_data, "2024-03", 3, "TCS", "Revenue")
    assert cagr == 10.0
    assert turnaround is False
    
    # Missing base year (2019-03 is not in dict for 5yr CAGR)
    cagr, turnaround = calculate_cagr_for_company(years_data, "2024-03", 5, "TCS", "Revenue")
    assert cagr is None
    assert turnaround is False

def test_calculate_average_metric():
    """Test multi-year average returns calculation"""
    years_data = {
        "2020-03": 10.0,
        "2021-03": 20.0,
        "2022-03": 30.0,
        "2023-03": 40.0,
        "2024-03": 50.0
    }
    
    # 5-year average ending at 2024-03
    avg = calculate_average_metric(years_data, "2024-03", 5)
    assert avg == 30.0  # (10+20+30+40+50) / 5
    
    # Missing year in history
    years_data_missing = {
        "2020-03": 10.0,
        "2021-03": 20.0,
        # missing 2022-03
        "2023-03": 40.0,
        "2024-03": 50.0
    }
    avg_missing = calculate_average_metric(years_data_missing, "2024-03", 5)
    assert avg_missing is None
