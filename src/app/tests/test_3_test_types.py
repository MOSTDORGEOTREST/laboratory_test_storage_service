from httpx import AsyncClient

async def test_type_create(ac: AsyncClient, test_test_types):
    for test_type in test_test_types:
        response = await ac.post(
            "/test_types/",
            json=test_type
        )
        assert response.status_code == 200

    response = await ac.post(
        "/test_types/",
        json=test_type
    )
    assert response.status_code == 409

async def test_type_update(ac: AsyncClient, test_test_types):
    response = await ac.put(
        "/test_types/?test_type_id=1",
        json=test_test_types[0]
    )
    assert response.status_code == 200

async def test_del_test_type(ac: AsyncClient):
    response = await ac.delete(
        f"/test_types/?test_type_id=2",
    )
    assert response.status_code == 204

    response = await ac.get(
        f"/test_types/?limit=500&offset=0",
    )
    assert 2 not in [response.json()[i]["test_type_id"] for i in range(len(response.json()))]
