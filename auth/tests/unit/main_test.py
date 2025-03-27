import sys
import os
import pytest
from httpx import ASGITransport, AsyncClient
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app

@pytest.mark.asyncio(loop_scope="session")
async def test_authorization():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8082") as client:
        response = await client.post("/auth/login", json={"login":"1231", "password":"123"})
        await client.aclose()
    assert response.status_code == 200

@pytest.mark.asyncio(loop_scope="session")
async def test_wrong_authorization():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8082") as client:
        response = await client.post("/auth/login", json={"login":"wrong_login", "password":"wrong_password"})
        await client.aclose()
    assert response.status_code == 401

