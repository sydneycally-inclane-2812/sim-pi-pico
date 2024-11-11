import sys
sys.path.append('/lib')

import ds3231
import ssd1306
from machine import Pin, I2C, Timer
import mfs

# Constants
I2C_FREQ = 400000
SYNC_INTERVAL = 1000
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH_LIST = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class ClockDisplay:
    def __init__(self):
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=I2C_FREQ)
        self.led = Pin(25, Pin.OUT)
        self.rtc = ds3231.DS3231(self.i2c)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.counter = None
        self.curr = []

    def print_time(self, timer):
        self.led.toggle()
        if self.counter is None or self.counter >= SYNC_INTERVAL:
            self.counter = 0
            self.curr = list(self.rtc.get_time())
        self.counter += 1
        self.update_display()
        self.increment_time()

    def update_display(self):
        self.oled.fill(0)
        self.oled.text(str(self.curr[3]), 0, 10)
        self.oled.text(str(self.curr[4]), 25, 10)
        self.oled.text(str(self.curr[5]), 50, 10)
        self.oled.text(str(self.curr[2]), 0, 40)
        self.oled.text(MONTH_LIST[self.curr[1] - 1], 25, 40)
        self.oled.text(str(self.curr[0]), 60, 40)
        self.oled.show()

    def increment_time(self):
        self.curr[5] += 1
        if self.curr[5] >= 60:
            self.curr[5] = 0
            self.curr[4] += 1
        if self.curr[4] >= 60:
            self.curr[4] = 0
            self.curr[3] += 1
        if self.curr[3] >= 24:
            self.curr[3] = 0
            self.curr[2] += 1
        if self.curr[2] > self.days_in_month(self.curr[0], self.curr[1]):
            self.curr[2] = 1
            self.curr[1] += 1
        if self.curr[1] > 12:
            self.curr[1] = 1
            self.curr[0] += 1

    @staticmethod
    def days_in_month(year, month):
        if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            return 29
        return DAYS_IN_MONTH[month - 1]

clock_display = ClockDisplay()
timer1 = Timer()
timer1.init(period=1000, mode=Timer.PERIODIC, callback=clock_display.print_time)

# 14.40625kb used out of 223.2344kb
# 44kb used out of 15360kb
# 15316kb free