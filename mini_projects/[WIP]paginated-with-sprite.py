import sys
if '/lib' not in sys.path:
    sys.path.append('/lib')
if '/assets' not in sys.path:
    sys.path.append('/assets')

import ds3231
import ssd1306
import aht20
import mfs
from machine import Pin, ADC, I2C, Timer
import neopixel
import time
import env
import framebuf

i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

