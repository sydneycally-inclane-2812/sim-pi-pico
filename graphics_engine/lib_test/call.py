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
import machine
from machine import Pin, ADC, I2C, Timer
import neopixel
import time
import env
import framebuf
import _thread
import pyogotchi

# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

ptr = ADC(Pin(29))
obbutton = Pin(24, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)
l1 = Pin(22, Pin.OUT)
l2 = Pin(23, Pin.OUT)
np = neopixel.NeoPixel(Pin(23, Pin.OUT), 1)
rtc = ds3231.DS3231(i2c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
aht = aht20.AHT20(i2c)

grass_series = [env.grass_left, env.grass_mid, env.grass_right, env.grass_mid]
grass_timings = [3, 2, 3, 2]

lucky_series = [env.dawg_full_t1, env.dawg_exh_t1, env.dawg_exh_t2, env.dawg_exh_t1, env.dawg_full_t2, env.dawg_full_t2]
lucky_timings = [5, 3, 2, 2, 5, 3]

game = pyogotchi.Pyogotchi(oled, 250, 250, 1000)
grass = pyogotchi.SimpleDynamicSprite_CycleOnly(frames=grass_series, seq_timer=grass_timings)
lucky = pyogotchi.SimpleDynamicSprite_CycleOnly(frames=lucky_series, seq_timer=lucky_timings)

game.add("grass1", grass, 0, 0, 5)
game.add("grass2", grass, 1, 20, 20)
game.add("grass3", grass, 2, 70, 35)
game.add("grass4", grass, 1, 84, 15)
game.add("grass5", grass, 0, 30, 40)
game.add("grass6", grass, 2, 0, 35)
game.add("grass7", grass, 1, 4, 45)
game.add("grass8", grass, 1, 100, 40)
game.add("grass9", grass, 1, 100, 10)
game.add("lucky", lucky, 0, 45, 7)

game.begin()

