from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, DeviceKey

from ruuvitag_ble import RuuvitagBluetoothDeviceData

V5_OUTDOOR_SENSOR_DATA = bytes.fromhex("0505a060a0c89afd34028cff006376726976dead7b3fefaf")  # fmt: skip
V5_OUTDOOR_SENSOR_DATA_INVALID_ACCEL = bytes.fromhex("0505a060a0c89a8000028cff006376726976dead7b3fefaf")  # fmt: skip
# INDOOR_SENSOR_DATA = bytes.fromhex("050ea44d7ec818fcbcfdf0ffb42bf600103cd9370ff7aa48")  # fmt: skip
V3_SENSOR_DATA = bytes.fromhex("03b20c1fca20007a002603d0088f")  # fmt: skip

KEY_TEMPERATURE = DeviceKey(key=DeviceClass.TEMPERATURE, device_id=None)
KEY_HUMIDITY = DeviceKey(key=DeviceClass.HUMIDITY, device_id=None)
KEY_PRESSURE = DeviceKey(key=DeviceClass.PRESSURE, device_id=None)
KEY_VOLTAGE = DeviceKey(key=DeviceClass.VOLTAGE, device_id=None)
KEY_MOVEMENT = DeviceKey(key="movement_counter", device_id=None)
KEY_ACCELERATION_X = DeviceKey(key="acceleration_x", device_id=None)
KEY_ACCELERATION_Y = DeviceKey(key="acceleration_y", device_id=None)
KEY_ACCELERATION_Z = DeviceKey(key="acceleration_z", device_id=None)
KEY_ACCELERATION_TOTAL = DeviceKey(key="acceleration_total", device_id=None)


def bytes_to_service_info(payload: bytes) -> BluetoothServiceInfo:
    return BluetoothServiceInfo(
        name="Test",
        address="00:00:00:00:00:00",
        rssi=-60,
        manufacturer_data={1177: payload},
        service_data={},
        service_uuids=[],
        source="",
    )


def test_parsing_v5():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V5_OUTDOOR_SENSOR_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag EFAF"
    assert up.devices[None].name == expected_name  # Parsed from advertisement
    assert up.entity_values[KEY_TEMPERATURE].native_value == 7.2  # Celsius
    assert up.entity_values[KEY_HUMIDITY].native_value == 61.84  # %
    assert up.entity_values[KEY_PRESSURE].native_value == 1013.54  # hPa
    assert up.entity_values[KEY_VOLTAGE].native_value == 2395  # mV
    assert up.entity_values[KEY_MOVEMENT].native_value == 114  # count
    assert up.entity_values[KEY_ACCELERATION_X].native_value == -7.02  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Y].native_value == 6.39  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Z].native_value == -2.51  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value == 9.82  # m/s^2


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


def test_parsing_v5_invalid_acceleration():
    """
    Test that invalid acceleration values are handled correctly (any component
    being invalid invalidates all acceleration values, including the total).
    """
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V5_OUTDOOR_SENSOR_DATA_INVALID_ACCEL)
    up = device.update(advertisement)
    assert up.entity_values[KEY_ACCELERATION_X].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Y].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Z].native_value is None
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value is None
