from __future__ import annotations

import math

AQI_MAX = 100
PM25_MAX = 60
PM25_MIN = 0
PM25_SCALE = AQI_MAX / (PM25_MAX - PM25_MIN)
CO2_MAX = 2300
CO2_MIN = 420
CO2_SCALE = AQI_MAX / (CO2_MAX - CO2_MIN)


def calculate_iaqs(co2_value: int | None, pm25_value: float | None) -> int | None:
    """Calculate the Ruuvi indoor air quality score (IAQS).

    Documentation for the calculation algorithm can be found at
    https://docs.ruuvi.com/ruuvi-air-firmware/ruuvi-indoor-air-quality-score-iaqs.
    """

    if co2_value is None or pm25_value is None:
        return None

    co2_clamped = min(max(co2_value, CO2_MIN), CO2_MAX)
    pm25_clamped = min(max(pm25_value, PM25_MIN), PM25_MAX)

    dx = (pm25_clamped - PM25_MIN) * PM25_SCALE
    dy = (co2_clamped - CO2_MIN) * CO2_SCALE

    value = AQI_MAX - math.hypot(dx, dy)
    if value > AQI_MAX:
        return AQI_MAX
    if value < 0:
        return 0
    return int(round(value))
