import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pydicom
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Function that displays the DICOM images
def display_dicom_image():
    directory = filedialog.askdirectory()
    if directory:
        dicom_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith('.dcm')]
        if dicom_files:
            dicom_files.sort()
            global ct_data
            ct_data = load_ct_volume(dicom_files)
            display_slice(0)
            slice_slider.config(to=len(ct_data) - 1)
            slice_label.config(text="")
        else:
            slice_label.config(text="No DICOM files found in the selected directory")

# Function that loads the CT volume (in the form of an entire folder)
def load_ct_volume(dicom_files):
    ct_slices = [pydicom.dcmread(file_path).pixel_array for file_path in dicom_files]
    return ct_slices

# Function that displays a single slice at a time
def display_slice(slice_number):
    ax.clear()
    slice = ct_data[slice_number]
    ax.imshow(slice, cmap='gray')
    canvas.draw()
    slice_label.config(text=f"Slice {slice_number}/{len(ct_data) - 1}")

# UI --- no need to touch this part (unless you want to make UI changes)
app = tk.Tk()
app.title("DICOM Viewer")

frame = ttk.Frame(app)
frame.pack(expand=True, fill='both')
display_button = ttk.Button(frame, text="Load DICOM", command=display_dicom_image)
display_button.grid(row=0, column=0)

fig = Figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().grid(row=1, column=0)

app.update()
slice_slider = tk.Scale(frame, from_=0, to=0, orient="horizontal", length=app.winfo_width()-2*20,
                         command=lambda x: display_slice(slice_slider.get()))
slice_slider.grid(row=2, column=0)
slice_label = ttk.Label(frame, text="", foreground="black")
slice_label.grid(row=3, column=0)

app.mainloop()
