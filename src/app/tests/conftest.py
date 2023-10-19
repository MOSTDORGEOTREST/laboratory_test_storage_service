from datetime import datetime

import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
import asyncio

from main import app
from main import configs

@pytest.fixture(scope="session")
def user():
    return {
        "username": configs.superuser_name,
        "password": configs.superuser_password,
    }

@pytest.fixture(scope="session")
def fake_user():
    return {
        "username": "fake",
        "password": "fake",
    }

@pytest.fixture(scope="session")
def test_object():
    return {
        "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA",
        "object_number": "111-11"
    }

@pytest.fixture(scope="session")
def test_boreholes():
    return [
        {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "borehole_name": "Borehole 1", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"},
        {"borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG", "borehole_name": "Borehole 2", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"},
        {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "borehole_name": "Borehole 3", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"}
    ]

@pytest.fixture(scope="session")
def test_wrong_boreholes():
    return [
        {"borehole_id": "xxx", "borehole_name": "Borehole wrong", "object_id": "xxx"},
    ]

@pytest.fixture(scope="session")
def test_samples():
    return [
        {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8",
         "laboratory_number": "11-1", "soil_type": "\u0421\u0443\u0433\u043b\u0438\u043d\u043e\u043a"},
        {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "KDajpo2gZfgEziujZ260QK9q7Isj0Ivl",
         "laboratory_number": "11-2",
         "soil_type": "\u0413\u043b\u0438\u043d\u0430 \u043f\u043b\u0430\u0441\u0442\u0438\u0447\u043d\u0430\u044f"},
        {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "XyRpq95O3AyIvvgNdHi9jRB593U0aqyI",
         "laboratory_number": "11-3", "soil_type": "\u0421\u0443\u043f\u0435\u0441\u044c"},
        {"borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG", "sample_id": "qvorVHlVuJeaz9mWVqgm3CIdBqaHa0yx",
         "laboratory_number": "12-1", "soil_type": "\u041f\u0435\u0441\u043e\u043a"},
        {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "WXeFV9FLq7rPtoGooTF8eMlW8Wgbc1ev",
         "laboratory_number": "10-1", "soil_type": "\u041f\u0435\u0441\u043e\u043a"},
        {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "PMZaoMF24AHFmAkgNHtE6t4IfUWkZa4G",
         "laboratory_number": "10-2",
         "soil_type": "\u041f\u0435\u0441\u043e\u043a \u0433\u0440\u0430\u0432\u0438\u0439\u043d\u044b\u0439"},
        {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "Q18wEMxp0Ui34Z3K4VpQbVg8QknXK8uV",
         "laboratory_number": "10-3",
         "soil_type": "\u041f\u0435\u0441\u043e\u043a \u043f\u044b\u043b\u0435\u0432\u0430\u0442\u044b\u0439"}
    ]

@pytest.fixture(scope="session")
def test_wrong_samples():
    return [
        {"borehole_id": "xxx", "sample_id": "xxx",
         "laboratory_number": "11-1", "soil_type": "\u0421\u0443\u0433\u043b\u0438\u043d\u043e\u043a"},
    ]


@pytest.fixture(scope="session")
def test_test_types():
    return [
        {
            "test_type": "сyclic",
            "description": "Динамическое разжижение грунтов",
        },
        {
            "test_type": "resonant",
            "description": "Резонансная колонка",
        },
        {
            "test_type": "vibration",
            "description": "Виброползучесть",
        },
    ]

@pytest.fixture(scope="session")
def test_wrong_test():
    return {
        "sample_id": "xxx",
        "test_type_id": 790,
        "timestamp": datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S"),
        "test_params": {
            "sigma_3": 100,
            "sigma_1": 200,
            "amplitude": 10,
            "frequency": 0.2,
        },
        "test_results": {
            "max_ppr": 0.98,
            "max_strain": 0.051
        },
    }

@pytest.fixture(scope="session")
def test_tests():
    return [
        {
            "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8",
            "test_type_id": 1,
            "timestamp": datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S"),
            "test_params": {
                "sigma_3": 100,
                "sigma_1": 200,
                "amplitude": 10,
                "frequency": 0.2,
            },
            "test_results": {
                "max_ppr": 0.5,
                "max_strain": 0.034
            },
        },
        {
            "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8",
            "test_type_id": 1,
            "timestamp": datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S"),
            "test_params": {
                "sigma_3": 150,
                "sigma_1": 200,
                "amplitude": 15,
                "frequency": 0.2,
            },
            "test_results": {
                "max_ppr": 0.98,
                "max_strain": 0.051
            },
        },
        {
            "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8",
            "test_type_id": 3,
            "timestamp": datetime(2023, 10, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S"),
            "test_params": {
                "sigma_3": 200,
                "sigma_1": 200,
                "amplitude": 5,
                "frequency": 0.2,
            },
            "test_results": {
                "max_ppr": 0.58,
                "max_strain": 0.015
            },
        },
    ]

@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac