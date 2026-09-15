"""
Unit Tests for FastAPI Health Endpoint
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
async def test_health_200(client):
    """Test health check endpoint returns 200 and expected counts"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data['status'] == 'ok'
    assert 'db_row_counts' in data
    assert data['db_row_counts']['companies'] == 92
