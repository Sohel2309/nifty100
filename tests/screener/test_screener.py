"""
Unit Tests for Stock Screener and Filter Engine
"""

import pytest
import numpy as np
import pandas as pd
from src.analytics.screener.engine import (
    winsorise_and_scale,
    score_de,
    score_icr,
    calculate_composite_scores,
    run_preset_screener
)

def test_winsorise_and_scale():
    """Test winsorisation and min-max scaling of series data"""
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    scaled = winsorise_and_scale(series)
    
    # P10 is 19.0, P90 is 91.0
    assert scaled.iloc[0] == 0.0
    assert scaled.iloc[1] > 0.0
    # Values >= 91.0 should be scaled to 100.0
    assert scaled.iloc[9] == 100.0 # 100.0 becomes 91.0 -> scaled = 100.0

def test_score_de():
    """Test Debt-to-Equity scoring rules"""
    assert score_de(0.0) == 100.0
    assert score_de(-0.5) == 100.0
    assert score_de(0.5) == 85.0
    assert score_de(1.0) == 70.0
    assert score_de(2.0) == 50.0
    assert score_de(5.0) == 0.0
    assert score_de(6.0) == 0.0
    assert score_de(None) == 0.0

def test_score_icr():
    """Test Interest Coverage Ratio scoring rules"""
    assert score_icr(None) == 100.0 # None represents interest=0 -> score = 100
    assert score_icr(1.5) == 0.0
    assert score_icr(3.0) == 50.0
    assert score_icr(5.0) == 75.0
    assert score_icr(10.0) == 100.0
    assert score_icr(12.0) == 100.0

def test_calculate_composite_scores():
    """Test Composite Score calculation logic"""
    # Create mock dataframe with required columns
    df = pd.DataFrame({
        'company_id': ['TCS', 'INFY'],
        'return_on_equity_pct': [25.0, 30.0],
        'operating_profit': [200.0, 180.0],
        'depreciation': [20.0, 15.0],
        'equity_capital': [100.0, 80.0],
        'reserves': [400.0, 320.0],
        'borrowings': [0.0, 10.0],
        'net_profit_margin_pct': [18.0, 16.0],
        'cash_from_operations_cr': [220.0, 190.0],
        'net_profit': [150.0, 130.0],
        'free_cash_flow_cr': [180.0, 160.0],
        'revenue_5yr_cagr': [12.0, 14.0],
        'pat_5yr_cagr': [10.0, 12.0],
        'debt_to_equity': [0.0, 0.025],
        'interest_coverage': [None, 72.0]
    })
    
    scored = calculate_composite_scores(df)
    assert 'composite_score' in scored.columns
    assert scored['composite_score'].iloc[0] > 0.0
    assert scored['composite_score'].iloc[1] > 0.0
