import ds3231
from machine import Pin, I2C

# Initializing I2C
sda=machine.Pin(0)
scl=machine.Pin(1)
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
rtc = ds3231.DS3231(i2c)

# Reset the time

rtc.set_time()

