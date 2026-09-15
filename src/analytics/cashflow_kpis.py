"""
Cash Flow KPIs Engine for Nifty 100 Financial Intelligence Platform
Implements FCF, CapEx, CapEx Intensity, FCF Conversion, CFO Quality Score, and Capital Allocation patterns.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

def calculate_fcf(operating_activity: Optional[float], investing_activity: Optional[float]) -> Optional[float]:
    """
    Calculate Free Cash Flow (FCF).
    FCF = CFO + CFI (operating_activity + investing_activity)
    """
    if operating_activity is None or investing_activity is None:
        return None
    return round(operating_activity + investing_activity, 4)

def calculate_capex(investing_activity: Optional[float]) -> Optional[float]:
    """
    Calculate CapEx (as absolute of investing activity proxy).
    """
    if investing_activity is None:
        return None
    return round(abs(investing_activity), 4)

def calculate_capex_intensity(investing_activity: Optional[float], sales: Optional[float]) -> Optional[float]:
    """
    Calculate CapEx Intensity %.
    CapEx Intensity = abs(investing_activity) / sales * 100
    Returns None if sales <= 0 or inputs are missing.
    """
    if investing_activity is None or sales is None or sales <= 0:
        return None
    return round((abs(investing_activity) / sales) * 100, 4)

def calculate_fcf_conversion(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    """
    Calculate FCF Conversion Rate %.
    FCF Conversion = FCF / EBITDA (operating_profit is EBITDA in this dataset) * 100
    Returns None if operating_profit <= 0 or FCF is None.
    """
    if fcf is None or operating_profit is None or operating_profit <= 0:
        return None
    return round((fcf / operating_profit) * 100, 4)

def calculate_cfo_quality(operating_activity: Optional[float], net_profit: Optional[float]) -> Optional[float]:
    """
    Calculate CFO Quality Score (CFO / PAT).
    CFO Quality = operating_activity / net_profit
    Returns None if net_profit <= 0 or operating_activity is None.
    """
    if operating_activity is None or net_profit is None or net_profit <= 0:
        return None
    return round(operating_activity / net_profit, 4)

def classify_capital_allocation(
    operating_activity: Optional[float], 
    investing_activity: Optional[float], 
    financing_activity: Optional[float]
) -> str:
    """
    Classify the company's capital allocation pattern based on the signs of CFO, CFI, and CFF.
    Signs are represented as + (>= 0) or - (< 0).
    
    Returns one of:
      - 'Reinvestor' (+, -, -)
      - 'Expanding / Growth' (+, -, +)
      - 'Return / Mature' (+, +, -)
      - 'Accumulator' (+, +, +)
      - 'Distress' (-, ?, +)  -- CFO < 0 and CFF >= 0
      - 'Severe Distress' (-, -, -)
      - 'Restructuring' (-, +, +) -- CFO < 0, CFI >= 0, CFF >= 0
      - 'Liquidating' (-, +, -)
      - 'Unknown'
    """
    if operating_activity is None or investing_activity is None or financing_activity is None:
        return "Unknown"
        
    cfo = operating_activity
    cfi = investing_activity
    cff = financing_activity
    
    s_cfo = "+" if cfo >= 0 else "-"
    s_cfi = "+" if cfi >= 0 else "-"
    s_cff = "+" if cff >= 0 else "-"
    
    # Check general distress condition first
    # CFO < 0 AND CFF > 0 (or >= 0)
    if cfo < 0 and cff >= 0:
        if cfi >= 0:
            return "Restructuring" # CFO < 0, CFI >= 0, CFF >= 0
        else:
            return "Distress"      # CFO < 0, CFI < 0, CFF >= 0
            
    pattern = (s_cfo, s_cfi, s_cff)
    
    mapping = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "-", "+"): "Expanding / Growth",
        ("+", "+", "-"): "Return / Mature",
        ("+", "+", "+"): "Accumulator",
        ("-", "-", "-"): "Severe Distress",
        ("-", "+", "-"): "Liquidating"
    }
    
    return mapping.get(pattern, "Unknown")
