from httpx import AsyncClient
from config import configs

async def test_fake_auth(ac: AsyncClient, fake_user):
    response = await ac.post("/auth/sign-in/", data=fake_user)
    assert response.status_code == 401

async def test_auth(ac: AsyncClient, user):
    response = await ac.post("/auth/sign-in/", data=user)
    assert response.status_code == 200

async def test_user(ac: AsyncClient):
    response = await ac.get("/auth/user/")
    assert response.status_code == 200
    assert response.json()["username"] == configs.superuser_name

async def test_token(ac: AsyncClient):
    response = await ac.post("/auth/token/")
    assert response.status_code == 200