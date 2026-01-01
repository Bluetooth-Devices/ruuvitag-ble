from ruuvitag_ble.parser import calculate_iaqs


def test_ruuvi_iaqs_calculation():
    """Test calculation of Ruuvi indoor air quality score (IAQS)."""
    assert calculate_iaqs(None, 0) is None
    assert calculate_iaqs(0, None) is None
    assert calculate_iaqs(500, 0.4) == 96
