"""
Unit Tests for Profitability Ratios (NPM, OPM, ROE, ROCE)
"""

import pytest
import logging
from src.analytics.ratios import (
    calculate_npm,
    calculate_opm,
    calculate_roe,
    calculate_roce
)

def test_calculate_npm_normal():
    """Test Net Profit Margin under normal positive conditions"""
    assert calculate_npm(15.0, 100.0) == 15.0
    assert calculate_npm(-5.0, 100.0) == -5.0
    assert calculate_npm(0.0, 50.0) == 0.0

def test_calculate_npm_edge_cases():
    """Test Net Profit Margin when sales is zero, negative, or None"""
    assert calculate_npm(15.0, 0.0) is None
    assert calculate_npm(15.0, -10.0) is None
    assert calculate_npm(15.0, None) is None
    assert calculate_npm(None, 100.0) is None

def test_calculate_opm_normal():
    """Test Operating Profit Margin under normal positive conditions"""
    assert calculate_opm(20.0, 100.0) == 20.0
    assert calculate_opm(0.0, 100.0) == 0.0

def test_calculate_opm_edge_cases():
    """Test Operating Profit Margin when sales is zero, negative, or None"""
    assert calculate_opm(20.0, 0.0) is None
    assert calculate_opm(20.0, -10.0) is None
    assert calculate_opm(20.0, None) is None
    assert calculate_opm(None, 100.0) is None

def test_calculate_opm_cross_check_warning(caplog):
    """Test OPM warning log when computed and reported OPM mismatch >= 1.0%"""
    with caplog.at_level(logging.WARNING):
        # Mismatch >= 1.0%
        val = calculate_opm(25.0, 100.0, reported_opm=23.5, company_id="TCS", year="2024-03")
        assert val == 25.0
        assert len(caplog.records) > 0
        assert "OPM Mismatch" in caplog.text
        
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        # Mismatch < 1.0% (no warning)
        val = calculate_opm(25.0, 100.0, reported_opm=24.5, company_id="TCS", year="2024-03")
        assert val == 25.0
        assert len(caplog.records) == 0

def test_calculate_roe_normal():
    """Test Return on Equity under normal positive conditions"""
    assert calculate_roe(20.0, 50.0, 50.0) == 20.0 # equity = 100
    assert calculate_roe(-10.0, 10.0, 40.0) == -20.0 # equity = 50

def test_calculate_roe_edge_cases():
    """Test Return on Equity when total equity is zero, negative, or inputs are None"""
    # Total equity = 0
    assert calculate_roe(20.0, 50.0, -50.0) is None
    # Total equity < 0
    assert calculate_roe(20.0, 50.0, -60.0) is None
    # Missing inputs
    assert calculate_roe(20.0, None, 50.0) is None
    assert calculate_roe(20.0, 50.0, None) is None
    assert calculate_roe(None, 50.0, 50.0) is None

def test_calculate_roce_normal():
    """Test Return on Capital Employed under normal positive conditions"""
    # EBIT = 30 - 5 = 25. CapEmployed = 50 + 50 + 50 = 150. ROCE = 25/150 * 100 = 16.6667
    assert calculate_roce(30.0, 5.0, 50.0, 50.0, 50.0) == 16.6667

def test_calculate_roce_edge_cases():
    """Test Return on Capital Employed under zero/negative capital or missing inputs"""
    # Capital Employed = 0
    assert calculate_roce(30.0, 5.0, 10.0, -20.0, 10.0) is None
    # Capital Employed < 0
    assert calculate_roce(30.0, 5.0, 10.0, -30.0, 10.0) is None
    # Missing inputs
    assert calculate_roce(None, 5.0, 50.0, 50.0, 50.0) is None
    assert calculate_roce(30.0, None, 50.0, 50.0, 50.0) is None
    assert calculate_roce(30.0, 5.0, None, 50.0, 50.0) is None
