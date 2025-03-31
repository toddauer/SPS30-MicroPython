import time
from machine import Pin, I2C
import struct

# Set up I2C communication (adjust the pins accordingly)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)

# SPS30 I2C address
SPS30_ADDRESS = 0x69

# Commands for SPS30
START_MEASUREMENT_CMD = b'\x00\x10'  # Pointer address for start measurement
READ_MEASURED_VALUES_CMD = b'\x03\x00'  # Pointer address for reading measured values
STOP_MEASUREMENT_CMD = b'\x01\x04'
READ_FIRMWARE_VERSION_CMD = b'\xD1\x00' # Could not get this to read correctly
CLEANING_MODE_CMD = b'\x10\x04'  # Command for cleaning mode

# Output format: 0x05 for unsigned 16-bit integers
OUTPUT_FORMAT = 0x05  # 0x05 = Unsigned 16-bit integer values

# Function to calculate the checksum (CRC-8)
def calculate_checksum(data):
    crc = 0xFF  # Initialize the CRC value
    for byte in data:
        crc ^= byte
        for _ in range(8):  # 8-bit CRC calculation
            if crc & 0x80:  # If the most significant bit is set
                crc = (crc << 1) ^ 0x31  # Polynomial 0x31
            else:
                crc <<= 1
            crc &= 0xFF  # Keep CRC within 8 bits
    return crc

# Function to start the sensor measurement
def start_measurement():
    # Define the measurement output format (0x05 for unsigned 16-bit)
    output_format = OUTPUT_FORMAT
    dummy_byte = 0x00     # Dummy byte
    data = bytearray([output_format, dummy_byte])

    # Calculate checksum for the first two bytes (output_format and dummy_byte)
    checksum = calculate_checksum(data)
    data.append(checksum)  # Add the checksum to the data

    # Send the pointer address and the data to the sensor
    i2c.writeto(SPS30_ADDRESS, START_MEASUREMENT_CMD + data)
    time.sleep(2)  # Increased delay to ensure sensor starts measuring properly

# Function to stop the sensor
def stop_measurement():
    i2c.writeto(SPS30_ADDRESS, STOP_MEASUREMENT_CMD)
    time.sleep(1)

# Function to enter cleaning mode
def enter_cleaning_mode():
    i2c.writeto(SPS30_ADDRESS, CLEANING_MODE_CMD)
    print("Cleaning mode activated. Waiting for completion...")
    time.sleep(40)  # Wait for cleaning mode to complete
    print("Cleaning mode completed.")
    
def stop_measurement():
    i2c.writeto(SPS30_ADDRESS, STOP_MEASUREMENT_CMD)
    print("Measurement stopped. Fan is off.")
    time.sleep(1)  # Short delay to ensure the sensor properly stops

# Function to read the firmware version
def read_firmware_version():
    i2c.writeto(SPS30_ADDRESS, READ_FIRMWARE_VERSION_CMD)
    time.sleep(0.5)  # Short delay to allow the sensor to respond
    
    # Read the 3 bytes of firmware version
    data = i2c.readfrom(SPS30_ADDRESS, 3)
    if len(data) != 3:
        print("Error: Invalid firmware version data received.")
        return None
    
    # Convert the firmware version bytes into a string
    firmware_version = ''.join([chr(byte) for byte in data])
    
    return firmware_version

# Function to read the measured values based on the selected output format
# Function to read the measured values based on the selected output format
def read_measured_values():
    i2c.writeto(SPS30_ADDRESS, READ_MEASURED_VALUES_CMD)
    time.sleep(0.5)  # Short delay to allow the sensor to respond
    
    # Read 30 bytes of data (sensor output length)
    data = i2c.readfrom(SPS30_ADDRESS, 30)
    if len(data) != 30:
        print("Error: Invalid data length received.")
        return None
    
    # Print raw data in a human-readable way
    print("Raw data (hex):", ' '.join(f'{byte:02X}' for byte in data))
    
    measurements = []
    
    # Process the data (2 bytes per value + 1 CRC byte for each 2-byte packet)
    for i in range(0, len(data), 3):  # Increment by 3 because each measurement has 2 bytes + 1 CRC
        value_bytes = data[i:i+2]
        crc_byte = data[i+2]
        
        # Check CRC for this 2-byte packet
        calculated_crc = calculate_checksum(value_bytes)
        if crc_byte != calculated_crc:
            print(f"CRC mismatch for data at index {i}. Expected {calculated_crc}, got {crc_byte}.")
            return None
        
        # Convert the 2-byte data into an unsigned 16-bit integer (Big-endian)
        value = struct.unpack('>H', bytes(value_bytes))[0]  # Big-endian unsigned 16-bit integer
        measurements.append(value)
    
    return measurements


# Main loop
start_measurement()

try:
    # Read and print the firmware version
    firmware_version = read_firmware_version()
    if firmware_version:
        print("Firmware Version:", firmware_version)
    else:
        print("Failed to read firmware version.")
    
    while True:
        time.sleep(5)
        measurements = read_measured_values()
        if measurements:
            # Print the measured values (assuming the order is PM1.0, PM2.5, PM10.0, etc.)
            print(f"PM1.0: {measurements[0]} µg/m³")
            print(f"PM2.5: {measurements[1]} µg/m³")
            print(f"PM4.0: {measurements[2]} µg/m³")
            print(f"PM10.0: {measurements[3]} µg/m³")
            print(f"NC0.5: {measurements[4]} particles/0.1L")
            print(f"NC1.0: {measurements[5]} particles/0.1L")
            print(f"NC2.5: {measurements[6]} particles/0.1L")
            print(f"NC4.0: {measurements[7]} particles/0.1L")
            print(f"NC10.0: {measurements[8]} particles/0.1L")
            print(f"Typical Particle Size: {measurements[9]} nm")
            print("--------------------------------------")
        else:
            print("Failed to read valid sensor data.")

            time.sleep(2)  # Delay between measurements
        
except KeyboardInterrupt:
    stop_measurement()
    print("Measurement stopped.")
