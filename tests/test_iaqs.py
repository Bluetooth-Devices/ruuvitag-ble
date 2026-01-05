from ruuvitag_ble.iaqs import calculate_iaqs


def test_ruuvi_iaqs_calculation():
    """Test calculation of Ruuvi indoor air quality score (IAQS)."""
    assert calculate_iaqs(None, 0) is None
    assert calculate_iaqs(0, None) is None
    assert calculate_iaqs(500, 0.4) == 96
    assert calculate_iaqs(420, 0.0) > 90  # type: ignore[operator]
    assert calculate_iaqs(450, 5.0) > 90  # type: ignore[operator]
    assert calculate_iaqs(633, 11.5) < 90  # type: ignore[operator]
    assert calculate_iaqs(1000, 35.0) < 70  # type: ignore[operator]
