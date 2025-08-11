import pytest

from ruuvitag_ble import RuuvitagBluetoothDeviceData
from ruuvitag_ble.df6_decoder import DataFormat6Decoder
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

# Test vectors from DF6 sensor data
V6_BASELINE_SENSOR_DATA = bytes.fromhex("06144E40F8C915000602193200A34BBDC0FF00FF")  # fmt: skip
V6_BREATH_HIGH_CO2_DATA = bytes.fromhex("0614DA863CC90300090DF9A600A057F690FF00FF")  # fmt: skip
V6_BREATH_LOWER_CO2_DATA = bytes.fromhex("0615113E08C9030007057B3E00A44D6290FF00FF")  # fmt: skip
V6_LOW_LUMINOSITY_DATA = bytes.fromhex("0614974158C9110005020C56007C4B9580FF00FF")  # fmt: skip
V6_C_TEST_DATA = bytes.fromhex("06170C5668C79E007000C90501D94ACD004C884F")  # fmt: skip


def test_parsing_v6_baseline():
    """Test parsing DF6 baseline sensor data."""
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V6_BASELINE_SENSOR_DATA)
    assert device.supported(advertisement)
    up = device.update(advertisement)
    expected_name = "RuuviTag 00FF"
    assert up.devices[None].name == expected_name  # Parsed from advertisement
    v = up.entity_values
    assert v[KEY_CO2].native_value == 537  # ppm
    assert v[KEY_HUMIDITY].native_value == 41.58  # %
    assert v[KEY_ILLUMINANCE].native_value == 1232  # lux
    assert v[KEY_NOX_INDEX].native_value == 1  # index
    assert v[KEY_PM25].native_value == 0.6  # μg/m³
    assert v[KEY_PRESSURE].native_value == 1014.77  # hPa
    assert v[KEY_TEMPERATURE].native_value == 25.99  # Celsius
    assert v[KEY_VOC_INDEX].native_value == 101.0  # index


def test_parsing_v6_breath_high_co2():
    """Test parsing DF6 data with elevated CO2 from breath."""
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V6_BREATH_HIGH_CO2_DATA)
    v = device.update(advertisement).entity_values
    assert v[KEY_CO2].native_value == 3577  # ppm (elevated from breath)
    assert v[KEY_HUMIDITY].native_value == 85.91  # %
    assert v[KEY_ILLUMINANCE].native_value == 1080  # lux
    assert v[KEY_NOX_INDEX].native_value == 1  # index
    assert v[KEY_PM25].native_value == 0.9  # μg/m³
    assert v[KEY_PRESSURE].native_value == 1014.59  # hPa
    assert v[KEY_TEMPERATURE].native_value == 26.69  # Celsius
    assert v[KEY_VOC_INDEX].native_value == 332  # index (elevated from breath)


def test_parsing_v6_breath_lower_co2():
    """Test parsing DF6 data with lower CO2 from breath test."""
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V6_BREATH_LOWER_CO2_DATA)
    v = device.update(advertisement).entity_values
    assert v[KEY_CO2].native_value == 1403  # ppm (lower CO2 than first breath test)
    assert v[KEY_HUMIDITY].native_value == 39.7  # %
    assert v[KEY_ILLUMINANCE].native_value == 1287  # lux
    assert v[KEY_NOX_INDEX].native_value == 1  # index
    assert v[KEY_PM25].native_value == 0.7  # μg/m³
    assert v[KEY_PRESSURE].native_value == 1014.59  # hPa
    assert v[KEY_TEMPERATURE].native_value == 26.96  # Celsius
    assert v[KEY_VOC_INDEX].native_value == 124  # index (lower than first breath test)


def test_parsing_v6_low_luminosity():
    """Test parsing DF6 data with low luminosity conditions."""
    device = RuuvitagBluetoothDeviceData()
    advertisement = bytes_to_service_info(V6_LOW_LUMINOSITY_DATA)
    v = device.update(advertisement).entity_values
    assert v[KEY_ILLUMINANCE].native_value == 224  # lux (low light conditions)


