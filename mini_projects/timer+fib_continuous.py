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

month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
counter = None # Syncs time every 1000 seconds and power on
curr= []
h, t = 0, 0
display_status = True
flag = True
l = 0
def buttonHandler(pin):
    global display_status
    display_status = not display_status
button.irq(trigger=Pin.IRQ_FALLING, handler=buttonHandler)

np[0] = (10, 10, 10)  # Set the first LED to red
np.write()  # Update the strip to show the changes
l1.value(1)

def updateFace(timer):
    global counter, curr, h, t, l, display_status, flag
    led.toggle()
    l1.toggle()
    l2.toggle()
    if (not display_status):
        oled.poweroff()
        flag = False
    if (display_status) and (not flag):
        oled.pw_on()
        flag = True
            
    if (counter == None) or (counter >= 1000):
        counter = 0
        curr = list(rtc.get_time())
    if (counter == None) or (counter % 10 == 0):
        h, t = aht.measure(rounding=2)

    if (counter == None) or (counter % 2 == 0):
        l = ptr.read_u16()
        
    counter += 1
    oled.fill(0)
    oled.text(str(curr[3]), 0, 0)
    oled.text(str(curr[4]), 20, 0)
    oled.text(str(curr[5]), 40, 0)

    oled.text(str(curr[2]), 0, 12)
    oled.text(month_list[curr[1] - 1], 20, 12)
    oled.text(str(curr[0]), 55, 12)
    
    oled.text(str(h), 0, 33)
    oled.text("%", 45, 33)
    oled.text(str(t), 70, 33)
    oled.text("C", 115, 33)
    
    oled.text(str(l), 0, 45)
    oled.text("L", 45, 45)
    
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

num = 1
num2 = 1
f = True
timer1 = machine.Timer()
timer1.init(period=1000, mode=Timer.PERIODIC, callback=updateFace)

# Fibonacci
while True:
    if f:
        num += num2
        print(num)
        f = False
    else:
        num2 += num
        print(num2)
        f = True
    time.sleep_ms(50)
    
timer1 = machine.Timer()
timer1.init(period=1000, mode=Timer.PERIODIC, callback=updateFace)

