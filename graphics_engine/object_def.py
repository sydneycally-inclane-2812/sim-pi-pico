# Add lib dir to sys
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
import uasyncio

# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

ptr = ADC(Pin(29))
button = Pin(24, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)
l1 = Pin(22, Pin.OUT)
l2 = Pin(23, Pin.OUT)
np = neopixel.NeoPixel(Pin(23, Pin.OUT), 1)
rtc = ds3231.DS3231(i2c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
aht = aht20.AHT20(i2c)


frames = [env.grass_left, env.grass_mid, env.grass_right]
ftimes = [2, 1, 3]
m = 'br'

class SimpleDynamicSprite:
    @staticmethod
    def valid_dims(frames):
        fdim = frames[0][0]
        for frame in frames:
            if frame[0] != fdim:
                return False
        return True

    def __init__(self, frames, mode, x=0, y=0):
        assert self.valid_dims(frames), "Frame dimensions do not match"
        self.frames = [frame[1] for frame in frames]
        self.mode = mode
        self.x = x
        self.y = y
        self.current_frame = 0

    def update(self):
        # Update logic for the sprite, e.g., change the current frame
        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def kill(self):
        # Logic to remove or deactivate the sprite
        pass

# Example usage
sprite = SimpleDynamicSprite(frames, mode='loop', x=10, y=10)
    

