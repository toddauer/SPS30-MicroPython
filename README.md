# SPS30 MicroPython Library

This repository provides a MicroPython library to interact with the Sensirion SPS30 particulate matter sensor via I2C. It allows you to read measurements and calculate the Air Quality Index (AQI) based on the PM2.5 readings.

## Features

- Read particulate matter concentrations (PM1.0, PM2.5, PM4.0, PM10.0)
- Read particle number concentrations (NC0.5, NC1.0, NC2.5, NC4.0, NC10.0)
- Calculate AQI for PM2.5
- Start and stop measurements
- Check if data is ready for reading
- CRC verification for data integrity

## Requirements

- MicroPython (compatible with ESP32/ESP8266 or other supported devices)
- Sensirion SPS30 sensor
- I2C communication setup
