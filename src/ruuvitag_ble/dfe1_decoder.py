"""
Decoder for RuuviTag Data Format E1 (Extended v1) data.

Based on https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-e1.md
"""

from __future__ import annotations

import struct


class DataFormatE1Decoder:
    def __init__(self, raw_data: bytes) -> None:
        if (data_len := len(raw_data)) < 40:
            raise ValueError(
                f"Data must be at least 40 bytes long for data format E1, got {data_len} bytes",
            )
        # Format breakdown (40 bytes total):
        # 0: header(1B), 1-2: temp(2B), 3-4: humidity(2B), 5-6: pressure(2B),
        # 7-8: pm1(2B), 9-10: pm25(2B), 11-12: pm4(2B), 13-14: pm10(2B),
        # 15-16: co2(2B), 17: voc(1B), 18: nox(1B), 19-21: lumi(3B),
        # 22-24: reserved(3B), 25-27: seq(3B), 28: flags(1B), 29-33: reserved(5B), 34-39: mac(6B)
        self.data: tuple[int | bytes, ...] = struct.unpack(
            ">BhHHHHHHHBB3s3s3sB5s6s",
            raw_data[:40],
        )
        if self.data[0] != 0xE1:
            raise ValueError(
                f"Invalid data format: {int(self.data[0])} (expected 0xE1)",
            )
        self.flags = int(self.data[14])

    @property
    def temperature_celsius(self) -> float | None:
        if self.data[1] == -32768:
            return None
        return round(int(self.data[1]) * 0.005, 3)

    @property
    def humidity_percentage(self) -> float | None:
        if self.data[2] == 65535:
            return None
        return round(int(self.data[2]) * 0.0025, 3)

    @property
    def pressure_hpa(self) -> float | None:
        if self.data[3] == 0xFFFF:
            return None
        return round((int(self.data[3]) + 50000) / 100, 2)

    @property
    def pm1_ug_m3(self) -> float | None:
        if self.data[4] == 0xFFFF:
            return None
        return round(int(self.data[4]) * 0.1, 1)

    @property
    def pm25_ug_m3(self) -> float | None:
        if self.data[5] == 0xFFFF:
            return None
        return round(int(self.data[5]) * 0.1, 1)

    @property
    def pm4_ug_m3(self) -> float | None:
        if self.data[6] == 0xFFFF:
            return None
        return round(int(self.data[6]) * 0.1, 1)

    @property
    def pm10_ug_m3(self) -> float | None:
        if self.data[7] == 0xFFFF:
            return None
        return round(int(self.data[7]) * 0.1, 1)

    @property
    def co2_ppm(self) -> int | None:
        if self.data[8] == 0xFFFF:
            return None
        return int(self.data[8])

    @property
    def voc_index(self) -> int | None:
        # VOC is 9 bits: 8 bits in data[9], LSB in bit 6 of flags
        val = int(self.data[9]) << 1
        if self.flags & 64:  # bit 6 of flags
            val |= 1
        if val == 0x1FF:
            return None
        return int(val)

    @property
    def nox_index(self) -> int | None:
        # NOX is 9 bits: 8 bits in data[10], LSB in bit 7 of flags
        val = int(self.data[10]) << 1
        if self.flags & 128:  # bit 7 of flags
            val |= 1
        if val == 0x1FF:
            return None
        return int(val)

    @property
    def luminosity_lux(self) -> float | None:
        lumi_bytes = bytes(self.data[11])
        if lumi_bytes == b"\xff\xff\xff":
            return None
        lumi_val = int.from_bytes(lumi_bytes, byteorder="big")
        return round(lumi_val * 0.01, 2)

    @property
    def measurement_sequence_number(self) -> int | None:
        seq_bytes = bytes(self.data[13])
        if seq_bytes == b"\xff\xff\xff":
            return None
        return int.from_bytes(seq_bytes, byteorder="big")

    @property
    def calibration_in_progress(self) -> bool:
        # Bit 0 of flags indicates calibration status
        return bool(self.flags & 1)

    @property
    def mac(self) -> str:
        return ":".join(f"{b:02X}" for b in bytes(self.data[16]))
