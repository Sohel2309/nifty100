"""
Unit Tests for Cash Flow KPIs, Capital Allocation Classification, and Relative ROCE Logic
"""

import pytest
import pandas as pd
from src.analytics.cashflow_kpis import (
    calculate_fcf,
    calculate_capex,
    calculate_capex_intensity,
    calculate_fcf_conversion,
    calculate_cfo_quality,
    classify_capital_allocation
)
from src.analytics.compute_ratios import analyze_bank_roce

def test_cashflow_kpis_normal():
    """Test standard calculations for Cash Flow KPIs"""
    # FCF = CFO (operating) + CFI (investing)
    assert calculate_fcf(100.0, -40.0) == 60.0
    assert calculate_fcf(50.0, 10.0) == 60.0
    
    # CapEx = abs(CFI)
    assert calculate_capex(-80.0) == 80.0
    assert calculate_capex(20.0) == 20.0
    
    # CapEx Intensity = abs(CFI) / Sales * 100
    assert calculate_capex_intensity(-10.0, 100.0) == 10.0
    
    # FCF Conversion = FCF / EBITDA * 100
    assert calculate_fcf_conversion(60.0, 120.0) == 50.0
    
    # CFO Quality = CFO / PAT
    assert calculate_cfo_quality(150.0, 100.0) == 1.5

def test_cashflow_kpis_edge_cases():
    """Test Cash Flow KPIs under zero/negative conditions and missing inputs"""
    # FCF missing inputs
    assert calculate_fcf(None, -40.0) is None
    assert calculate_fcf(100.0, None) is None
    
    # CapEx missing inputs
    assert calculate_capex(None) is None
    
    # CapEx Intensity with zero/negative sales or missing inputs
    assert calculate_capex_intensity(-10.0, 0.0) is None
    assert calculate_capex_intensity(-10.0, -50.0) is None
    assert calculate_capex_intensity(None, 100.0) is None
    
    # FCF Conversion with zero/negative operating profit or missing inputs
    assert calculate_fcf_conversion(60.0, 0.0) is None
    assert calculate_fcf_conversion(60.0, -10.0) is None
    assert calculate_fcf_conversion(None, 120.0) is None
    
    # CFO Quality with zero/negative net profit or missing inputs
    assert calculate_cfo_quality(150.0, 0.0) is None
    assert calculate_cfo_quality(150.0, -20.0) is None
    assert calculate_cfo_quality(None, 100.0) is None

def test_capital_allocation_patterns():
    """Test all 8 CFO, CFI, CFF sign combinations for capital allocation classification"""
    # 1. Reinvestor (+, -, -)
    assert classify_capital_allocation(100.0, -50.0, -30.0) == "Reinvestor"
    
    # 2. Expanding / Growth (+, -, +)
    assert classify_capital_allocation(100.0, -50.0, 20.0) == "Expanding / Growth"
    
    # 3. Return / Mature (+, +, -)
    assert classify_capital_allocation(100.0, 40.0, -30.0) == "Return / Mature"
    
    # 4. Accumulator (+, +, +)
    assert classify_capital_allocation(100.0, 40.0, 20.0) == "Accumulator"
    
    # 5. Distress (-, -, +) -> CFO < 0 and CFF >= 0
    assert classify_capital_allocation(-50.0, -20.0, 60.0) == "Distress"
    
    # 6. Severe Distress (-, -, -)
    assert classify_capital_allocation(-50.0, -20.0, -10.0) == "Severe Distress"
    
    # 7. Restructuring (-, +, +) -> CFO < 0, CFI >= 0, CFF >= 0
    assert classify_capital_allocation(-50.0, 10.0, 40.0) == "Restructuring"
    
    # 8. Liquidating (-, +, -)
    assert classify_capital_allocation(-50.0, 10.0, -30.0) == "Liquidating"
    
    # Missing input
    assert classify_capital_allocation(None, -50.0, -30.0) == "Unknown"

def test_analyze_bank_roce_output_generation():
    """Verify that analyze_bank_roce correctly produces sector_roce_notes.csv"""
    import os
    # Run analysis function on the development DB
    analyze_bank_roce(db_path="./data/nifty100.db")
    
    # Verify file is generated
    csv_path = "output/sector_roce_notes.csv"
    assert os.path.exists(csv_path)
    
    # Read output and verify columns and headers
    df = pd.read_csv(csv_path)
    required_cols = {'company_id', 'year', 'sub_sector', 'computed_roce', 'sector_median_roce', 'deviation_from_median', 'classification', 'anomaly_flag', 'note'}
    assert required_cols.issubset(df.columns)
    
    # Ensure financials sector companies (like HDFCBANK) exist in output
    assert "HDFCBANK" in df['company_id'].unique()
