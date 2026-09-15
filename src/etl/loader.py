"""
Excel Loader Module for Nifty 100 Financial Intelligence Platform

Handles loading Excel files with custom headers, normalization, and validation.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================
# NORMALIZATION FUNCTIONS
# ============================================================

def normalize_year(year_value) -> Optional[str]:
    """
    Normalize financial year values to YYYY-MM format.
    
    Handles:
    - "Mar-23" -> "2023-03"
    - "2024-03" -> "2024-03"
    - "Mar 2023" -> "2023-03"
    - "March 2023" -> "2023-03"
    - 2023 -> "2023-03"
    
    Args:
        year_value: Raw year value (str, int, or datetime)
        
    Returns:
        Normalized year in YYYY-MM format or None if invalid
        
    Raises:
        ValueError: If year_value is invalid format
    """
    if pd.isna(year_value):
        return None
        
    # Convert to string
    year_str = str(year_value).strip()
    
    # Pattern 1: Mar-23, Apr-24, etc.
    pattern1 = r'^([A-Za-z]{3})-(\d{2})$'
    match1 = re.match(pattern1, year_str)
    if match1:
        month_str, year_short = match1.groups()
        year_full = int("20" + year_short)
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        month_num = month_map.get(month_str.lower())
        if month_num:
            return f"{year_full}-{month_num}"
    
    # Pattern 2: YYYY-MM or YYYY/MM
    pattern2 = r'^(\d{4})[-/](\d{1,2})$'
    match2 = re.match(pattern2, year_str)
    if match2:
        year, month = match2.groups()
        return f"{year}-{int(month):02d}"
    
    # Pattern 3: Mar 2023, March 2023, etc. (with space)
    pattern3 = r'^([A-Za-z]{3,9})\s+(\d{4})$'
    match3 = re.match(pattern3, year_str)
    if match3:
        month_str, year = match3.groups()
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        month_num = month_map.get(month_str.lower())
        if month_num:
            return f"{year}-{month_num}"
    
    # Pattern 4: Just a year (YYYY)
    pattern4 = r'^(\d{4})$'
    match4 = re.match(pattern4, year_str)
    if match4:
        year = match4.group(1)
        return f"{year}-03"  # Assume March (fiscal year end)
    
    logger.warning(f"Could not normalize year value: {year_value}")
    return None


def normalize_ticker(ticker_value) -> Optional[str]:
    """
    Normalize company ticker/ID values to uppercase stripped format.
    
    Handles:
    - "  TCS  " -> "TCS"
    - "tcs" -> "TCS"
    - "tata consultancy services" -> "TCS" (if mapping available)
    - Whitespace trimming
    - Case normalization
    
    Args:
        ticker_value: Raw ticker value (str, int, or other)
        
    Returns:
        Normalized ticker in uppercase or None if invalid
        
    Raises:
        ValueError: If ticker_value is invalid format
    """
    if pd.isna(ticker_value):
        return None
    
    # Convert to string and strip whitespace
    ticker_str = str(ticker_value).strip()
    
    # Remove any internal whitespace and special characters (keep alphanumeric only)
    ticker_str = re.sub(r'[^A-Za-z0-9\-]', '', ticker_str)
    
    if not ticker_str:
        return None
    
    # Convert to uppercase
    ticker_str = ticker_str.upper()
    
    # Validate: should be 1-10 alphanumeric characters
    if not re.match(r'^[A-Z0-9\-]{1,10}$', ticker_str):
        logger.warning(f"Invalid ticker format after normalization: {ticker_value} -> {ticker_str}")
        return None
    
    return ticker_str


# ============================================================
# EXCEL LOADER CLASS
# ============================================================

class ExcelLoader:
    """
    Loads and validates Excel files for Nifty 100 financial data.
    
    Supports:
    - Custom header row specification (header_row parameter)
    - Data normalization (ticker, year)
    - Data validation and quality checks
    - Multiple sheets within single files
    """
    
    # Core dataset configurations
    CORE_DATASETS = {
        'companies': {
            'sheet': 'Companies',
            'header_row': 1,  # 0-indexed: Row 1 = actual headers
            'key_columns': ['id'],
            'nullable_columns': ['company_logo', 'chart_link', 'about_company', 'website', 
                                'nse_profile', 'bse_profile', 'book_value', 'roce_percentage', 
                                'roe_percentage'],
        },
        'profitandloss': {
            'sheet': 'Profit & Loss',
            'header_row': 1,
            'key_columns': ['company_id', 'year'],
            'normalize': {'company_id': normalize_ticker, 'year': normalize_year},
        },
        'balancesheet': {
            'sheet': 'Balance Sheet',
            'header_row': 1,
            'key_columns': ['company_id', 'year'],
            'normalize': {'company_id': normalize_ticker, 'year': normalize_year},
        },
        'cashflow': {
            'sheet': 'Cash Flow',
            'header_row': 1,
            'key_columns': ['company_id', 'year'],
            'normalize': {'company_id': normalize_ticker, 'year': normalize_year},
        },
        'analysis': {
            'sheet': 'Analysis',
            'header_row': 1,
            'key_columns': ['company_id'],
            'normalize': {'company_id': normalize_ticker},
        },
        'documents': {
            'sheet': 'Documents',
            'header_row': 1,
            'key_columns': ['company_id', 'Year'],
            'normalize': {'company_id': normalize_ticker},
        },
        'prosandcons': {
            'sheet': 'Pros & Cons',
            'header_row': 1,
            'key_columns': ['id'],
            'normalize': {'company_id': normalize_ticker},
        },
    }
    
    def __init__(self, data_dir: str = './data'):
        """
        Initialize the ExcelLoader.
        
        Args:
            data_dir: Root directory containing Excel files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        logger.info(f"ExcelLoader initialized with data_dir: {self.data_dir}")
    
    def load_file(
        self,
        filename: str,
        sheet_name: str = 0,
        header_row: Optional[int] = None,
        normalize_cols: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Load an Excel file with optional header row specification.
        
        Args:
            filename: Name of Excel file to load
            sheet_name: Sheet name or index to read
            header_row: Row number to use as header (0-indexed). If None, uses default (0)
            normalize_cols: Dict of {col_name: normalize_func} to apply normalization
            
        Returns:
            Loaded and normalized DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If sheet doesn't exist or data is invalid
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            logger.info(f"Loading {filename} from sheet '{sheet_name}' with header_row={header_row}")
            
            # Load Excel file with specified header row
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from {filename}")
            
            # Apply normalization if specified
            if normalize_cols:
                df = self._normalize_dataframe(df, normalize_cols)
            
            return df
        
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            raise ValueError(f"Failed to load Excel file {filename}: {str(e)}")
    
    def load_core_dataset(self, dataset_name: str) -> pd.DataFrame:
        """
        Load a core dataset with predefined configuration.
        
        Args:
            dataset_name: Name of core dataset ('companies', 'profitandloss', etc.)
            
        Returns:
            Loaded and normalized DataFrame
            
        Raises:
            ValueError: If dataset_name is not recognized
        """
        if dataset_name not in self.CORE_DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(self.CORE_DATASETS.keys())}")
        
        config = self.CORE_DATASETS[dataset_name]
        filename = f"{dataset_name}.xlsx"
        
        logger.info(f"Loading core dataset: {dataset_name}")
        
        df = self.load_file(
            filename=filename,
            sheet_name=config['sheet'],
            header_row=config['header_row'],
            normalize_cols=config.get('normalize')
        )
        
        # Validate key columns exist
        missing_cols = [col for col in config['key_columns'] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing key columns in {dataset_name}: {missing_cols}")
        
        logger.info(f"Successfully loaded {dataset_name}: {len(df)} rows")
        
        return df
    
    def load_all_core_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all core datasets.
        
        Returns:
            Dictionary of {dataset_name: DataFrame}
        """
        datasets = {}
        for dataset_name in self.CORE_DATASETS.keys():
            try:
                datasets[dataset_name] = self.load_core_dataset(dataset_name)
            except Exception as e:
                logger.error(f"Failed to load {dataset_name}: {str(e)}")
                raise
        
        return datasets
    
    def load_supplementary_dataset(
        self,
        filename: str,
        sheet_name: str = 0,
        header_row: int = 0
    ) -> pd.DataFrame:
        """
        Load a supplementary dataset (non-core).
        
        Args:
            filename: Name of Excel file
            sheet_name: Sheet to load
            header_row: Header row number (0-indexed)
            
        Returns:
            Loaded DataFrame
        """
        return self.load_file(
            filename=filename,
            sheet_name=sheet_name,
            header_row=header_row,
            normalize_cols={'company_id': normalize_ticker} if 'company_id' in str(filename).lower() else None
        )
    
    @staticmethod
    def _normalize_dataframe(df: pd.DataFrame, normalize_cols: Dict) -> pd.DataFrame:
        """
        Apply normalization functions to specified columns.
        
        Args:
            df: DataFrame to normalize
            normalize_cols: Dict of {col_name: normalize_func}
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        for col_name, normalize_func in normalize_cols.items():
            if col_name in df.columns:
                logger.debug(f"Normalizing column: {col_name}")
                df[col_name] = df[col_name].apply(normalize_func)
            else:
                logger.warning(f"Column {col_name} not found in DataFrame for normalization")
        
        return df
    
    @staticmethod
    def validate_data_quality(
        df: pd.DataFrame,
        dataset_name: str,
        tolerance_pct: float = 1.0
    ) -> Tuple[bool, List[str]]:
        """
        Validate data quality for a dataset.
        
        Args:
            df: DataFrame to validate
            dataset_name: Name of dataset (for context)
            tolerance_pct: Tolerance percentage for validation checks
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check for null values in key columns
        if dataset_name in ExcelLoader.CORE_DATASETS:
            config = ExcelLoader.CORE_DATASETS[dataset_name]
            nullable = config.get('nullable_columns', [])
            
            for col in config['key_columns']:
                if col in df.columns:
                    null_count = df[col].isna().sum()
                    if null_count > 0:
                        warnings.append(f"{col}: {null_count} null values in key column")
        
        # Check for duplicates in key columns
        if dataset_name in ExcelLoader.CORE_DATASETS:
            key_cols = ExcelLoader.CORE_DATASETS[dataset_name]['key_columns']
            available_keys = [col for col in key_cols if col in df.columns]
            if available_keys:
                duplicates = df[available_keys].duplicated().sum()
                if duplicates > 0:
                    warnings.append(f"{duplicates} duplicate rows based on key columns")
        
        is_valid = len(warnings) == 0
        return is_valid, warnings


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_loader(data_dir: str = './data') -> ExcelLoader:
    """
    Factory function to create an ExcelLoader instance.
    
    Args:
        data_dir: Data directory path
        
    Returns:
        ExcelLoader instance
    """
    return ExcelLoader(data_dir=data_dir)
