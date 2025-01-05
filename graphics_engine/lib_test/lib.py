# Pyogotchi
# Annotated edition, the other one is not to save space.

import machine
from machine import Timer # For some fucking reason it doesn't import everything over
import framebuf


class Pyogotchi:
    def __init__(self, disp, frame_cl: int, game_cl: int, env_cl: int):
        '''
        Initialize the Pyogotchi object
            disp: the display object, currently only tested on SSD1306 and must support framebuf
            frame_cl: the frame update cycle length in ms
            game_cl: the game update cycle length in ms
            env_cl: the environment update cycle length in ms
        '''

        # Assigning the variables
        self.disp = disp
        self.frame_cl = frame_cl
        self.game_cl = game_cl
        self.env_cl = env_cl
        self.game_status = False
        
        # Assigning the list of sprites, sensors and inputs
        # Sensors are from the environment, such as light or temperature
        # Inputs are currently only button presses from the user, future may include rotary encoders, potentiometers, etc.
        self.sprites = {}
        self.sensors = []
        self.inputs = []
        
        # Assigning the timers
        # Considering transitioning to a single timer with a more robust callback system
        # One of the pros of the timer is that its simpler and allows for downtime between updates, easier for development.
        # Cons is that it hogs up 3/4 timers on the RP2040
        self.frame_tmr = machine.Timer(-1)
        self.game_tmr = machine.Timer(-1)
        self.env_tmr = machine.Timer(-1)
        
    def add(self, name: str, sprite, frame: int, x: int, y: int):
        '''
            Add a sprite to the display
                name: name of the sprite
                sprite: reference to the sprite object
                frame: the initial frame to display
                x: x coordinate
                y: y coordinate
        '''
        if frame >= sprite.length or frame < 0:
            raise ValueError("Invalid initial frame")
        if name in self.sprites.keys():
            raise ValueError("Object already exists")
        # bundling all the information into a dictionary entry
        seq_counter, frame_data = sprite.force_retrieve(frame)
        self.sprites[name] = [sprite, seq_counter, frame_data, x, y]
    
    def remove(self, sprite: str):
        if sprite not in self.sprites:
            raise ValueError("Invalid object reference")
        # blanking out the space, should also create a separate function to blank out for better reusability
        width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
        x, y = self.sprites[sprite][3], self.sprites[sprite][4]
        data = bytearray([0 for i in self.sprites[sprite][2]])
        fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
        self.disp.blit(fbuf, x, y)
        # removing the sprite from the dictionary
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
        # The main update loop to find the sprites that needs to be update and update them
        to_update = []
        for sprite in self.sprites:
            curr_seq = self.sprites[sprite][1] # grab the current sequence counter from the sprite bundle
            frame_data, reset_flag = self.sprites[sprite][0].get_next_frame(curr_seq) # calling the sprite object to get the next frame
            
            # if the returned data is not None, update the information in the sprite bundle and flag it as to be updated
            if frame_data is not None:
                self.sprites[sprite][2] = frame_data
                to_update.append(sprite)
            
            # if the reset flag is true, reset the sequence counter to 0, else increment it by 1. Future logic would be a bit more complex to accomodate for different looping styles.
            if reset_flag:
                self.sprites[sprite][1] = 0
            else:
                self.sprites[sprite][1] += 1
        
        # updating the sprites that needs to be updated, can be made to call _update_sprite for better reusability
        for sprite in to_update:
            width, height = self.sprites[sprite][0].width, self.sprites[sprite][0].height
            x, y = self.sprites[sprite][3], self.sprites[sprite][4]
            data = self.sprites[sprite][2]
            fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
            self.disp.blit(fbuf, x, y)
        self.disp.show()
    
    def _game_update(self, timer):
        # The game update loop, currently empty
        # Main tasks:
        # Polls the inputs
        # Handles input
        # Update the game state
        # Updates the game state, sprite positions and interactions, sprite animation sequence etc and save it in the sprite bundle

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
