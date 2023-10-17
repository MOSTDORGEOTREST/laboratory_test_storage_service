test_data = {
    "object": {
        "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA",
        "object_number": "111-11",
    },
    "boreholes": [
        {
            "borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae",
            "borehole_name": "Cкважина 1",
            "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA",
        },
        {
            "borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG",
            "borehole_name": "Cкважина 2",
            "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA",
        },
        {
            "borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M",
            "borehole_name": "Cкважина 3",
            "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA",
        },

    ],
    "samples": [
        {
            "borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae",
            "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8",
            "laboratory_number": "11-1",
            "soil_type": "Суглинок",
        },
{
            "borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae",
            "sample_id": "KDajpo2gZfgEziujZ260QK9q7Isj0Ivl",
            "laboratory_number": "11-2",
            "soil_type": "Глина пластичная",
        },
{
            "borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae",
            "sample_id": "XyRpq95O3AyIvvgNdHi9jRB593U0aqyI",
            "laboratory_number": "11-3",
            "soil_type": "Супесь",
        },
        {
            "borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG",
            "sample_id": "qvorVHlVuJeaz9mWVqgm3CIdBqaHa0yx",
            "laboratory_number": "12-1",
            "soil_type": "Песок",
        },
        {
            "borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M",
            "sample_id": "WXeFV9FLq7rPtoGooTF8eMlW8Wgbc1ev",
            "laboratory_number": "10-1",
            "soil_type": "Песок",
        },
{
            "borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M",
            "sample_id": "PMZaoMF24AHFmAkgNHtE6t4IfUWkZa4G",
            "laboratory_number": "10-2",
            "soil_type": "Песок гравийный",
        },
{
            "borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M",
            "sample_id": "Q18wEMxp0Ui34Z3K4VpQbVg8QknXK8uV",
            "laboratory_number": "10-3",
            "soil_type": "Песок пылеватый",
        },

    ],
}
import json
s = json.dumps(test_data)
print(s)

{"object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA", "object_number": "111-11"}

[
    {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "borehole_name": "C\u043a\u0432\u0430\u0436\u0438\u043d\u0430 1", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"},
    {"borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG", "borehole_name": "C\u043a\u0432\u0430\u0436\u0438\u043d\u0430 2", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"},
    {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "borehole_name": "C\u043a\u0432\u0430\u0436\u0438\u043d\u0430 3", "object_id": "lU7MGLdT9mN6aXjgCxqkqSixNRbhfjTA"}
]

[
    {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "wVPddOIxR3Atks9Uk47wuzZ33zwj0HS8", "laboratory_number": "11-1", "soil_type": "\u0421\u0443\u0433\u043b\u0438\u043d\u043e\u043a"}, {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "KDajpo2gZfgEziujZ260QK9q7Isj0Ivl", "laboratory_number": "11-2", "soil_type": "\u0413\u043b\u0438\u043d\u0430 \u043f\u043b\u0430\u0441\u0442\u0438\u0447\u043d\u0430\u044f"},
    {"borehole_id": "voeSOHOIgB6dYC3j7LjlEwPANT5E09ae", "sample_id": "XyRpq95O3AyIvvgNdHi9jRB593U0aqyI", "laboratory_number": "11-3", "soil_type": "\u0421\u0443\u043f\u0435\u0441\u044c"},
    {"borehole_id": "IdOwUktwXGlkSn1jiKgYUcjqh5B4xxXG", "sample_id": "qvorVHlVuJeaz9mWVqgm3CIdBqaHa0yx", "laboratory_number": "12-1", "soil_type": "\u041f\u0435\u0441\u043e\u043a"},
    {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "WXeFV9FLq7rPtoGooTF8eMlW8Wgbc1ev", "laboratory_number": "10-1", "soil_type": "\u041f\u0435\u0441\u043e\u043a"},
    {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "PMZaoMF24AHFmAkgNHtE6t4IfUWkZa4G", "laboratory_number": "10-2", "soil_type": "\u041f\u0435\u0441\u043e\u043a \u0433\u0440\u0430\u0432\u0438\u0439\u043d\u044b\u0439"},
    {"borehole_id": "oJY7KtZy1qDrA3NxBDHSS8oSG2kEYb3M", "sample_id": "Q18wEMxp0Ui34Z3K4VpQbVg8QknXK8uV", "laboratory_number": "10-3", "soil_type": "\u041f\u0435\u0441\u043e\u043a \u043f\u044b\u043b\u0435\u0432\u0430\u0442\u044b\u0439"}
]
'''