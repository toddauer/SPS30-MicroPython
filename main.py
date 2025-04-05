from machine import I2C, Pin
import time
from sps30 import SPS30

# Set up I2C (adjust pins as needed)
scl = 27
sda = 26
i2c = I2C(1, scl=Pin(scl), sda=Pin(sda), freq=100000)
sensor = SPS30(i2c)

print("Starting SPS30...")
sensor.start_measurement()

try:
    while True:
        if sensor.read_data_ready():
            data = sensor.read_measurement()
            for k, v in data:
                if isinstance(v, float):  # Only format if it's a float
                    print(f"{k}: {v:.2f}")
                else:
                    print(f"{k}: {v}")  # AQI is a string, so just print it
            print()
        else:
            print("Waiting for data...")
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")
    sensor.stop_measurement()

