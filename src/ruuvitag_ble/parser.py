from __future__ import annotations

import logging
import math

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

        if hasattr(decoder, "movement_counter"):
            self.update_sensor(
                key="movement_counter",
                device_class=DeviceClass.COUNT,
                native_unit_of_measurement=None,
                native_value=decoder.movement_counter,
            )

        try:
            acc_x_mg, acc_y_mg, acc_z_mg = decoder.acceleration_vector_mg
            # Typing ignores are used here, as the arising TypeErrors
            # will be caught at runtime (IOW, we don't waste runtime doing
            # unlikely type checks).
            acc_x_mss = round(acc_x_mg * 0.00980665, 2)  # type: ignore
            acc_y_mss = round(acc_y_mg * 0.00980665, 2)  # type: ignore
            acc_z_mss = round(acc_z_mg * 0.00980665, 2)  # type: ignore
            acc_total_mss = round(
                math.hypot(acc_x_mss, acc_y_mss, acc_z_mss),
                2,
            )
        except TypeError:  # When any of the acceleration values are None (unlikely)
            acc_total_mss = acc_x_mss = acc_y_mss = acc_z_mss = None  # type: ignore

        self.update_sensor(
            key="acceleration_x",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=acc_x_mss,
        )
        self.update_sensor(
            key="acceleration_y",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=acc_y_mss,
        )
        self.update_sensor(
            key="acceleration_z",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=acc_z_mss,
        )
        self.update_sensor(
            key="acceleration_total",
            device_class=DeviceClass.ACCELERATION,
            native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            native_value=acc_total_mss,
        )
