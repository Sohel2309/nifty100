"""
Financial Ratios Calculation Library for Nifty 100 Financial Intelligence Platform
Implements core profitability, leverage, and efficiency ratios.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

def calculate_npm(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """
    Calculate Net Profit Margin (NPM) %.
    NPM = net_profit / sales * 100
    Returns None if sales <= 0 or either input is None.
    """
    if sales is None or sales <= 0:
        return None
    if net_profit is None:
        return None
    return round((net_profit / sales) * 100, 4)

def calculate_opm(
    operating_profit: Optional[float], 
    sales: Optional[float], 
    reported_opm: Optional[float] = None, 
    company_id: str = "", 
    year: str = ""
) -> Optional[float]:
    """
    Calculate Operating Profit Margin (OPM) %.
    OPM = operating_profit / sales * 100
    Cross-checks vs reported OPM and logs a warning on mismatch >= 1.0%.
    Returns None if sales <= 0 or either input is None.
    """
    if sales is None or sales <= 0:
        return None
    if operating_profit is None:
        return None
    
    computed_opm = (operating_profit / sales) * 100
    
    if reported_opm is not None:
        if abs(computed_opm - reported_opm) >= 1.0:
            logger.warning(
                f"[DQ-05 OPM Mismatch] Co: {company_id}, Year: {year} | Computed: {computed_opm:.2f}%, Reported: {reported_opm:.2f}%"
            )
            
    return round(computed_opm, 4)

def calculate_roe(net_profit: Optional[float], equity_capital: Optional[float], reserves: Optional[float]) -> Optional[float]:
    """
    Calculate Return on Equity (ROE) %.
    ROE = net_profit / (equity_capital + reserves) * 100
    Returns None if total equity <= 0 or net_profit is None.
    """
    if equity_capital is None or reserves is None:
        return None
    total_equity = equity_capital + reserves
    if total_equity <= 0:
        return None
    if net_profit is None:
        return None
    return round((net_profit / total_equity) * 100, 4)

def calculate_roce(
    operating_profit: Optional[float], 
    depreciation: Optional[float], 
    equity_capital: Optional[float], 
    reserves: Optional[float], 
    borrowings: Optional[float]
) -> Optional[float]:
    """
    Calculate Return on Capital Employed (ROCE) %.
    EBIT = operating_profit - depreciation
    ROCE = EBIT / (equity_capital + reserves + borrowings) * 100
    Returns None if capital employed <= 0 or inputs are missing.
    """
    if operating_profit is None or depreciation is None:
        return None
    ebit = operating_profit - depreciation
    
    if equity_capital is None or reserves is None or borrowings is None:
        return None
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return round((ebit / capital_employed) * 100, 4)

def calculate_debt_to_equity(
    borrowings: Optional[float], 
    equity_capital: Optional[float], 
    reserves: Optional[float]
) -> Optional[float]:
    """
    Calculate Debt-to-Equity ratio.
    D/E = borrowings / (equity_capital + reserves)
    Returns 0.0 if borrowings == 0.
    Returns None if total equity <= 0.
    """
    if equity_capital is None or reserves is None:
        return None
    total_equity = equity_capital + reserves
    if total_equity <= 0:
        return None
    if borrowings is None:
        return None
    if borrowings == 0:
        return 0.0
    return round(borrowings / total_equity, 4)

def calculate_interest_coverage(
    operating_profit: Optional[float], 
    other_income: Optional[float], 
    interest: Optional[float]
) -> Optional[float]:
    """
    Calculate Interest Coverage Ratio (ICR).
    ICR = (operating_profit + other_income) / interest
    Returns None if interest <= 0 (representing 'Debt Free' or unserviceable).
    """
    if interest is None or interest <= 0:
        return None
    op_prof = operating_profit if operating_profit is not None else 0.0
    oth_inc = other_income if other_income is not None else 0.0
    return round((op_prof + oth_inc) / interest, 4)

def calculate_asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """
    Calculate Asset Turnover.
    Asset Turnover = sales / total_assets
    Returns None if total_assets <= 0 or sales is None.
    """
    if total_assets is None or total_assets <= 0:
        return None
    if sales is None:
        return None
    return round(sales / total_assets, 4)

def calculate_book_value_per_share(
    equity_capital: Optional[float], 
    reserves: Optional[float], 
    face_value: Optional[float]
) -> Optional[float]:
    """
    Calculate Book Value Per Share.
    Book Value Per Share = (total_equity / equity_capital) * (face_value / 100)
    Returns None if equity_capital <= 0 or inputs are missing.
    """
    if equity_capital is None or reserves is None or face_value is None or equity_capital <= 0:
        return None
    total_equity = equity_capital + reserves
    return round((total_equity / equity_capital) * (face_value / 100), 4)
