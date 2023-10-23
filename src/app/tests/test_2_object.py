from httpx import AsyncClient

async def test_create_wrong_boreholes(ac: AsyncClient, test_wrong_boreholes):
    response = await ac.post(
        "/objects/boreholes",
        json=test_wrong_boreholes
    )
    assert response.status_code == 417

async def test_create_object(ac: AsyncClient, test_object):
    response = await ac.post(
        "/objects/objects",
        json=test_object
    )
    assert response.status_code == 201

async def test_create_wrong_samples(ac: AsyncClient, test_wrong_samples):
    response = await ac.post(
        "/objects/samples",
        json=test_wrong_samples
    )
    assert response.status_code == 417

async def test_create_boreholes(ac: AsyncClient, test_boreholes):
    response = await ac.post(
        "/objects/boreholes",
        json=test_boreholes
    )
    assert response.status_code == 201

async def test_create_samples(ac: AsyncClient, test_samples):
    response = await ac.post(
        "/objects/samples",
        json=test_samples
    )
    assert response.status_code == 201

async def test_del_samples(ac: AsyncClient, test_samples):
    response = await ac.delete(
        f"/objects/samples?sample_id={test_samples[1]['sample_id']}",
    )
    assert response.status_code == 204

async def test_del_borehole(ac: AsyncClient, test_boreholes):
    response = await ac.delete(
        f"/objects/boreholes?borehole_id={test_boreholes[1]['borehole_id']}",
    )
    assert response.status_code == 204