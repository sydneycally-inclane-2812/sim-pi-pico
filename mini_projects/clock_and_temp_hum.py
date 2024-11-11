# Add lib dir to sys
import sys
if '/lib' not in sys.path:
    sys.path.append('/lib')

import ds3231
import ssd1306
import aht20
import mfs
from machine import Pin, I2C, Timer

# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

led = Pin(25, Pin.OUT)
rtc = ds3231.DS3231(i2c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
aht = aht20.AHT20(i2c)

month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
counter = None # Syncs time every 1000 seconds and power on
curr= []
h, t = 0, 0

def updateFace(timer):
    global counter, curr, h, t
    led.toggle()
    if (counter == None) or (counter >= 1000):
        counter = 0
        curr = list(rtc.get_time())
    if (counter == None) or (counter % 10 == 0):
        h, t = aht.measure(rounding=3)
    counter += 1
    oled.fill(0)
    oled.text(str(curr[3]), 0, 5)
    oled.text(str(curr[4]), 20, 5)
    oled.text(str(curr[5]), 40, 5)

    oled.text(str(curr[2]), 0, 17)
    oled.text(month_list[curr[1] - 1], 20, 17)
    oled.text(str(curr[0]), 55, 17)
    
    oled.text(str(h), 0, 40)
    oled.text("%", 55, 40)
    oled.text(str(t), 0, 52)
    oled.text("C", 55, 52)
    
    # Maintain the time until update
    curr[5] += 1
    if curr[5] >= 60:
        curr[5] = 0
        curr[4] += 1
    if curr[4] >= 60:
        curr[4] = 0
        curr[3] += 1
    if curr[3] >= 24:
        curr[3] = 0
        curr[2] += 1
  
    days_in_month = [31, 28 + (1 if (curr[0] % 4 == 0 and (curr[0] % 100 != 0 or curr[0] % 400 == 0)) else 0), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    if curr[2] > days_in_month[curr[1]-1]:
        curr[2] = 1
        curr[1] += 1
    if curr[1] > 12:
        curr[1] = 1
        curr[0] += 1
    oled.show()


timer1 = machine.Timer()
timer1.init(period=1000, mode=Timer.PERIODIC, callback=updateFace)