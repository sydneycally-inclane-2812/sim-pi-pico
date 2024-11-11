from machine import Pin, I2C, Timer
import time

i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

_ADDR = const(0x38) # or b

# remember to wait 20ms after start and soft reset

# commands
INIT            = const(0b10111110) #0xBE
TRIG_MEASURE    = const(0b10101100) #0xAC
SOFT_RESET      = const(0b10111010)	#0xBA

# init send 0b11100001 or 0xE1 first
# temperature send 0b10101100 or 0xAC
# then wait for measurement
# after that, send one of the three commands

class AHT20:
    def __init__(self, i2c):
        self.aht20 = i2c
        if _ADDR not in self.aht20.scan():
            raise RuntimeError("AHT20 cannot be found at", _ADDR)
        
    def start(self):
        '''
            1. Send 0x
        '''
        