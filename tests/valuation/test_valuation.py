"""
Unit Tests for Valuation and Market Data Engine
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.valuation import score_valuation

def test_score_valuation():
    """Test overvaluation/undervaluation P/E rules"""
    # Overvaluation Flag: P/E > (sector_median * 1.5) -> 'Caution'
    # Undervaluation Flag: P/E < (sector_median * 0.7) -> 'Discount'
    # Else -> 'Neutral'
    
    # Mock row dict
    row_caution = {'pe_ratio': 30.0, 'sector_median_pe': 18.0} # 30 > 18 * 1.5 (27.0)
    assert score_valuation(row_caution) == 'Caution'
    
    row_discount = {'pe_ratio': 10.0, 'sector_median_pe': 18.0} # 10 < 18 * 0.7 (12.6)
    assert score_valuation(row_discount) == 'Discount'
    
    row_neutral = {'pe_ratio': 20.0, 'sector_median_pe': 18.0} # 12.6 <= 20 <= 27.0
    assert score_valuation(row_neutral) == 'Neutral'
    
    row_null1 = {'pe_ratio': None, 'sector_median_pe': 18.0}
    assert score_valuation(row_null1) == 'Neutral'
    
    row_null2 = {'pe_ratio': 20.0, 'sector_median_pe': None}
    assert score_valuation(row_null2) == 'Neutral'
    
    row_zero = {'pe_ratio': 20.0, 'sector_median_pe': 0.0}
    assert score_valuation(row_zero) == 'Neutral'
