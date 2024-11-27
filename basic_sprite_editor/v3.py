import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import json

# '''
# TODO: 
# Fix load function, 
# Add create new file and open existing file options, 
# Fix bytearray dump to dump into clipboard,
# Save as txt instead of json,
# Export as image at higher resolution for sharing,
# Add option to dump as hex instead of binary,
# '''

# '''
# Current features:
# - Mildly optimized from previous version
# - Specify if creating new file or opening existing file
# - Create a new canvas with specified dimensions
# - Draw/erase pixels by clicking and dragging
# - Dynamically resize canvas and pixel size
# - Show/hide grid numbers based on pixel size
# - Save/load to JSON
# - Dump as bytearray
# '''

# '''
# Limitations:
# - No undo/redo functionality
# - Enforce dimensions to be multiples of 8
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
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save)
        file_menu.add_command(label="Load", command=self.load)
        file_menu.add_command(label="Dump as Bytearray", command=self.dump_bytearray) # Should be copy to clipboard as bytearray
        # Add copy to clipboard as hex
        # Add save as txt
        # Add export as image at higher resolution
        
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
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.pixels, file)

    def load(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        
        if file_path:
            with open(file_path, 'r') as file:
                self.pixels = json.load(file)
            self.redraw_canvas()

    def dump_bytearray(self):
        bytearray_data = self.convert_to_bytearray()
        bytearray_str = ', '.join(f'0b{byte:08b}' for byte in bytearray_data)
        messagebox.showinfo("Bytearray Dump", f"bytearray([{bytearray_str}])")

    def convert_to_bytearray(self):
        bytearray_data = bytearray()
        for y in range(self.height):
            for x in range(0, self.width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < self.width and self.pixels[y][x + bit]:
                        byte |= (1 << (7 - bit))
                bytearray_data.append(byte)
        return bytearray_data

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

def get_canvas_size():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    width = simpledialog.askinteger("Canvas Size", "Enter canvas width (in pixels):", minvalue=1, maxvalue=150)
    height = simpledialog.askinteger("Canvas Size", "Enter canvas height (in pixels):", minvalue=1, maxvalue=150)
    root.destroy()
    # Force dimensions to be multiples of 8
    width = (width + 7) // 8 * 8
    height = (height + 7) // 8 * 8
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

if __name__ == "__main__":
    action = choose_action()
    if action == 'new':
        width, height = get_canvas_size()
        root = tk.Tk()
        root.title("Pixel Art Editor")
        root.geometry("800x600")  # Set initial window size
        app = PixelArtApp(root, width, height)
        root.mainloop()
    elif action == 'open':
        root = tk.Tk()
        root.title("Pixel Art Editor")
        root.geometry("800x600")  # Set initial window size
        # TODO: load should get the dimensions first, initialize the canvas then load the file.
        app = PixelArtApp(root, 8, 8)  # Temporary size, will be updated on load
        app.load()
        root.mainloop()
        