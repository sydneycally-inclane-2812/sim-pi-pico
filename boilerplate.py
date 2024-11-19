# Add lib dir to sys
import sys
if '/lib' not in sys.path:
    sys.path.append('/lib')

import ds3231
import ssd1306
import aht20
import mfs
from machine import Pin, ADC, I2C, Timer
import neopixel