def test_parsing_c_data():
    # See https://github.com/ruuvi/ruuvi.endpoints.c/blob/f16619cc261ec/test/test_ruuvi_endpoint_6.c#L33
    p = DataFormat6Decoder(V6_C_TEST_DATA)
    assert p.temperature_celsius == 29.5
    assert p.humidity_percentage == 55.3
    assert p.pressure_hpa == 1011.02
    assert p.pm25_ug_m3 == 11.2
    assert p.co2_ppm == 201
    assert p.voc_index == 10
    assert p.nox_index == 2
    assert p.luminosity_lux == 13027
    assert p.sound_avg_dba == 47.6
    assert p.measurement_sequence_number == 205
    assert p.mac == "4C:88:4F"


def test_parsing_v6_invalid_data():
    """Test parsing DF6 data with invalid/NaN values."""
    # Based on test_ruuvi_endpoint_6_get_invalid_data
    invalid_data = bytes.fromhex("068000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
    p = DataFormat6Decoder(invalid_data)
    # Temperature should be NaN (0x8000 represents invalid temperature)
    # Most other values should be invalid (0xFFFF or 0xFF patterns)
    assert p.temperature_celsius is None
    assert p.sound_avg_dba is None
    assert p.humidity_percentage is None
    assert p.pressure_hpa is None
    assert p.pm25_ug_m3 is None
    assert p.co2_ppm is None
    assert p.voc_index is None
    assert p.nox_index is None
    assert p.luminosity_lux is None
    assert p.measurement_sequence_number == 255
    assert p.mac == "FF:FF:FF"


def test_parsing_v6_underflow():
    """Test parsing DF6 data with underflow values that get clamped to minimum."""
    # Based on test_ruuvi_endpoint_6_underflow
    # Values below minimum should be clamped to minimum valid values
    underflow_data = bytes.fromhex("0680010000000000000000000000000000000000")
    p = DataFormat6Decoder(underflow_data)
    # These should be clamped to minimum valid values
    assert p.temperature_celsius == pytest.approx(-163.835, abs=0.01)  # Min temperature
    assert p.humidity_percentage == 0.0  # Min humidity
    assert p.pressure_hpa == 500.0  # Min pressure
    assert p.pm25_ug_m3 == 0.0  # Min PM2.5
    assert p.co2_ppm == 0  # Min CO2
    assert p.voc_index == 0  # Min VOC
    assert p.nox_index == 0  # Min NOx
    assert p.luminosity_lux == 0  # Min luminosity
    assert p.sound_avg_dba == 18.0  # Min sound
    assert p.measurement_sequence_number == 0
    assert p.mac == "00:00:00"


def test_parsing_v6_overflow():
    """Test parsing DF6 data with overflow values that get clamped to maximum."""
    overflow_data = bytes.fromhex("067FFF9C40FFFE27109C40FAFAFEFEFF07FFFFFF")
    p = DataFormat6Decoder(overflow_data)
    # These should be clamped to maximum valid values
    assert p.temperature_celsius == pytest.approx(163.835, abs=0.01)  # Max temperature
    assert p.humidity_percentage == 100.0  # Max humidity
    assert p.pressure_hpa == pytest.approx(1155.34, abs=0.01)  # Max pressure
    assert p.pm25_ug_m3 == pytest.approx(1000.0, abs=0.01)  # Max PM2.5
    assert p.co2_ppm == 40000  # Max CO2
    assert p.voc_index == 500  # Max VOC
    assert p.nox_index == 500  # Max NOx
    assert p.luminosity_lux == 65535  # Max luminosity
    assert p.sound_avg_dba == 119.6  # Max sound (120 in C version)
    assert p.measurement_sequence_number == 255
    assert p.mac == "FF:FF:FF"


def test_bad_data():
    with pytest.raises(ValueError):
        DataFormat6Decoder(bytes.fromhex("0614"))
    with pytest.raises(ValueError):
        DataFormat6Decoder(bytes.fromhex("07" * 20))
