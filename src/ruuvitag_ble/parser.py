from __future__ import annotations

import logging
import math

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, Units

from ruuvitag_ble.df3_decoder import DataFormat3Decoder
from ruuvitag_ble.df5_decoder import DataFormat5Decoder
from ruuvitag_ble.df6_decoder import DataFormat6Decoder
from ruuvitag_ble.dfe1_decoder import DataFormatE1Decoder

_LOGGER = logging.getLogger(__name__)

decoder_classes: dict[
    int,
    type[
        DataFormat3Decoder
        | DataFormat5Decoder
        | DataFormat6Decoder
        | DataFormatE1Decoder
    ],
] = {
    0x03: DataFormat3Decoder,
    0x05: DataFormat5Decoder,
    0x06: DataFormat6Decoder,
    0xE1: DataFormatE1Decoder,
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
            decoder_cls = decoder_classes[data_format]
        except KeyError:
            _LOGGER.debug("Data format not supported: %s", raw_data)
            return
        decoder = decoder_cls(raw_data)

        # Compute short identifier from MAC address
        # (preferring the MAC address the tag broadcasts).
        identifier = short_address(decoder.mac or service_info.address)
        dev_type = "Ruuvi Air" if "Air" in str(service_info.name) else "RuuviTag"
        self.set_device_type(dev_type)
        self.set_device_manufacturer("Ruuvi Innovations Ltd.")
        self.set_device_name(f"{dev_type} {identifier}")

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
        if hasattr(decoder, "battery_voltage_mv"):
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

        if hasattr(decoder, "pm1_ug_m3"):
            self.update_sensor(
                key=DeviceClass.PM1,
                device_class=DeviceClass.PM1,
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                native_value=decoder.pm1_ug_m3,
            )

        if hasattr(decoder, "pm25_ug_m3"):
            self.update_sensor(
                key=DeviceClass.PM25,
                device_class=DeviceClass.PM25,
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                native_value=decoder.pm25_ug_m3,
            )

        if hasattr(decoder, "pm4_ug_m3"):
            self.update_sensor(
                key="pm4",
                device_class=None,  # TODO: DeviceClass.PM4 isn't a thing...
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                native_value=decoder.pm4_ug_m3,
            )

        if hasattr(decoder, "pm10_ug_m3"):
            self.update_sensor(
                key=DeviceClass.PM10,
                device_class=DeviceClass.PM10,
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                native_value=decoder.pm10_ug_m3,
            )

        if hasattr(decoder, "co2_ppm"):
            self.update_sensor(
                key=DeviceClass.CO2,
                device_class=DeviceClass.CO2,
                native_unit_of_measurement=Units.CONCENTRATION_PARTS_PER_MILLION,
                native_value=decoder.co2_ppm,
            )

        if hasattr(decoder, "voc_index"):
            self.update_sensor(
                key="voc_index",
                device_class=DeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                native_unit_of_measurement=None,
                native_value=decoder.voc_index,
            )

        if hasattr(decoder, "nox_index"):
            self.update_sensor(
                key="nox_index",
                device_class=DeviceClass.NITROGEN_MONOXIDE,
                native_unit_of_measurement=None,
                native_value=decoder.nox_index,
            )

        if hasattr(decoder, "luminosity_lux"):
            self.update_sensor(
                key=DeviceClass.ILLUMINANCE,
                device_class=DeviceClass.ILLUMINANCE,
                native_unit_of_measurement=Units.LIGHT_LUX,
                native_value=decoder.luminosity_lux,
            )

        if hasattr(decoder, "acceleration_vector_mg"):
            self._update_acceleration(decoder)  # type: ignore[arg-type]

    def _update_acceleration(
        self,
        decoder: DataFormat3Decoder | DataFormat5Decoder,
    ) -> None:
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
