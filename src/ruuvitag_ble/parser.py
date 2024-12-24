from __future__ import annotations

import logging

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, Units

from ruuvitag_ble.df3_decoder import DataFormat3Decoder
from ruuvitag_ble.df5_decoder import DataFormat5Decoder

_LOGGER = logging.getLogger(__name__)


class RuuvitagBluetoothDeviceData(BluetoothData):
    """Data for Ruuvitag BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        try:
            raw_data = service_info.manufacturer_data[0x0499]
        except (KeyError, IndexError):
            _LOGGER.debug("Manufacturer ID 0x0499 not found in data")
            return None

        data_format = raw_data[0]
        if data_format not in (0x03, 0x05):
            _LOGGER.debug("Data format not supported: %s", raw_data)
            return

        decoder_classes = {
            0x03: DataFormat3Decoder,
            0x05: DataFormat5Decoder,
        }

        decoder = decoder_classes.get(data_format, DataFormat5Decoder)(raw_data)

        # Compute short identifier from MAC address
        # (preferring the MAC address the tag broadcasts).
        identifier = short_address(decoder.mac or service_info.address)
        self.set_device_type("RuuviTag")
        self.set_device_manufacturer("Ruuvi Innovations Ltd.")
        self.set_device_name(f"RuuviTag {identifier}")

        self.update_sensor(
            key=DeviceClass.TEMPERATURE,
            device_class=DeviceClass.TEMPERATURE,
            native_unit_of_measurement=Units.TEMP_CELSIUS,
            native_value=decoder.temperature_celsius,
        )
        self.update_sensor(
            key=DeviceClass.HUMIDITY,
            device_class=DeviceClass.HUMIDITY,
            native_unit_of_measurement=Units.PERCENTAGE,
            native_value=decoder.humidity_percentage,
        )
        self.update_sensor(
            key=DeviceClass.PRESSURE,
            device_class=DeviceClass.PRESSURE,
            native_unit_of_measurement=Units.PRESSURE_HPA,
            native_value=decoder.pressure_hpa,
        )
        self.update_sensor(
            key=DeviceClass.VOLTAGE,
            device_class=DeviceClass.VOLTAGE,
            native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_MILLIVOLT,
            native_value=decoder.battery_voltage_mv,
        )

        if data_format == 0x05:
            self.update_sensor(
                key="movement_counter",
                device_class=DeviceClass.COUNT,
                native_unit_of_measurement=None,
                native_value=decoder.movement_counter,
            )
