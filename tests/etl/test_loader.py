import pytest
import sqlite3
import pandas as pd
from pathlib import Path
from src.db.loader import DatabaseLoader, run_etl_load
from src.etl.loader import ExcelLoader

def test_db_schema_initialization(tmp_path):
    """Test that all 12 tables are created successfully from schema.sql"""
    db_file = tmp_path / "nifty100_test.db"
    schema_file = Path("src/db/schema.sql")
    
    db_loader = DatabaseLoader(db_path=str(db_file), schema_path=str(schema_file))
    assert db_loader.initialize_database(force_recreate=True) is True
    
    # Check tables in SQLite
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    expected_tables = [
        'companies', 'profitandloss', 'balancesheet', 'cashflow',
        'analysis', 'documents', 'prosandcons', 'sectors',
        'stock_prices', 'market_cap', 'financial_ratios', 'peer_groups'
    ]
    for table in expected_tables:
        assert table in tables

def test_table_schemas_contain_new_tables():
    """Test that DatabaseLoader.TABLE_SCHEMAS contains new schemas"""
    schemas = DatabaseLoader.TABLE_SCHEMAS
    assert 'financial_ratios' in schemas
    assert 'peer_groups' in schemas
    
    # Check key columns
    assert 'net_profit_margin_pct' in schemas['financial_ratios']
    assert 'is_benchmark' in schemas['peer_groups']
