from httpx import AsyncClient

async def test_file_create(ac: AsyncClient, test_tests, test_wrong_test):
    response = await ac.post(
        "/tests/files/?test_id=0",
        files={'test': open('./tests/file.png', 'rb')}
    )
    assert response.status_code == 404

    response = await ac.post(
        "/tests/files/?test_id=2",
        files={'test': open('./tests/file.png', 'rb')}
    )
    assert response.status_code == 200