from machine import Pin, I2C
import ssd1306
import time

# Set up I2C on bus 0 (SDA=GP0, SCL=GP1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

# OLED dimensions (128x64 is typical for SSD1306)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Clear the display
oled.fill(0)

# Display some text
oled.text('Hello, World!', 0, 0)
oled.text("This sucks!", 0, 9)
oled.text("Line 3", 0, 9*2)
oled.text("Line 4", 0, 9*3)
oled.text("Line 5", 0, 9*4)
oled.text("Line 6", 0, 9*5)
oled.text("Line 7", 0, 9*6)
oled.show()

# Keep the display on for a while
time.sleep(5)
