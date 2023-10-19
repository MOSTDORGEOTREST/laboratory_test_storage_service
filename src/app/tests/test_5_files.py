from httpx import AsyncClient

async def test_file_create(ac: AsyncClient):
    response = await ac.post(
        "/tests/files/?test_id=0",
        files={'file': open('./tests/file.png', 'rb')}
    )
    assert response.status_code == 404

    response = await ac.post(
        "/tests/files/?test_id=2",
        files={'file': open('./tests/file.png', 'rb')}
    )
    assert response.status_code == 200

    response = await ac.post(
        "/tests/files/?test_id=2",
        files={'file': open('./tests/file.png', 'rb')}
    )
    assert response.status_code == 200

async def test_file_get(ac: AsyncClient):
    response = await ac.get(
        "tests/files/?test_id=2"
    )
    assert response.status_code == 200

async def test_file_delete(ac: AsyncClient):
    response = await ac.delete(
        "tests/files/?test_id=2"
    )
    assert response.status_code == 204

    response = await ac.get(
        "tests/files/?test_id=2"
    )
    assert response.status_code == 404

