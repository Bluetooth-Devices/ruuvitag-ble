import pytest

from ruuvitag_ble import RuuvitagBluetoothDeviceData
from ruuvitag_ble.dfe1_decoder import DataFormatE1Decoder
from tests.utils import (
    KEY_CO2,
    KEY_HUMIDITY,
    KEY_ILLUMINANCE,
    KEY_NOX_INDEX,
    KEY_PM25,
    KEY_PRESSURE,
    KEY_TEMPERATURE,
    KEY_VOC_INDEX,
    bytes_to_service_info,
)

# Test vectors from https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-e1.md
# Note: The "XXXXXX" in the raw data represents reserved fields that we can set to 0x00
# The flags byte (index 28) has bit 0 set for calibration in progress
E1_VALID_DATA = bytes.fromhex(
    "E1170C5668C79E0065007004BD11CA00C90A0213E0AC000000DECDEE110000000000CBB8334C884F",
)
E1_MAX_VALUES = bytes.fromhex(
    "E17FFF9C40FFFE27102710271027109C40FAFADC28F0000000FFFFFE3F0000000000CBB8334C884F",
)
E1_MIN_VALUES = bytes.fromhex(
    "E1800100000000000000000000000000000000000000000000000000000000000000CBB8334C884F",
)
E1_INVALID_VALUES = bytes.fromhex(
    "E18000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
)


def test_parsing_e1_valid_data():
    """Test parsing E1 format with valid sensor data."""
    p = DataFormatE1Decoder(E1_VALID_DATA)
    assert p.temperature_celsius == 29.500
    assert p.humidity_percentage == 55.300
    assert p.pressure_hpa == 1011.02
    assert p.pm1_ug_m3 == 10.1
    assert p.pm25_ug_m3 == 11.2
    assert p.pm4_ug_m3 == 121.3
    assert p.pm10_ug_m3 == 455.4
    assert p.co2_ppm == 201
    assert p.voc_index == 20
    assert p.nox_index == 4
    assert p.luminosity_lux == 13027.00
    assert p.measurement_sequence_number == 14601710
    assert p.calibration_in_progress
    assert p.mac == "CB:B8:33:4C:88:4F"


def test_parsing_e1_max_values():
    """Test parsing E1 format with maximum values."""
    p = DataFormatE1Decoder(E1_MAX_VALUES)
    assert p.temperature_celsius == 163.835
    assert p.humidity_percentage == 100.000
    assert p.pressure_hpa == 1155.34
    assert p.pm1_ug_m3 == 1000.0
    assert p.pm25_ug_m3 == 1000.0
    assert p.pm4_ug_m3 == 1000.0
    assert p.pm10_ug_m3 == 1000.0
    assert p.co2_ppm == 40000
    assert p.voc_index == 500
    assert p.nox_index == 500
    assert p.luminosity_lux == 144284.00
    assert p.measurement_sequence_number == 16777214
    assert p.mac == "CB:B8:33:4C:88:4F"


def test_parsing_e1_min_values():
    """Test parsing E1 format with minimum values."""
    p = DataFormatE1Decoder(E1_MIN_VALUES)
    assert p.temperature_celsius == pytest.approx(-163.835, abs=0.001)
    assert p.humidity_percentage == 0.000
    assert p.pressure_hpa == 500.00
    assert p.pm1_ug_m3 == 0.0
    assert p.pm25_ug_m3 == 0.0
    assert p.pm4_ug_m3 == 0.0
    assert p.pm10_ug_m3 == 0.0
    assert p.co2_ppm == 0
    assert p.voc_index == 0
    assert p.nox_index == 0
    assert p.luminosity_lux == 0.00
    assert p.measurement_sequence_number == 0
    assert not p.calibration_in_progress
    assert p.mac == "CB:B8:33:4C:88:4F"


def test_parsing_e1_invalid_values():
    """Test parsing E1 format with invalid/NaN values."""
    p = DataFormatE1Decoder(E1_INVALID_VALUES)
    assert p.temperature_celsius is None
    assert p.humidity_percentage is None
    assert p.pressure_hpa is None
    assert p.pm1_ug_m3 is None
    assert p.pm25_ug_m3 is None
    assert p.pm4_ug_m3 is None
    assert p.pm10_ug_m3 is None
    assert p.co2_ppm is None
    assert p.voc_index is None
    assert p.nox_index is None
    assert p.luminosity_lux is None
    assert p.measurement_sequence_number is None
    assert p.mac == "FF:FF:FF:FF:FF:FF"


def test_parsing_e1_via_bluetooth_device_data():
    """Test parsing E1 format through the BluetoothDeviceData interface."""
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(E1_VALID_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    assert "884F" in str(up.devices[None].name)
    v = up.entity_values
    assert v[KEY_TEMPERATURE].native_value == 29.500
    assert v[KEY_HUMIDITY].native_value == 55.300
    assert v[KEY_PRESSURE].native_value == 1011.02
    assert v[KEY_PM25].native_value == 11.2
    assert v[KEY_CO2].native_value == 201
    assert v[KEY_VOC_INDEX].native_value == 20
    assert v[KEY_NOX_INDEX].native_value == 4
    assert v[KEY_ILLUMINANCE].native_value == 13027.00


def test_bad_data():
    with pytest.raises(ValueError):
        DataFormatE1Decoder(bytes.fromhex("E114"))
    with pytest.raises(ValueError):
        DataFormatE1Decoder(bytes.fromhex("06" + "00" * 39))
