"""
Decoder for RuuviTag Data Format 5 data.

Based on https://github.com/ttu/ruuvitag-sensor/blob/23e6555/ruuvitag_sensor/decoder.py (MIT Licensed)
Ruuvi Sensor Protocols: https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md
"""

from __future__ import annotations

import math
import struct


class DataFormat5Decoder:
    def __init__(self, raw_data: bytes) -> None:
        if len(raw_data) < 24:
            raise ValueError("Data must be at least 24 bytes long for data format 5")
        self.data: tuple[int, ...] = struct.unpack(">BhHHhhhHBH6B", raw_data)

    @property
    def temperature_celsius(self) -> float | None:
        if self.data[1] == -32768:
            return None
        return round(self.data[1] / 200.0, 2)

    @property
    def humidity_percentage(self) -> float | None:
        if self.data[2] == 65535:
            return None
        return round(self.data[2] / 400, 2)

    @property
    def pressure_hpa(self) -> float | None:
        if self.data[3] == 0xFFFF:
            return None
        return round((self.data[3] + 50000) / 100, 2)

    @property
    def acceleration_vector_mg(self) -> tuple[int, int, int] | tuple[None, None, None]:
        ax = self.data[4]
        ay = self.data[5]
        az = self.data[6]
        if ax == -32768 or ay == -32768 or az == -32768:
            return (None, None, None)
        return (ax, ay, az)

    @property
    def acceleration_x_mss(self) -> float | None:
        ax = self.data[4]
        if ax == -32768:
            return None
        return round(ax / 1000.0 * 9.8, 2)

    @property
    def acceleration_y_mss(self) -> float | None:
        ay = self.data[5]
        if ay == -32768:
            return None
        return round(ay / 1000.0 * 9.8, 2)

    @property
    def acceleration_z_mss(self) -> float | None:
        az = self.data[6]
        if az == -32768:
            return None
        return round(az / 1000.0 * 9.8, 2)

    @property
    def acceleration_total_mss(self) -> float | None:
        ax, ay, az = self.acceleration_vector_mg
        if ax is None or ay is None or az is None:
            return None
        # Conversion to m/s^2
        return round(math.sqrt(ax * ax + ay * ay + az * az) / 1000.0 * 9.8, 2)

    @property
    def battery_voltage_mv(self) -> int | None:
        voltage = self.data[7] >> 5
        if voltage == 2047:  # invalid per spec
            return None
        return voltage + 1600

    @property
    def tx_power_dbm(self) -> int | None:
        tx_power = self.data[7] & 0x001F
        if tx_power == 31:  # invalid per spec
            return None
        return -40 + (tx_power * 2)

    @property
    def movement_counter(self) -> int:
        return self.data[8]

    @property
    def measurement_sequence_number(self) -> int:
        return self.data[9]
