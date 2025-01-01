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
import env
import framebuf

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

frame_series = [env.grass_left, env.grass_mid, env.grass_right, env.grass_mid]
frame_timings = [3, 2, 3, 2]

l1.value(1)
l2.value(0)

class Pyogotchi:
    def __init__(self, disp, frame_cl: int, game_cl: int, env_cl: int):
        self.disp = disp
        self.frame_cl = frame_cl
        self.game_cl = game_cl
        self.env_cl = env_cl
        
        self.sprites = {}
        self.sensors = []
        self.inputs = []
        
        self.frame_tmr = machine.Timer(-1)
        self.game_tmr = machine.Timer(-1)
        self.env_tmr = machine.Timer(-1)
        
    def add(self, name: str, sprite, frame: int, x: int, y: int):
        if frame >= sprite.length or frame < 0:
            raise ValueError("Invalid initial frame")
        if name in self.sprites.keys():
            raise ValueError("Object already exists")
        seq_counter, frame_data = sprite.force_retrieve(frame)
        self.sprites[name] = [sprite, seq_counter, frame_data, x, y]
    
    def _frame_update(self, timer):
        to_update = []
        for sprite in self.sprites:
            curr_seq = self.sprites[sprite][1]
            frame_data, reset_flag = self.sprites[sprite][0].get_next_frame(curr_seq)
            
            if frame_data is not None:
                self.sprites[sprite][2] = frame_data
                to_update.append(sprite)
                
            if reset_flag:
                self.sprites[sprite][1] = 0
            else:
                self.sprites[sprite][1] += 1
        
        for sprite in to_update:
            width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
            x, y = self.sprites[sprite][3], self.sprites[sprite][4]
            data = self.sprites[sprite][2]
            fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
            self.disp.blit(fbuf, x, y)
        self.disp.show()
    
    def _game_update(self, timer):
        #print("game updated")
        l1.toggle()
        l2.toggle()
        
    def _env_update(self, timer):
        #print("env updated")
        led.toggle()
    
    def begin(self):
        for sprite in self.sprites:
            width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
            x, y = self.sprites[sprite][3], self.sprites[sprite][4]
            data = self.sprites[sprite][2]
            fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
            self.disp.blit(fbuf, x, y)
        self.disp.show()    
        self.frame_tmr.init(period=self.frame_cl, mode=Timer.PERIODIC, callback=self._frame_update)
        self.game_tmr.init(period=self.game_cl, mode=Timer.PERIODIC, callback=self._game_update)
        self.env_tmr.init(period=self.env_cl, mode=Timer.PERIODIC, callback=self._env_update)
    
    def end(self):
        self.frame_tmr.deinit()
        self.game_tmr.deinit()
        self.env_tmr.deinit()
        self.disp.fill(0)
        self.disp.show()
    
class SimpleDynamicSprite_CycleOnly:
    def __init__(self, frames, seq_timer):
        self._validate(frames, seq_timer)
        self.frames = [frame[1] for frame in frames]
        self.width = frames[0][0][0]
        self.height = frames[0][0][1]
        self.length = len(frames)
        self.seq_timer = [max(sum(seq_timer[:i])- 1, 0) for i in range(1, len(seq_timer)+1)]

    def _validate(self, frames, seq_timer):
        # check same dim, frames and seq_timer same length, seq_timer > 0
        if not all([frame[0] == frames[0][0] for frame in frames]):
            raise ValueError("Inconsistent frame dimensions")
        if len(frames) != len(seq_timer):
            raise ValueError("Frame and seq_timer mismatch")
        if not all([i > 0 for i in seq_timer]):
            raise ValueError("Invalid seq_timer")

    def get_next_frame(self, seq_counter):
        '''return format (update_flag, frame, reset_flag)
        frame: the frame to be displayed, None if not updating
        reset_flag: True if the frame is the last frame, false if not
        '''
        if seq_counter < 0 or seq_counter > self.seq_timer[-1]:
            raise ValueError("Invalid seq_counter")
        if seq_counter == 0:
            return self.frames[0], False
        elif seq_counter in self.seq_timer[:-1]:
            idx = self.seq_timer.index(seq_counter)
            return self.frames[idx + 1], False
        if seq_counter == self.seq_timer[-1]:
            return self.frames[0], True
        return None, False
    
    def force_retrieve(self, frame_idx):
        '''return format (seq_counter, frame, reset_flag)
        seq_counter: the first counter value to belong with the frame, for example if the seq is [1, 3, 5] and frame 1 is requested, seq_counter would be 1
        frame: the frame to be displayed
        '''
        if frame_idx < 0 or frame_idx >= len(self.frames):
            raise ValueError("Invalid frame_idx")
        if frame_idx == 0:
            return 0, self.frames[0]
        elif frame_idx == len(self.frames) - 1:
            return self.seq_timer[-1], self.frames[-1]
        else:
            return self.seq_timer[frame_idx - 1], self.frames[frame_idx]
        

game = Pyogotchi(oled, 250, 250, 1000)
grass = SimpleDynamicSprite_CycleOnly(frames=frame_series, seq_timer=frame_timings)

game.add("grass1", grass, 0, 0, 0)
game.add("grass2", grass, 1, 20, 20)
game.add("grass3", grass, 2, 70, 35)
game.add("grass4", grass, 1, 84, 15)
game.add("grass5", grass, 0, 30, 40)
game.add("grass6", grass, 2, 0, 35)
game.add("grass7", grass, 1, 4, 45)
game.add("grass8", grass, 1, 100, 40)
game.add("grass9", grass, 1, 100, 10)
game.add("grass10", grass, 1, 50, 0)



game.begin()