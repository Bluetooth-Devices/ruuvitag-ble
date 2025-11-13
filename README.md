# ruuvitag-ble

[Sans-IO](https://sans-io.readthedocs.io/) parser for [Ruuvi](https://ruuvi.com/) wireless sensor BLE devices.

Mainly meant for interoperation with [Home Assistant](https://www.home-assistant.io/)'s
Ruuvi integration, but could be useful in other contexts as well.

## Supported Devices

- [**RuuviTag**](https://ruuvi.com/ruuvitag/) - Environmental sensor tags
- [**RuuviTag Pro**](https://ruuvi.com/ruuvitag-pro/) - Heavy-duty environmental sensor tags
- [**Ruuvi Air**](https://ruuvi.com/air/) - Air quality monitors

## Supported Data Formats

This library supports the following Ruuvi BLE advertisement data formats:

### RuuviTag and RuuviTag Pro

#### Data Format 3 (0x03)

Legacy format supported by older RuuviTag firmware.

**Measurements:**

- Temperature (Celsius, range: -127.99 to 127.99°C, resolution: 0.01°C)
- Humidity (%, range: 0 to 100%, resolution: 0.5%)
- Pressure (hPa, range: 500 to 1155.35 hPa, resolution: 0.01 hPa)
- Acceleration X/Y/Z (m/s², converted from mG)
- Battery voltage (mV)

#### Data Format 5 (0x05)

Standard format used by RuuviTag firmware 2.x and later.

**Measurements:**

- Temperature (Celsius, range: -163.835 to 163.835°C, resolution: 0.005°C)
- Humidity (%, range: 0 to 163.8350%, resolution: 0.0025%)
- Pressure (hPa, range: 500 to 1155.35 hPa, resolution: 0.01 hPa)
- Acceleration X/Y/Z (mG, converted to m/s²)
- Battery voltage (mV, range: 1600 to 3647 mV)
- TX power (dBm, range: -40 to 20 dBm)
- Movement counter
- Measurement sequence number
- MAC address (6 bytes)

### Ruuvi Air

#### Data Format 6 (0x06)

Compact format for air quality monitoring, used by Ruuvi Air and similar devices.

**Measurements:**

- Temperature (Celsius, resolution: 0.005°C)
- Humidity (%, resolution: 0.0025%)
- Pressure (hPa, resolution: 0.01 hPa)
- PM2.5 (μg/m³, resolution: 0.1 μg/m³)
- CO2 (ppm)
- VOC index (9-bit value, range: 0-500)
- NOx index (9-bit value, range: 0-500)
- Luminosity (lux, logarithmic scale)
- Sound average (dBA, resolution: 0.2 dBA, range: 18-119.6 dBA)
- Measurement sequence number
- MAC address (3 bytes)

#### Data Format E1 (0xE1)

Extended format providing comprehensive environmental and air quality data with higher precision.

**Measurements:**

- Temperature (Celsius, range: -163.835 to 163.835°C, resolution: 0.005°C)
- Humidity (%, range: 0 to 100%, resolution: 0.0025%)
- Pressure (hPa, range: 500 to 1155.34 hPa, resolution: 0.01 hPa)
- PM1.0 (μg/m³, resolution: 0.1 μg/m³)
- PM2.5 (μg/m³, resolution: 0.1 μg/m³)
- PM4.0 (μg/m³, resolution: 0.1 μg/m³)
- PM10 (μg/m³, resolution: 0.1 μg/m³)
- CO2 (ppm)
- VOC index (9-bit value, range: 0-500)
- NOx index (9-bit value, range: 0-500)
- Luminosity (lux, resolution: 0.01 lux)
- Measurement sequence number (24-bit)
- Calibration status flag
- MAC address (6 bytes)
