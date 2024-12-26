"""
Decoder for RuuviTag Data Format 3 data.

Ruuvi Sensor Protocols: https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_03.md
"""

from __future__ import annotations

import math
import struct


class DataFormat3Decoder:
    def __init__(self, raw_data: bytes) -> None:
        if len(raw_data) < 14:
            raise ValueError("Data must be at least 14 bytes long for data format 3")
        self.data: tuple[int, ...] = struct.unpack(">BBbBHhhhH", raw_data)

    @property
    def humidity_percentage(self) -> float | None:
        if self.data[1] > 200:
            return None
        return round(self.data[1] / 2, 2)

    @property
    def temperature_celsius(self) -> float | None:
        return round(self.data[2] + self.data[3] / 100.0, 2)

    @property
    def pressure_hpa(self) -> float | None:
        if self.data[3] == 0xFFFF:
            return None

        return round((self.data[4] + 50000) / 100, 2)

    @property
    def acceleration_vector_mg(self) -> tuple[int, int, int] | tuple[None, None, None]:
        ax = self.data[5]
        ay = self.data[6]
        az = self.data[7]
        if ax == -32768 or ay == -32768 or az == -32768:
            return (None, None, None)

        return (ax, ay, az)

    @property
    def acceleration_total_mss(self) -> float | None:
        ax, ay, az = self.acceleration_vector_mg
        if ax is None or ay is None or az is None:
            return None
        # Conversion from milliG to m/s^2
        return math.sqrt(ax * ax + ay * ay + az * az) / 1000.0 * 9.8

    @property
    def battery_voltage_mv(self) -> int | None:
        return self.data[8]
