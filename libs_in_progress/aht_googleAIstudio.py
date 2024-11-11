import machine
import time

class AHT20:
    def __init__(self, i2c, addr=0x38):
        self.i2c = i2c
        self.addr = addr
        self.reset()
        self.initialize()

    def reset(self):
      # Soft reset - not a full power down reset
      self._write_register(0x1b, 0x00, 0x00)
      time.sleep_ms(5)

      self._write_register(0x1c, 0x00, 0x00)
      time.sleep_ms(5)

      self._write_register(0x1e, 0x00, 0x00)
      time.sleep_ms(5)




    def initialize(self):
        time.sleep_ms(20) # Wait after power-on

        # Check status and perform soft-reset if necessary
        status = self._read_status()
        #Check if CAL bit is enabled
        if not (status & 0x18) == 0x18 :
          self.reset()
          time.sleep_ms(10)

        # Normal mode
        self._write_register(0xA8, 0x00, 0x00)
        time.sleep_ms(10)

        # Calibration enable
        self._write_register(0xBE, 0x08, 0x00)
        time.sleep_ms(10)

    def _read_status(self):
        self.i2c.writeto(self.addr, bytearray([0x71]))
        return self.i2c.readfrom(self.addr, 1)[0]


    def _write_register(self, cmd, byte1, byte2):
        self.i2c.writeto(self.addr, bytearray([cmd, byte1, byte2]))


    def measure(self):
        # Trigger measurement
        self._write_register(0xAC, 0x33, 0x00)

        # Wait for completion (with timeout)
        timeout = 50 # adjust as needed
        while (self._read_status() & 0x80) != 0:
            time.sleep_ms(1)
            timeout -= 1
            if timeout == 0:
                raise RuntimeError("AHT20 measurement timed out!")



        # Read data
        self.i2c.writeto(self.addr, bytearray([0x71]))
        data = self.i2c.readfrom(self.addr, 7)

        # Process data
        h = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / (1 << 20)  # Humidity (%)
        t = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / (1 << 20) - 50  # Temperature (°C)

        return h, t

# Example usage (assuming I2C is already initialized):
# i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)  # Adjust pins and freq
# sensor = AHT20(i2c)
# humidity, temperature = sensor.measure()
# print("Humidity:", humidity, "%")
# print("Temperature:", temperature, "°C")