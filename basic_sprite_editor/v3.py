import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import json

# '''
# TODO: 
# [DONE] Fix load function, 
# [DONE] Add create new file and open existing file options, 
# Fix bytearray dump to dump into clipboard,
# Save as txt instead of json,
# Export as image at higher resolution for sharing,
# Add option to dump as hex instead of binary,
# Explicitly force dimensions to be multiples of 8 by rejecting any other values at the canvas size prompt,
# '''

# '''
# Current features:
# - Mildly optimized from previous version
# - Specify if creating new file or opening existing file
# - Create a new canvas with specified dimensions
# - Draw/erase pixels by clicking and dragging
# - Dynamically resize canvas and pixel size
# - Show/hide grid numbers based on pixel size
# - Save/load to CSV
# - Dump as bytearray
# '''

# '''
# Limitations:
# - No undo/redo functionality
# - Implicitly enforce dimensions to be multiples of 8
# '''
class PixelArtApp:
    def __init__(self, root, width, height, pixel_size=20):
        self.root = root
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.show_numbers = True
        self.show_number_threshold = 20
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.draw_pixel)
        self.canvas.bind("<Button-1>", self.draw_pixel)
        self.canvas.bind("<Button-3>", self.erase_pixel)
        self.canvas.bind("<B3-Motion>", self.erase_pixel)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.pixels = [[0 for _ in range(width)] for _ in range(height)]
        self.create_menu()
        self.draw_grid()
        self.redraw_canvas()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        canvas_menu = tk.Menu(menu)
        help_menu = tk.Menu(menu)
        
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save (.JSON/.txt)", command=self.save)
        file_menu.add_command(label="Load (.JSON/.txt)", command=self.load)
        file_menu.add_command(label="Create New Canvas", command=lambda:begin_program('new'))
        file_menu.add_separator()
        file_menu.add_command(label="Copy as Bytearray", command=self.dump_bytearray)
        file_menu.add_command(label="Copy as Hex", command=self.dump_hex) 
        file_menu.add_command(label="Copy as C/C++ Array", command=self.dump_cpp_array) 
        
        menu.add_cascade(label="Canvas", menu=canvas_menu)
        canvas_menu.add_command(label="Clear", command=self.clear_canvas)
        canvas_menu.add_command(label="Invert", command=self.invert_canvas)
        
        menu.add_cascade(label="Documentation", menu=help_menu)
        help_menu.add_command(label="Help", command=self.help)
        help_menu.add_command(label="About", command=self.about)
        
        
    def draw_pixel(self, event):
        x = (event.x - 20) // self.pixel_size
        y = (event.y - 20) // self.pixel_size
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.pixels[y][x] == 0:
                self.pixels[y][x] = 1
                self.canvas.create_rectangle(
                    x * self.pixel_size + 20, y * self.pixel_size + 20,
                    (x + 1) * self.pixel_size + 20, (y + 1) * self.pixel_size + 20,
                    fill='black', outline='black'
                )

    def erase_pixel(self, event):
        x = (event.x - 20) // self.pixel_size
        y = (event.y - 20) // self.pixel_size
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.pixels[y][x] == 1:
                self.pixels[y][x] = 0
                self.canvas.create_rectangle(
                    x * self.pixel_size + 20, y * self.pixel_size + 20,
                    (x + 1) * self.pixel_size + 20, (y + 1) * self.pixel_size + 20,
                    fill='white', outline='gray'
                )
    
    def save(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt"), ("JSON File", "*.json")])
        if file_path:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as file:
                    json.dump(self.pixels, file)
            elif file_path.endswith('.txt'):
                with open(file_path, 'w') as file:
                    for row in self.pixels:
                        file.write(','.join(map(str, row)) + '\n')
        
    def load(self): # Managing the load process
        def _load(file_path): # Actually loading a file from the file path
            buffer = []
            if file_path:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as file:
                        buffer = json.load(file)
                elif file_path.endswith('.txt'):
                    with open(file_path, 'r') as file:
                        buffer = [list(map(int, line.strip().split(','))) for line in file]
                return buffer
                
        def _sync_buffer():
            self.height = len(self.buffer)
            self.width = len(self.buffer[0])
            self.pixels = self.buffer
            self.redraw_canvas()
                
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.buffer = _load(file_path) # Extract the file contents to a buffer
                if len(self.pixels) != len(self.buffer) or len(self.pixels[0]) != len(self.buffer[0]):
                    dialog = tk.Toplevel(self.root)
                    dialog.title("Warning")
                    tk.Label(dialog, text="The dimensions of the loaded file do not match the current canvas size. \n Continuing will overwrite the current canvas. Do you want to continue?").pack(padx=10, pady=10)
                    tk.Button(dialog, text="Continue", command=lambda:[dialog.destroy(), _sync_buffer()]).pack(side=tk.LEFT, padx=10, pady=10)
                    tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
                else:
                    dialog = tk.Toplevel(self.root)
                    dialog.title("Warning")
                    tk.Label(dialog, text="Do you want to overwrite this file?").pack(padx=10, pady=10)
                    tk.Button(dialog, text="Yes", command=lambda:[dialog.destroy(), _sync_buffer()]).pack(side=tk.LEFT, padx=10, pady=10)
                    tk.Button(dialog, text="No", command=dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
    
    def _to_bytearray(self):
        data = bytearray()
        for y in range(self.height):
            for x in range(0, self.width, 8):
                byte = 0
                for i in range(8):
                    if x + i < self.width and self.pixels[y][x + i]:
                        byte |= 1 << (7 - i)
                data.append(byte)
        return data
    
    def dump_bytearray(self):
        data = self._to_bytearray()
        data_str = ', '.join(f'0b{byte:08b}' for byte in data)
        self.root.clipboard_clear()
        self.root.clipboard_append(f"bytearray([{data_str}])")
        messagebox.showinfo("Copy as Bytearray", "Bytearray copied to clipboard")
        self.root.update()

    def dump_cpp_array(self):
        data = self._to_bytearray()
        data_str = ', '.join(f'0x{byte:02x}' for byte in data)
        self.root.clipboard_clear()
        self.root.clipboard_append(f"unsigned char data[] = {{{data_str}}};")
        messagebox.showinfo("Copy as C++ Array", "C++ array copied to clipboard")
        self.root.update()

    def dump_hex(self):
        data = self._to_bytearray()
        data_str = ', '.join(f'0x{byte:02x}' for byte in data)
        self.root.clipboard_clear()
        self.root.clipboard_append(f"[{data_str}]")
        messagebox.showinfo("Copy as Hex","Hex saved to Clipboard")
        self.root.update()        
        
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == 1:
                    self.canvas.create_rectangle(
                        x * self.pixel_size + 20, y * self.pixel_size + 20,
                        (x + 1) * self.pixel_size + 20, (y + 1) * self.pixel_size + 20,
                        fill='black', outline='black'
                    )

    def draw_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                self.canvas.create_rectangle(
                    x * self.pixel_size + 20, y * self.pixel_size + 20,
                    (x + 1) * self.pixel_size + 20, (y + 1) * self.pixel_size + 20,
                    outline='gray'
                )
        if self.show_numbers:
            for i in range(self.width):
                self.canvas.create_text(i * self.pixel_size + 30, 10, text=str(i), fill='black')
            for i in range(self.height):
                self.canvas.create_text(10, i * self.pixel_size + 30, text=str(i), fill='black')

    def resize_canvas(self, event):
        # Calculate new pixel size based on the canvas size
        new_pixel_size = min((event.width - 20) // self.width, (event.height - 20) // self.height)
        if new_pixel_size != self.pixel_size:
            self.pixel_size = new_pixel_size
            self.show_numbers = self.pixel_size >= self.show_number_threshold  # Hide numbers if pixel size is too small
            self.redraw_canvas()
    
    def clear_canvas(self):
        self.pixels = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.redraw_canvas()
    
    def invert_canvas(self):
        self.pixels = [[1 - pixel for pixel in row] for row in self.pixels]
        self.redraw_canvas()

    def help(self):
        text = \
        '''
        This is a simple pixel art editor that allows you to create monochromic sprites. \n
        To draw, left click and drag the mouse over the canvas. \n
        To erase, right click and drag the mouse. \n
        
        To save your work, click on the File menu and select Save, then specify the file name and format you want. It is recommended to save as a .txt file. \n
        
        To load a saved file, click on the File menu and select Load, then navigate to the file you want to load. To create a new canvas, click on the File menu and select Create New Canvas, then specify the dimensions of the new canvas.
        
        You can also quickly share your work by copying it as a bytearray or hex string. Click on the File menu and select Copy as Bytearray or Copy as Hex. Bytearray is useful for MicroPython and other embedded projects, while hex string is useful for C/C++ projects.
        
        To clear the canvas or invert the colors, click on the Canvas menu and select Clear or Invert. \n
        For any problem or suggestion, please contact the developer. \n
        If your name starts with T, I am very thankful for your help in this project. Any feature requests please let me know.
        
        If you have a problem when the program doesn't show the new canvas properly after an import, I recommend resizing the window a little bit so it can refresh the canvas.
        I am working on a fix. 
        '''
        messagebox.showinfo("Help", text)
    
    def about(self):
        text = \
        '''
        Sprite Editor v3.0 - Part of the Pyogotchi project
        Hung Dat Tran
        Email: saigondese3000.aus@duck.com
        '''
        messagebox.showinfo("About", text)
        
def get_canvas_size():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    dialog = tk.Toplevel(root)
    dialog.title("Canvas Size")
    tk.Label(dialog, text="Both dimensions will automatically be rounded to the nearest multiple of eight.", font=('Helvetica', 10, 'italic')).pack(padx=10, pady=5)
    tk.Label(dialog, text="Enter canvas width (in pixels):", font=('Helvetica', 10)).pack(padx=10, pady=5)
    width_entry = tk.Entry(dialog)
    width_entry.pack(padx=10, pady=5)

    tk.Label(dialog, text="Enter canvas height (in pixels):", font=('Helvetica', 10)).pack(padx=10, pady=5)
    height_entry = tk.Entry(dialog)
    height_entry.pack(padx=10, pady=5)

    width, height = 0, 0
    def on_ok():
        nonlocal width, height
        width = int(width_entry.get())
        height = int(height_entry.get())
        # Force dimensions to be multiples of 8
        width = (width + 7) // 8 * 8
        height = (height + 7) // 8 * 8
        dialog.destroy()
        root.quit()
        

    tk.Button(dialog, text="OK", command=on_ok).pack(pady=10)

    root.mainloop()
    root.destroy()

    return width, height

def choose_action():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    action = None

    def new_canvas():
        nonlocal action
        action = 'new'
        root.quit()

    def open_file():
        nonlocal action
        action = 'open'
        root.quit()

    dialog = tk.Toplevel(root)
    dialog.title("Choose Action")
    tk.Label(dialog, text="Choose an action:").pack(pady=10)
    tk.Button(dialog, text="New Canvas", command=new_canvas).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(dialog, text="Open File", command=open_file).pack(side=tk.RIGHT, padx=10, pady=10)
    root.mainloop()
    root.destroy()
    return action

def stop_program(root):
    if root:
        root.quit()
        root.destroy()

def begin_program(action = None):
    if action is None:
        action = choose_action()
    if action == 'new':
        width, height = get_canvas_size()
        root = tk.Tk()
        root.title("Pixel Art Editor")
        root.geometry("1024x800")  # Set initial window size
        app = PixelArtApp(root, width, height)
        root.mainloop()
    elif action == 'open':
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")])
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as file:
                        buffer = json.load(file)
                elif file_path.endswith('.txt'):
                    with open(file_path, 'r') as file:
                        buffer = [list(map(int, line.strip().split(','))) for line in file]
            except Exception as e:
                root = tk.Tk()
                dialog = tk.Toplevel(root)
                dialog.title("Error")
                tk.Label(dialog, text=f"Failed to load file: {e}").pack(padx=10, pady=10)
                tk.Button(dialog, text="OK", command=lambda: [dialog.destroy(), root.destroy(), begin_program()]).pack(pady=10)
                root.withdraw()
                root.mainloop()  # Start the Tkinter event loop to show the dialog
            else:
                width = len(buffer[0])
                height = len(buffer)
                root = tk.Tk()
                root.title("Pixel Art Editor")
                root.geometry("1024x800+200+200")  # Set initial window size
                root.protocol("WM_DELETE_WINDOW", lambda: stop_program(root))
                app = PixelArtApp(root, width, height)
                app.pixels = buffer
                app.redraw_canvas()
                root.mainloop()
            finally:
                stop_program(root)

if __name__ == "__main__":
    begin_program()    
        