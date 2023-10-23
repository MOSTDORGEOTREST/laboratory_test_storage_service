from httpx import AsyncClient

async def test_create(ac: AsyncClient, test_tests, test_wrong_test):
    for test in test_tests:
        response = await ac.post(
            "/tests/",
            json=test
        )
        assert response.status_code == 200

    response = await ac.post(
        "/tests/",
        json=test_wrong_test
    )
    assert response.status_code == 404

async def test_update(ac: AsyncClient, test_tests):
    response = await ac.put(
        "/tests/?test_id=1",
        json=test_tests[2]
    )
    assert response.status_code == 200

async def test_del_test(ac: AsyncClient):
    response = await ac.delete(
        f"/tests/?test_id=1",
    )
    assert response.status_code == 204

    #response = await ac.get(
    #    f"/tests/?limit=500&offset=0",
    #)
    #assert 1 not in [response.json()[i]["test_id"] for i in range(len(response.json()))]
