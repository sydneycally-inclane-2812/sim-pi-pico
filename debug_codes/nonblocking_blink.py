from machine import Pin, Timer

led = Pin(25, Pin.OUT)  # Set up the LED pin

def blink(timer):
    led.toggle()          # Toggle the LED state

# Create a timer that calls the blink function every 500 ms
timer = Timer()
timer.init(period=500, mode=Timer.PERIODIC, callback=blink)
#
