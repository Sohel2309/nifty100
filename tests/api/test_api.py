"""
Unit Tests for FastAPI Main REST Endpoints
"""

import pytest
import httpx
from src.api.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

@pytest.mark.anyio
async def test_companies_count(client):
    """Test companies list endpoint returns all 92 companies"""
    response = await client.get("/api/v1/companies")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 92
    
@pytest.mark.anyio
async def test_invalid_ticker(client):
    """Test retrieving invalid company returns 404"""
    response = await client.get("/api/v1/companies/INVALID")
    assert response.status_code == 404
    
@pytest.mark.anyio
async def test_screener_filter(client):
    """Test stock screening filters"""
    response = await client.get("/api/v1/screener?min_roe=15")
    assert response.status_code == 200
    
    data = response.json()
    for co in data:
        assert co['ROE'] >= 15.0
        
@pytest.mark.anyio
async def test_company_ratios(client):
    """Test retrieving ratios for TCS"""
    response = await client.get("/api/v1/companies/TCS/ratios")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 10  # should contain >= 10 years of ratios
    for row in data:
        assert row['company_id'] == 'TCS'
