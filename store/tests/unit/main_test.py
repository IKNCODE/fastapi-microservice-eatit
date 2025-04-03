import sys
import os
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import asyncio

# Добавляем путь к корневой директории проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from main import app


''' Test getting all products'''
@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_products():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.get("store/p/all")
        await client.aclose()
    assert response.status_code == 200

''' Test getting product by his id'''
@pytest.mark.asyncio(loop_scope="session")
async def test_get_product_by_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.get("store/7")
        await client.aclose()
    assert response.status_code == 200
    print(response.json()[0])
    assert response.json()[0]['Products']['name'] == "Бифилайф Самокат, 2,5%, яблоко и банан, с 8 месяцев "

''' Test getting all units'''
@pytest.mark.asyncio(loop_scope="session")
async def test_get_unit():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.get("unit/u/all")
        await client.aclose()
    assert response.status_code == 200




