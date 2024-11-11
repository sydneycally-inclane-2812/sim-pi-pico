from machine import Pin, ADC
import time

# Create a list to hold Pin objects
pins = []

# Initialize the pins in a loop
for i in range(3, 9):
    pin = Pin(i, Pin.IN, Pin.PULL_DOWN)
    pins.append(pin)

# Initialize the analog light sensor pin
adc = ADC(Pin(29))
while True:
    for pin in pins:
        state = pin.value()  # Read the value directly from the pin object
        print(state, sep='')
    print()
    print(adc.read_u16())
    print()
    time.sleep_ms(500)
