"""
Unit Tests for Cash Flow Intelligence Scoring Logic
"""

import pytest
import numpy as np
from src.analytics.cashflow_intel import score_cfo_quality, score_capex_intensity, score_fcf_conversion

def test_score_cfo_quality():
    """Verify classification of CFO/PAT ratio"""
    assert score_cfo_quality(1.2) == "High Quality Earnings"
    assert score_cfo_quality(0.3) == "Accrual Risk"
    assert score_cfo_quality(0.7) == "Normal"
    assert score_cfo_quality(np.nan) == "Normal"
    
def test_score_capex_intensity():
    """Verify classification of CapEx Intensity %"""
    assert score_capex_intensity(2.5) == "Asset-Light"
    assert score_capex_intensity(9.2) == "Capital Intensive"
    assert score_capex_intensity(5.0) == "Moderate"
    assert score_capex_intensity(np.nan) == "Moderate"
    
def test_score_fcf_conversion():
    """Verify classification of FCF / EBITDA conversion"""
    assert score_fcf_conversion(75.0) == "Efficient"
    assert score_fcf_conversion(15.0) == "CapEx Heavy"
    assert score_fcf_conversion(45.0) == "Average"
    assert score_fcf_conversion(np.nan) == "Average"
