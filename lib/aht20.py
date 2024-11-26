import machine
import time

# Based on library provided by Aosong
# http://aosong.com/userfiles/files/software/AHT20-21%20DEMO%20V1_3(1).rar

_ADDR = 0x38  # Correct I2C address for AHT20/AHT21 (0x38 shifted left by 1)

class AHT20:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = _ADDR  # Assign the correct address to the instance variable
        self.soft_reset()
        self.initialize()

    def soft_reset(self):
        self._write_register(0xBA, 0x00, 0x00) # use 0xBA for commands such as soft_reset
        time.sleep_ms(20) # increased delay as per datasheet

    def initialize(self):
        time.sleep_ms(20)

        status = self._read_status()
        if not (status & 0x18) == 0x08: # check only cal enable bit [3]. 
            self.soft_reset()
            time.sleep_ms(10)

        self._write_register(0xBA, 0xA8, 0x00)
        time.sleep_ms(20)  # increased delay as per datasheet for command

        self._write_register(0xBA, 0xBE, 0x08, 0x00)
        time.sleep_ms(15) # added 100ms to ensure calibration is fully initialized.


    def _read_status(self):
        self.i2c.writeto(self.addr, bytearray([0x71]))
        return self.i2c.readfrom(self.addr, 1)[0]
    
    def _write_register(self, *args):
      self.i2c.writeto(self.addr, bytearray(args))

        
    def measure(self, rounding=5):
        self._write_register(0xAC, 0x33, 0x00)
        
        timeout = 50
        while (self._read_status() & 0x80) != 0:
            time.sleep_ms(10)
            timeout -= 1
            if timeout == 0:
                raise RuntimeError("AHT20 measurement timed out!")
        
        # Read data (outside the loop)
        self.i2c.writeto(self.addr, bytearray([0x71]))
        data = self.i2c.readfrom(self.addr, 7)

        h = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / (1 << 20)
        t = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / (1 << 20) - 50
    
        return round(h, rounding), round(t, rounding)