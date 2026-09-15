"""
ETL Module for Nifty 100 Financial Intelligence Platform
Handles data loading, normalization, and validation
"""

from .loader import ExcelLoader, normalize_year, normalize_ticker

__all__ = ['ExcelLoader', 'normalize_year', 'normalize_ticker']
