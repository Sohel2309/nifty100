"""
CAGR Engine for Nifty 100 Financial Intelligence Platform
Computes Revenue, PAT, and EPS CAGRs for 3yr, 5yr, and 10yr windows.
Handles turnaround flags and negative base values.
"""

import logging
from typing import Optional, Tuple, Dict, List

logger = logging.getLogger(__name__)

def calculate_cagr(
    start_value: Optional[float], 
    end_value: Optional[float], 
    n: int
) -> Tuple[Optional[float], bool]:
    """
    Calculate Compound Annual Growth Rate (CAGR) %.
    Formula: ((end_value / start_value) ** (1 / n) - 1) * 100
    
    Returns:
        Tuple[cagr_value, turnaround_flag]
        - cagr_value: CAGR % or None if mathematically undefined.
        - turnaround_flag: True if start_value < 0 and end_value > 0 (Turnaround).
    """
    if start_value is None or end_value is None or n <= 0:
        return None, False
    
    # Check for turnaround scenario
    turnaround_flag = (start_value < 0 and end_value > 0)
    
    # If base value is negative, CAGR is mathematically undefined in real numbers
    if start_value <= 0:
        return None, turnaround_flag
        
    # If end value is negative or zero, ratio is <= 0. Fractional power is undefined or zero.
    if end_value <= 0:
        return None, turnaround_flag
        
    try:
        cagr = ((end_value / start_value) ** (1 / n) - 1) * 100
        return round(cagr, 4), turnaround_flag
    except Exception as e:
        logger.error(f"Error calculating CAGR: {e}")
        return None, turnaround_flag

def parse_year_string(year_str: str) -> Tuple[int, str]:
    """Parse year string like '2024-03' into (2024, '03')"""
    parts = year_str.split('-')
    year_num = int(parts[0])
    month = parts[1] if len(parts) > 1 else '03'
    return year_num, month

def get_historical_year(year_str: str, offset_years: int) -> str:
    """Get the year string offset by offset_years. E.g. '2024-03' - 3 -> '2021-03'"""
    year_num, month = parse_year_string(year_str)
    prev_year = year_num - offset_years
    return f"{prev_year:04d}-{month}"

def calculate_cagr_for_company(
    years_data: Dict[str, float], 
    latest_year: str, 
    n: int,
    company_id: str = "",
    metric_name: str = ""
) -> Tuple[Optional[float], bool]:
    """
    Calculate N-year CAGR for a company given a dictionary of {year: value} and a target latest_year.
    """
    start_year = get_historical_year(latest_year, n)
    
    start_val = years_data.get(start_year)
    end_val = years_data.get(latest_year)
    
    if start_val is None or end_val is None:
        return None, False
        
    cagr_val, turnaround = calculate_cagr(start_val, end_val, n)
    
    if turnaround:
        logger.info(
            f"[CAGR Turnaround] Co: {company_id}, Metric: {metric_name}, Period: {n}yr | "
            f"Base ({start_year}): {start_val}, End ({latest_year}): {end_val}"
        )
    elif cagr_val is None:
        logger.info(
            f"[CAGR Undefined] Co: {company_id}, Metric: {metric_name}, Period: {n}yr | "
            f"Base ({start_year}): {start_val}, End ({latest_year}): {end_val}"
        )
        
    return cagr_val, turnaround

def calculate_average_metric(
    years_data: Dict[str, float], 
    latest_year: str, 
    n: int
) -> Optional[float]:
    """
    Calculate the simple average of a metric over n years ending at latest_year.
    Requires all n years to be present in the data.
    """
    year_num, month = parse_year_string(latest_year)
    vals = []
    
    for i in range(n):
        y_str = f"{(year_num - i):04d}-{month}"
        val = years_data.get(y_str)
        if val is None:
            return None
        vals.append(val)
        
    if len(vals) < n:
        return None
        
    return round(sum(vals) / n, 4)
