import sys
if '/lib' not in sys.path:
    sys.path.append('/lib')

import math
import ssd1306
from machine import Pin, I2C, Timer
import time
import _thread

# Set up I2C and OLED display
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Ball position and speed
fps = 60  # Frames per second
xpos = 0
speed = 115  # Pixels per second
frame_time = 1000 // fps  # Frame time in milliseconds

# Shared lock for thread-safe access to variables
lock = _thread.allocate_lock()

def draw_ball():
    global xpos
    last_time = time.ticks_ms()
    
    while True:
        # Get the current time
        current_time = time.ticks_ms()
        
        # Calculate the elapsed time in seconds
        elapsed_time = time.ticks_diff(current_time, last_time) / 1000.0  # Convert milliseconds to seconds
        
        # Update ball position based on elapsed time
        with lock:  # Ensure thread-safe update
            xpos += speed * elapsed_time
            if xpos > 128:  # Reset if out of bounds
                xpos = 0
        
        # Clear the display
        oled.fill(0)
        
        # Draw the ball as a small filled rectangle
        with lock:  # Ensure thread-safe read
            oled.text('o', int(xpos), 30)  # A 4x4 "ball"
        
        oled.show()
        
        # Update last_time
        last_time = current_time
        
        # Delay for the frame time
        time.sleep_ms(frame_time)

# Main function to start the second core
def main():
    # Start the ball-drawing routine on the second core
    _thread.start_new_thread(draw_ball, ())
    
    # Main loop (can handle other tasks here)
    while True:
        pass  # Add main-core tasks here if needed

# Run the main function
main()
