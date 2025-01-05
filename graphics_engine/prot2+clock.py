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
import _thread
import pyogotchi


# Initializing I2C
i2c=machine.I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

ptr = ADC(Pin(29))
obbutton = Pin(24, Pin.IN, Pin.PULL_UP)
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
l = 0

l1.value(1)
l2.value(0)
        
class Pyogotchi:
    def __init__(self, disp, frame_cl: int, game_cl: int, env_cl: int):
        self.disp = disp
        self.frame_cl = frame_cl
        self.game_cl = game_cl
        self.env_cl = env_cl
        self.game_status = False
        
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
    
    def remove(self, sprite: str):
        if sprite not in self.sprites:
            raise ValueError("Invalid object reference")
        width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
        x, y = self.sprites[sprite][3], self.sprites[sprite][4]
        data = bytearray([0 for i in self.sprites[sprite][2]])
        fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
        self.disp.blit(fbuf, x, y)
        del self.sprites[sprite]
    
    def update_loc(self, sprite: str, m: str, x = 0, y = 0):
        '''
            Update the location of a specified sprite
            sprite: name of the sprite you want to change location
            mode:
                'a': absolute coords
                'r': relative coords
        '''
        pass
    
    def _update_sprite(self, sprite: str, blackout: bool):
        '''
            For when you want to blank out a specific area, either because that sprite has been removed
            or moved somewhere else.
        '''
        pass
    
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
#         l1.toggle()
#         l2.toggle()
        pass
        
    def _env_update(self, timer):
        #print("env updated")
#         led.toggle()
        pass
    
    def begin(self):
        self.disp.fill(0)
        for sprite in self.sprites:
            width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
            x, y = self.sprites[sprite][3], self.sprites[sprite][4]
            data = self.sprites[sprite][2]
            fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
            self.disp.blit(fbuf, x, y)
        self.disp.show()
        self.game_status = True
        self.frame_tmr.init(period=self.frame_cl, mode=Timer.PERIODIC, callback=self._frame_update)
        self.game_tmr.init(period=self.game_cl, mode=Timer.PERIODIC, callback=self._game_update)
        self.env_tmr.init(period=self.env_cl, mode=Timer.PERIODIC, callback=self._env_update)
    
    def end(self):
        self.frame_tmr.deinit()
        self.game_tmr.deinit()
        self.env_tmr.deinit()
        self.game_status = False
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

grass_series = [env.grass_left, env.grass_mid, env.grass_right, env.grass_mid]
grass_timings = [3, 2, 3, 2]

lucky_series = [env.dawg_full_t1, env.dawg_exh_t1, env.dawg_exh_t2, env.dawg_exh_t1, env.dawg_full_t2, env.dawg_full_t2]
lucky_timings = [5, 3, 2, 2, 5, 3]

game = Pyogotchi(oled, 250, 250, 1000)
grass = SimpleDynamicSprite_CycleOnly(frames=grass_series, seq_timer=grass_timings)
lucky = SimpleDynamicSprite_CycleOnly(frames=lucky_series, seq_timer=lucky_timings)

game.add("grass1", grass, 0, 0, 5)
game.add("grass2", grass, 1, 20, 20)
game.add("grass3", grass, 2, 70, 35)
game.add("grass4", grass, 1, 84, 15)
game.add("grass5", grass, 0, 30, 40)
game.add("grass6", grass, 2, 0, 35)
game.add("grass7", grass, 1, 4, 45)
game.add("grass8", grass, 1, 100, 40)
game.add("grass9", grass, 1, 100, 10)
game.add("lucky", lucky, 0, 45, 7)


def buttonHandler(pin):
    global display_status
    display_status = not display_status
obbutton.irq(trigger=Pin.IRQ_FALLING, handler=buttonHandler)

def statusDisp(timer=None):
    global counter, curr, h, t, l, display_status
    led.toggle()
    l1.toggle()
    l2.toggle()
            
    if (counter == None) or (counter >= 10):
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

def os_prog(timer):
    global display_status, game
    if display_status: # show the game
        if not game.game_status:
            game.begin()
    else:
        if game.game_status:
            game.end()
        statusDisp()

OSTimer = machine.Timer(-1)
OSTimer.init(period=1000, mode=Timer.PERIODIC, callback=os_prog)
    


        
