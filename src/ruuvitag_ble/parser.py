from __future__ import annotations

import logging

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, Units

from ruuvitag_ble.df3_decoder import DataFormat3Decoder
from ruuvitag_ble.df5_decoder import DataFormat5Decoder

_LOGGER = logging.getLogger(__name__)

decoder_classes: dict[
    int,
    type[DataFormat3Decoder | DataFormat5Decoder],
] = {
    0x03: DataFormat3Decoder,
    0x05: DataFormat5Decoder,
}


class RuuvitagBluetoothDeviceData(BluetoothData):
    """Data for Ruuvitag BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        try:
            raw_data = service_info.manufacturer_data[0x0499]
        except (KeyError, IndexError):
            _LOGGER.debug("Manufacturer ID 0x0499 not found in data")
            return None

        data_format = raw_data[0]
        try:
            decoder_cls: type[DataFormat3Decoder | DataFormat5Decoder] = (
                decoder_classes[data_format]
            )
        except KeyError:
            _LOGGER.debug("Data format not supported: %s", raw_data)
            return
        decoder = decoder_cls(raw_data)

        # Compute short identifier from MAC address
        identifier = short_address(service_info.address)
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
        self.update_sensor(
            key="acceleration_x",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=decoder.acceleration_x_mss,
        )
        self.update_sensor(
            key="acceleration_y",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=decoder.acceleration_y_mss,
        )
        self.update_sensor(
            key="acceleration_z",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=decoder.acceleration_z_mss,
        )
        self.update_sensor(
            key="acceleration_total",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=decoder.acceleration_total_mss,
        )

        if hasattr(decoder, "movement_counter"):
            self.update_sensor(
                key="movement_counter",
                device_class=DeviceClass.COUNT,
                native_unit_of_measurement=None,
                native_value=decoder.movement_counter,
            )

        if hasattr(decoder, "tx_power_dbm"):
            self.update_sensor(
                key="tx_power",
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                native_value=decoder.tx_power_dbm,
            )

        if hasattr(decoder, "measurement_sequence_number"):
            self.update_sensor(
                key="measurement_sequence_number",
                device_class=DeviceClass.COUNT,
                native_unit_of_measurement=None,
                native_value=decoder.measurement_sequence_number,
            )
