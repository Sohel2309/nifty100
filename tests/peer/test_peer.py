"""
Unit Tests for Peer Comparison Engine
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.peer import compute_percent_rank

def test_compute_percent_rank():
    """Test SQL-like PERCENT_RANK() rank calculations"""
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    pr = compute_percent_rank(series)
    
    assert pr.iloc[0] == 0.0   # lowest gets 0.0
    assert pr.iloc[4] == 1.0   # highest gets 1.0
    assert pr.iloc[2] == 0.5   # median gets 0.5
    
    # Test ties
    series_ties = pd.Series([10.0, 10.0, 20.0, 30.0])
    pr_ties = compute_percent_rank(series_ties)
    assert pr_ties.iloc[0] == 0.0
    assert pr_ties.iloc[1] == 0.0
    assert pr_ties.iloc[3] == 1.0
    
    # Test single item or empty series
    single = pd.Series([10.0])
    assert compute_percent_rank(single).iloc[0] == 1.0
    
    empty = pd.Series(dtype=float)
    assert len(compute_percent_rank(empty)) == 0
