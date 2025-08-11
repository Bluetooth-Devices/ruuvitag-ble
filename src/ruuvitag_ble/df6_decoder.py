"""
Decoder for RuuviTag Data Format 6 data.

Based on https://github.com/ruuvi/ruuvi.endpoints.c/blob/f16619cc2/src/ruuvi_endpoint_6.c
         https://github.com/ruuvi/ruuvi.endpoints.c/blob/f16619cc2/src/ruuvi_endpoint_6.h
"""

from __future__ import annotations

import math
import struct

# See https://github.com/ruuvi/ruuvi.endpoints.c/blob/f16619cc2/src/ruuvi_endpoint_6.h#L58
LUX_LOG_SCALE = math.log(65536) / 254.0


class DataFormat6Decoder:
    def __init__(self, raw_data: bytes) -> None:
        if (data_len := len(raw_data)) < 20:
            raise ValueError(
                f"Data must be at least 20 bytes long for data format 6, got {data_len} bytes",
            )
        # Format: header(B), temp(h), humidity(H), pressure(H), pm25(H), co2(H), voc(B), nox(B), lumi(B), sound(B), seq(B), flags(B), mac(3B)
        # Cutting to 20 bytes since the advertisement may contain more data, and `struct.unpack` expects a fixed size.
        self.data: tuple[int, ...] = struct.unpack(">BhHHHHBBBBBB3B", raw_data[:20])
        if self.data[0] != 0x06:
            raise ValueError(f"Invalid data format: {self.data[0]} (expected 0x06)")

    @property
    def temperature_celsius(self) -> float | None:
        if self.data[1] == -32768:
            return None
        return round(self.data[1] / 200.0, 2)

    @property
    def humidity_percentage(self) -> float | None:
        if self.data[2] == 65535:
            return None
        return round(self.data[2] / 400.0, 2)

    @property
    def pressure_hpa(self) -> float | None:
        if self.data[3] == 0xFFFF:
            return None
        return round((self.data[3] + 50000) / 100, 2)

    @property
    def pm25_ug_m3(self) -> float | None:
        if self.data[4] == 0xFFFF:
            return None
        return round(self.data[4] / 10.0, 2)

    @property
    def co2_ppm(self) -> int | None:
        if self.data[5] == 0xFFFF:
            return None
        return self.data[5]

    @property
    def voc_index(self) -> int | None:
        val = self.data[6] << 1
        if self.data[11] & 64:  # (1 << 6)
            val |= 1
        if val == 0x1FF:
            return None
        return int(val)

    @property
    def nox_index(self) -> int | None:
        val = self.data[7] << 1
        if self.data[11] & 128:  # (1 << 7)
            val |= 1
        if val == 0x1FF:
            return None
        return int(val)

    @property
    def luminosity_lux(self) -> int | None:
        if self.data[8] == 0xFF:
            return None
        if self.data[8] == 0:
            return 0
        return int(round(math.exp(self.data[8] * LUX_LOG_SCALE) - 1))

    @property
    def sound_avg_dba(self) -> float | None:
        val = self.data[9] << 1
        if self.data[11] & 16:  # (1 << 4)
            val |= 1
        if val == 0x1FF:
            return None
        return round(val / 5 + 18, 2)

    @property
    def measurement_sequence_number(self) -> int:
        return self.data[10]

    @property
    def mac(self) -> str:
        return ":".join(f"{x:02X}" for x in self.data[12:15])
