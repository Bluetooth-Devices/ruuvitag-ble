from ruuvitag_ble import RuuvitagBluetoothDeviceData
from tests.utils import (
    KEY_ACCELERATION_TOTAL,
    KEY_ACCELERATION_X,
    KEY_ACCELERATION_Y,
    KEY_ACCELERATION_Z,
    KEY_HUMIDITY,
    KEY_PRESSURE,
    KEY_TEMPERATURE,
    KEY_VOLTAGE,
    bytes_to_service_info,
)

V3_SENSOR_DATA = bytes.fromhex("03b20c1fca20007a002603d0088f")  # fmt: skip
V3_SENSOR_DATA_SUBZERO = bytes.fromhex("03b28145ca20007a002603d0088f")  # fmt: skip


def test_parsing_v3():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V3_SENSOR_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag 0000"
    assert up.devices[None].name == expected_name
    assert up.entity_values[KEY_TEMPERATURE].native_value == 12.31  # Celsius
    assert up.entity_values[KEY_HUMIDITY].native_value == 89.0  # %
    assert up.entity_values[KEY_PRESSURE].native_value == 1017.44  # hPa
    assert up.entity_values[KEY_VOLTAGE].native_value == 2191  # mV
    assert up.entity_values[KEY_ACCELERATION_X].native_value == 1.2  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Y].native_value == 0.37  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Z].native_value == 9.57  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value == 9.65  # m/s^2


def test_parsing_v3_subzero():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V3_SENSOR_DATA_SUBZERO)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    # via the datasheet: 0x8145 = -1.69 °C
    assert up.entity_values[KEY_TEMPERATURE].native_value == -1.69  # Celsius
