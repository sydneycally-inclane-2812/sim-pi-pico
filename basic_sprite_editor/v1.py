import tkinter as tk
from tkinter import simpledialog, filedialog
import json

class PixelArtApp:
    def __init__(self, root, width, height, pixel_size=20):
        self.root = root
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.show_numbers = pixel_size >= 40
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.draw_pixel)
        self.canvas.bind("<Button-1>", self.draw_pixel)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.pixels = [[0 for _ in range(width)] for _ in range(height)]
        self.create_menu()
        self.draw_grid()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save JSON", command=self.saveJSON)
        file_menu.add_command(label="Load JSON", command=self.loadJSON)
        file_menu.add_command(label="Save Byte Array", command=self.saveBA)
        file_menu.add_command(label="Load Byte Array", command=self.loadBA)
        file_menu.add_command(label="Clear", command=self.clear)

    def draw_pixel(self, event):
        x = (event.x - 20) // self.pixel_size
        y = (event.y - 20) // self.pixel_size
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = 1
            self.canvas.create_rectangle(
                x * self.pixel_size + 20, y * self.pixel_size + 20,
                (x + 1) * self.pixel_size + 20, (y + 1) * self.pixel_size + 20,
                fill='black', outline='black'
            )

    def saveJSON(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.pixels, file)

    def loadJSON(self):
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

    def saveBA(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                for row in self.pixels:
                    file.write(''.join(map(str, row)) + '\n')
    
    def loadBA(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text file", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.pixels = [[int(c) for c in line.strip()] for line in file]
            self.redraw_canvas()
    
    def clear(self):
        self.pixels = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.redraw_canvas()

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
            self.show_numbers = self.pixel_size >= 40  # Hide numbers if pixel size is too small
            self.redraw_canvas()

    def init_action():
        root = tk.Tk()
        root.withdraw()
        action = None
        def new():
            nonlocal action
            action = 'new'
            root.quit()
        def load():
            nonlocal action
            action = 'load'
            root.quit()
        dialog = tk.Toplevel(root)
        dialog.title("Create new canvas or load existing one")
        tk.Label(dialog, text="Choose Action:").pack()
def get_canvas_size():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    width = simpledialog.askinteger("Canvas Size", "Enter canvas width (in pixels):", minvalue=1, maxvalue=300)
    height = simpledialog.askinteger("Canvas Size", "Enter canvas height (in pixels):", minvalue=1, maxvalue=128)
    root.destroy()
    width = (width + 7) // 8 * 8  # Round up to the nearest multiple of 8
    height = (height + 7) // 8 * 8
    return width, height

if __name__ == "__main__":
    width, height = get_canvas_size()
    root = tk.Tk()
    root.title("Pixel Art Editor")
    root.geometry("1024x768")  # Set initial window size
    app = PixelArtApp(root, width, height)
    root.mainloop()