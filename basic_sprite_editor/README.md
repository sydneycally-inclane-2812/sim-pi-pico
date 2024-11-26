# Basic Python *(and maybe more)* Sprite Editing Client
This is a supportive client for creating and editing sprites for use with the Pyogotchi project, written in Python. The program allows for create/load existing sprites in different formats, simple editing and save/dump to JSON/bytearray to directly save into the Pi Pico storage.

*Latest version: v2*

*Available in: Python*
## Current features
- Specify if creating new file or opening existing file
- Create a new canvas with specified dimensions
- Draw/erase pixels by clicking and dragging
- Dynamically resize canvas and pixel size
- Show/hide grid numbers based on pixel size
- Save/load JSON
- Dump as bytearray

## Features in progress
- Cleaner starting dialogs
- More informative interface

## Future development
- Web application for better portability, or using a compiled language for better performance
- Improve UI/UX
- Better integrate the development process
    - Allow for the concurrent design of smaller but reusable component sprites
    - Integrate with the game flow design process (adding behavior procedure, events and triggers with external sensors, etc.)
    - Generate code for the behavior for ease of development
