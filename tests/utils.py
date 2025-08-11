from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, DeviceKey

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
