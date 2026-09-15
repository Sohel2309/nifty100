"""
Unit Tests for NLP Qualitative Analysis Module
"""

import pytest
from src.analytics.nlp import parse_growth_text

def test_parse_growth_text():
    """Verify regex parsing of CAGR growth narratives"""
    res1 = parse_growth_text("10 Years:     15%")
    assert res1.get(10) == 15.0
    
    res2 = parse_growth_text("5 Years          14%")
    assert res2.get(5) == 14.0
    
    res3 = parse_growth_text("Last Year:      12%")
    assert res3.get(1) == 12.0
    
    res4 = parse_growth_text("Invalid text")
    assert len(res4) == 0
