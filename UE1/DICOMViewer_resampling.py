import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pydicom
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import ndimage


# Function that displays the DICOM images
def display_dicom_image():
    directory = filedialog.askdirectory()
    if directory:
        dicom_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if
                       filename.lower().endswith('.dcm')]
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


def apply_down_upsampling(image, order=0):
    if order is None:
        return image
    downsampled = ndimage.zoom(image, zoom=0.25, order=order)
    upsampled = ndimage.zoom(downsampled, zoom=4, order=order)

    return upsampled


def get_order_from_input(selection):
    if selection == "nearest-neighbor":
        return 0
    elif selection == "bilinear-interpolation":
        return 1
    elif selection == "cubic-interpolation":
        return 2
    else:
        return None


# Function that displays a single slice at a time
def display_slice(slice_number):
    ax.clear()
    slice = ct_data[slice_number]
    order_input = get_order_from_input(filter_var.get())
    slice = apply_down_upsampling(slice, order=order_input)
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
slice_slider = tk.Scale(frame, from_=0, to=0, orient="horizontal", length=app.winfo_width() - 2 * 20,
                        command=lambda x: display_slice(slice_slider.get()))
slice_slider.grid(row=2, column=0)
slice_label = ttk.Label(frame, text="", foreground="black")
slice_label.grid(row=3, column=0)

###################################### ADDED
# selecting interpolation order
filter_label = tk.Label(frame, text="Select interpolation method:")
filter_label.grid(row=4, column=0, padx=10, pady=(10, 0))
filter_var = tk.StringVar()
filter_var.set("off")
filter_menu = ttk.OptionMenu(frame, filter_var, "off", "off", "nearest-neighbor", "bilinear-interpolation",
                             "cubic-interpolation")
filter_menu.grid(row=5, column=0, padx=10)
slice_label.grid(row=6, column=0)
###################################### ADDED

app.mainloop()
