# Add lib dir to sys
import sys
sys.path.append('/lib')

import ds3231
import ssd1306
from machine import Pin, I2C, Timer
import mfs

# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

led = Pin(25, Pin.OUT)
rtc = ds3231.DS3231(i2c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

counter = None # Syncs time every 1000 seconds and power on
curr= []
def printTime(timer):
    global counter, curr
    led.toggle()
    if (counter == None) or (counter >= 1000):
        counter = 0
        curr = list(rtc.get_time())
    counter += 1
    oled.fill(0)
    # oled.text('Current time is:', 0, 0)
    oled.text(str(curr[3]), 0, 10)
    oled.text(str(curr[4]), 25, 10)
    oled.text(str(curr[5]), 50, 10)
    # oled.text("On: ", 0, 30)
    oled.text(str(curr[2]), 0, 40)
    oled.text(month_list[curr[1] - 1], 25, 40)
    oled.text(str(curr[0]), 60, 40)
    
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
timer1.init(period=1000, mode=Timer.PERIODIC, callback=printTime)


