import pytest
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, DeviceKey

from ruuvitag_ble import RuuvitagBluetoothDeviceData

V5_SENSOR_DATA = (
    b"\x05\x05\xa0`\xa0\xc8\x9a\xfd4\x02\x8c\xff\x00cvriv\xde\xad{?\xef\xaf"
)
V3_SENSOR_DATA = b"\x03\xb2\x0c\x1f\xca \x00z\x00&\x03\xd0\x08\x8f"
V5_SENSOR_DATA_SHORT = (
    b"\x05\x05\xa0`\xa0\xc8\x9a\xfd4\x02\x8c\xff\x00cvriv\xde\xad{?\xef"
)
V3_SENSOR_DATA_SHORT = b"\x03\xb2\x0c\x1f\xca \x00z\x00&\x03\xd0\x08"
V5_SENSOR_DATA_ERROR = b"\x05\x80\x00\xff\xff\xff\xff\x80\x00\x80\x00\x80\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
V3_SENSOR_DATA_ERROR = b"\x03\xff\x80\xff\xff\xff\x80\x00\x80\x00\x80\x00\xff\xff"
INVALID_FORMAT_ERROR = b"\x02\xb2\x0c\x1f\xca \x00z\x00&\x03\xd0\x08\x8f"

KEY_TEMPERATURE = DeviceKey(key=DeviceClass.TEMPERATURE, device_id=None)
KEY_HUMIDITY = DeviceKey(key=DeviceClass.HUMIDITY, device_id=None)
KEY_PRESSURE = DeviceKey(key=DeviceClass.PRESSURE, device_id=None)
KEY_VOLTAGE = DeviceKey(key=DeviceClass.VOLTAGE, device_id=None)
KEY_MOVEMENT = DeviceKey(key="movement_counter", device_id=None)
KEY_TX_POWER = DeviceKey(key="tx_power", device_id=None)
KEY_SEQUENCE_NUMBER = DeviceKey(key="measurement_sequence_number", device_id=None)
KEY_ACCELERATION_X = DeviceKey(key="acceleration_x", device_id=None)
KEY_ACCELERATION_Y = DeviceKey(key="acceleration_y", device_id=None)
KEY_ACCELERATION_Z = DeviceKey(key="acceleration_z", device_id=None)
KEY_ACCELERATION_TOTAL = DeviceKey(key="acceleration_total", device_id=None)


def bytes_to_service_info(payload: bytes) -> BluetoothServiceInfo:
    return BluetoothServiceInfo(
        name="Test",
        address="AB:CD:EF:BA:DC:FE",
        rssi=-60,
        manufacturer_data={1177: payload},
        service_data={},
        service_uuids=[],
        source="",
    )


def bytes_to_service_info_wrong_mfr(payload: bytes) -> BluetoothServiceInfo:
    return BluetoothServiceInfo(
        name="Test",
        address="AB:CD:EF:BA:DC:FE",
        rssi=-60,
        manufacturer_data={1234: payload},
        service_data={},
        service_uuids=[],
        source="",
    )


def test_parsing_v5():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V5_SENSOR_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag DCFE"
    assert up.devices[None].name == expected_name  # Parsed from advertisement
    assert up.entity_values[KEY_TEMPERATURE].native_value == 7.2  # Celsius
    assert up.entity_values[KEY_HUMIDITY].native_value == 61.84  # %
    assert up.entity_values[KEY_PRESSURE].native_value == 1013.54  # hPa
    assert up.entity_values[KEY_VOLTAGE].native_value == 2395  # mV
    assert up.entity_values[KEY_MOVEMENT].native_value == 114  # count
    assert up.entity_values[KEY_TX_POWER].native_value == 4  # dBm
    assert up.entity_values[KEY_SEQUENCE_NUMBER].native_value == 0  # count
    assert up.entity_values[KEY_ACCELERATION_X].native_value == -7.02  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Y].native_value == 6.39  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Z].native_value == -2.51  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value == 9.82  # m/s^2


def test_error_v5():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V5_SENSOR_DATA_ERROR)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag DCFE"
    assert up.devices[None].name == expected_name  # Parsed from advertisement
    assert up.entity_values[KEY_TEMPERATURE].native_value is None
    assert up.entity_values[KEY_HUMIDITY].native_value is None
    assert up.entity_values[KEY_PRESSURE].native_value is None
    assert up.entity_values[KEY_VOLTAGE].native_value is None
    assert up.entity_values[KEY_TX_POWER].native_value is None
    assert up.entity_values[KEY_ACCELERATION_X].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Y].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Z].native_value is None
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value is None
    advertisement = bytes_to_service_info(V5_SENSOR_DATA_SHORT)
    with pytest.raises(ValueError):
        device.update(advertisement)


def test_parsing_v3():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V3_SENSOR_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag DCFE"
    assert up.devices[None].name == expected_name
    assert up.entity_values[KEY_TEMPERATURE].native_value == 12.31  # Celsius
    assert up.entity_values[KEY_HUMIDITY].native_value == 89.0  # %
    assert up.entity_values[KEY_PRESSURE].native_value == 1017.44  # hPa
    assert up.entity_values[KEY_VOLTAGE].native_value == 2191  # mV
    assert up.entity_values[KEY_ACCELERATION_X].native_value == 1.2  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Y].native_value == 0.37  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_Z].native_value == 9.56  # m/s^2
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value == 9.65  # m/s^2


def test_error_v3():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V3_SENSOR_DATA_ERROR)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag DCFE"
    assert up.devices[None].name == expected_name  # Parsed from advertisement
    assert up.entity_values[KEY_TEMPERATURE].native_value is None
    assert up.entity_values[KEY_HUMIDITY].native_value is None
    assert up.entity_values[KEY_ACCELERATION_X].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Y].native_value is None
    assert up.entity_values[KEY_ACCELERATION_Z].native_value is None
    assert up.entity_values[KEY_ACCELERATION_TOTAL].native_value is None
    advertisement = bytes_to_service_info(V3_SENSOR_DATA_SHORT)
    with pytest.raises(ValueError):
        device.update(advertisement)


def test_wrong_mfr():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info_wrong_mfr(V3_SENSOR_DATA_ERROR)
    up = device.update(advertisement)
    assert not up.entity_values


def test_invalid_format():
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(INVALID_FORMAT_ERROR)
    up = device.update(advertisement)
    assert not up.entity_values
