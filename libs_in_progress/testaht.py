import time
from machine import I2C, Pin

# Define constants based on the AHT20 documentation
AHT20_I2C_ADDRESS = 0x38

# Commands
AHT20_INIT_CMD = b'\xBE\x08\x00'  # Initialization command
AHT20_TRIGGER_MEASUREMENT_CMD = b'\xAC\x33\x00'  # Trigger measurement command
AHT20_SOFT_RESET_CMD = b'\xBA'  # Soft reset command

class AHT20:
    def __init__(self, i2c, address=AHT20_I2C_ADDRESS):
        self.i2c = i2c
        self.address = address
        self.initialize_sensor()

    def initialize_sensor(self):
        """Initializes the AHT20 sensor."""
        self.i2c.writeto(self.address, AHT20_INIT_CMD)
        time.sleep(0.01)  # Wait 10ms for initialization

    def soft_reset(self):
        """Sends a soft reset command to the sensor."""
        self.i2c.writeto(self.address, AHT20_SOFT_RESET_CMD)
        time.sleep(0.02)  # Wait 20ms for soft reset to complete

    def trigger_measurement(self):
        """Triggers a temperature and humidity measurement."""
        self.i2c.writeto(self.address, AHT20_TRIGGER_MEASUREMENT_CMD)
        time.sleep(0.075)  # Wait for measurement to be ready (>75ms)

    def read_status(self):
        """Reads the status register of the sensor to check if it's busy."""
        status = self.i2c.readfrom(self.address, 1)[0]
        busy = (status & 0x80) != 0  # Check if the busy bit is set (bit 7)
        return busy

    def read_temperature_and_humidity(self):
        """Reads the sensor data and calculates temperature and humidity."""
        self.trigger_measurement()
        
        # Wait for the sensor to be ready by checking the busy flag
        while self.read_status():
            time.sleep(0.01)  # Poll every 10ms

        # Read 6 bytes of data from the sensor
        data = self.i2c.readfrom(self.address, 6)
        
        # Unpack the data: Humidity (20 bits), Temperature (20 bits)
        humidity_raw = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
        temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        # Calculate the relative humidity in percentage
        humidity = (humidity_raw / (2**20)) * 100.0

        # Calculate the temperature in Celsius
        temperature = ((temperature_raw / (2**20)) * 200.0) - 50.0

        return temperature, humidity

# Example usage


sda=machine.Pin(0)
scl=machine.Pin(1)
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)

aht20 = AHT20(i2c)

# temperature, humidity = aht20.read_temperature_and_humidity()
# print("Temperature: {:.2f} °C, Humidity: {:.2f} %".format(temperature, humidity))