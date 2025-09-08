import tkinter as tk
from tkinter import ttk

class TransparentRegionSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Region Selector")

        # Try transparent background
        try:
            self.root.attributes("-transparentcolor", "white")
        except tk.TclError:
            print("⚠ Transparent color not supported. The background will stay visible.")

        self.root.config(bg="white")
        self.root.attributes("-topmost", True)
        self.root.geometry("400x300+100+100")
        self.root.overrideredirect(True)  # No title bar

        # Canvas covers entire window
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Label with background for coordinates
        self.coord_label = self.canvas.create_text(
            0, 0, anchor="center", text="", fill="black",
            font=("Segoe UI", 12, "bold"), tags="coord"
        )
        self.coord_bg = self.canvas.create_rectangle(0, 0, 0, 0, fill="yellow", outline="", tags="coord_bg")
        self.canvas.tag_raise(self.coord_label)  # text above bg

        # Style for ttk buttons
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

        # Quit button (bottom-left)
        self.quit_btn = ttk.Button(self.root, text="Quit", command=self.root.destroy)
        self.quit_btn.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        # Copy button (bottom-right)
        self.copy_btn = ttk.Button(self.root, text="Copy", command=self.copy_to_clipboard)
        self.copy_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.bind("<Button-3>", self.start_resize)
        self.canvas.bind("<B3-Motion>", self.do_resize)

        # Keyboard shortcuts
        self.root.bind("<Return>", self.copy_to_clipboard)  # Enter = copy region
        self.root.bind("<Escape>", lambda e: self.root.destroy())  # Esc = quit

        self._drag_data = {"x": 0, "y": 0}
        self._resize_data = {"x": 0, "y": 0, "w": 0, "h": 0}

        # Update loop
        self.update_overlay()

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_move(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._resize_data["x"] = event.x
        self._resize_data["y"] = event.y
        self._resize_data["w"] = self.root.winfo_width()
        self._resize_data["h"] = self.root.winfo_height()

    def do_resize(self, event):
        dx = event.x - self._resize_data["x"]
        dy = event.y - self._resize_data["y"]
        new_w = max(100, self._resize_data["w"] + dx)
        new_h = max(80, self._resize_data["h"] + dy)
        self.root.geometry(f"{new_w}x{new_h}+{self.root.winfo_x()}+{self.root.winfo_y()}")

    def update_overlay(self):
        self.canvas.delete("border")

        # Draw thick blue border
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.canvas.create_rectangle(0, 0, w, h, outline="blue", width=15, tags="border")

        # Update coordinates with background
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        text = f"(x={x}, y={y}, w={w}, h={h})"
        self.canvas.itemconfig(self.coord_label, text=text)

        # Center text
        self.canvas.coords(self.coord_label, w/2, h/2)

        # Update background rectangle for text
        bbox = self.canvas.bbox(self.coord_label)
        if bbox:
            self.canvas.coords(self.coord_bg, bbox[0]-5, bbox[1]-2, bbox[2]+5, bbox[3]+2)
        self.canvas.tag_lower(self.coord_bg, self.coord_label)

        self.root.after(100, self.update_overlay)

    def copy_to_clipboard(self, event=None):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        region = f"({x}, {y}, {w}, {h})"
        self.root.clipboard_clear()
        self.root.clipboard_append(region)
        print("📋 Copied:", region)


if __name__ == "__main__":
    root = tk.Tk()
    app = TransparentRegionSelector(root)
    root.mainloop()
