import tkinter as tk
from tkinter import filedialog
import ui_func as func

if __name__ == "__main__":
    root = tk.Tk()

    # Open a file dialog to choose an image
    file_path = filedialog.askopenfilename(title="Select Image File")

    if file_path:
        image_editor = func.ImageEditor(root, file_path)
        root.mainloop()