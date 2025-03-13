import pytest, datetime
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.mark.asyncio
async def test_get_rolls_1():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/rolls")
        assert response.status_code == 404
        data = response.json()

@pytest.mark.asyncio
async def test_add_roll():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/rolls", json={"length": 10, "weight": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["length"] == 10
        assert data["weight"] == 10

@pytest.mark.asyncio
async def test_get_rolls_2():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/rolls")
        assert response.status_code == 200
        data = response.json()
        print(data[0])
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["length"] == 10
        assert data[0]["weight"] == 10
        assert data[0]["date_create"] == str(datetime.date.today())
        assert data[0]["date_delete"] == None

@pytest.mark.asyncio
async def test_delete_roll_1():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/delete/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data["id"] == 1
        assert data["length"] == 10
        assert data["weight"] == 10
        assert data["date_create"] == str(datetime.date.today())
        assert data["date_delete"] == str(datetime.date.today())

@pytest.mark.asyncio
async def test_delete_roll_2():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/delete/1")
        assert response.status_code == 404
