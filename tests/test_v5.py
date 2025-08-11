from ruuvitag_ble import RuuvitagBluetoothDeviceData
from tests.utils import (
    KEY_ACCELERATION_TOTAL,
    KEY_ACCELERATION_X,
    KEY_ACCELERATION_Y,
    KEY_ACCELERATION_Z,
    KEY_HUMIDITY,
    KEY_MOVEMENT,
    KEY_PRESSURE,
    KEY_TEMPERATURE,
    KEY_VOLTAGE,
    bytes_to_service_info,
)

# INDOOR_SENSOR_DATA = bytes.fromhex("050ea44d7ec818fcbcfdf0ffb42bf600103cd9370ff7aa48")  # fmt: skip
V5_OUTDOOR_SENSOR_DATA = bytes.fromhex("0505a060a0c89afd34028cff006376726976dead7b3fefaf")  # fmt: skip
V5_OUTDOOR_SENSOR_DATA_INVALID_ACCEL = bytes.fromhex("0505a060a0c89a8000028cff006376726976dead7b3fefaf")  # fmt: skip


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
