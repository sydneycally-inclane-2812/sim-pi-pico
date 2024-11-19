# Printing all the characters of the framebuf charset

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

i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

buffer = []
row = 0
for letter in range(32, 128):
    buffer.append(chr(letter))
    if len(buffer) >= 20:
        oled.text(''.join(buffer), 0, row)
        row += 10
        buffer = []
oled.text(''.join(buffer), 0, row)
        
    

oled.show()