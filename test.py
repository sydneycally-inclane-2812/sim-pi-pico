import sys
sys.path.append('/lib')

import ds3231
import ssd1306
from machine import Pin, I2C, Timer
import mfs
import aht20
import time

# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

led = Pin(25, Pin.OUT)
rtc = ds3231.DS3231(i2c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
aht = aht20.AHT20(i2c)
# time.sleep(1)
# aht.initialize()

h, t = aht.measure(rounding=2)
print(h, t)
