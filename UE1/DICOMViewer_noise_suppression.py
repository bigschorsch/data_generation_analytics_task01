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


# visit: https://docs.scipy.org/doc/scipy-1.11.3/reference/generated/scipy.ndimage.median_filter.html
## size: shape that is taken from the input array at every element position (input for filter)
## footprint: boolean array, that specifies a shape
## mode: how input-array is extended beyond its boundaries ('reflect', 'constant', 'nearest', 'mirror', 'wrap')
## axes: filter along specified axes
# https://docs.scipy.org/doc/scipy-1.11.3/reference/generated/scipy.ndimage.uniform_filter.html
## similar to median
# https://docs.scipy.org/doc/scipy-1.11.3/reference/generated/scipy.ndimage.gaussian_filter.html
## sigma
## order (0 => normal smoothing, 1=> highlight gradients, 2=> highlight rapid changes)
## radius (of the gaussian kernel)
def apply_filter(slice_data, filter_type='MED', param=3, mode='reflect', axes=None, order=0, radius=2):
    if filter_type == 'MED':
        return ndimage.median_filter(slice_data, size=param, mode=mode, axes=axes)
    if filter_type == 'AVG':
        return ndimage.uniform_filter(slice_data, size=param, mode=mode, axes=axes)
    if filter_type == 'GAUS':
        return ndimage.gaussian_filter(slice_data, sigma=param, order=order, radius=radius,
                                       mode=mode, axes=axes)
    return slice_data


def get_axes_from_input(selection):
    if selection == "x":
        return (1,)
    elif selection == "y":
        return (0,)
    else:
        return None  # filtering at both axes


# Function that displays a single slice at a time
def display_slice(slice_number):
    ax.clear()
    sliced_image = ct_data[slice_number]

    filter_type = filter_var.get()
    mode = mode_var.get()
    param = float(param_entry.get()) if filter_type == 'GAUS' else int(param_entry.get())
    axes = get_axes_from_input(axes_var.get())
    order_val = int(order_entry.get()) if filter_type == 'GAUS' else 0
    radius_val = int(radius_entry.get()) if filter_type == 'GAUS' else 4.0

    sliced_image = apply_filter(sliced_image, filter_type, param, mode, axes, order_val, radius_val)
    ax.imshow(sliced_image, cmap='gray')
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

########################## ADDED
# selecting filter-type
filter_var = tk.StringVar()
filter_var.set("MED")
filter_menu = ttk.OptionMenu(frame, filter_var, "MED", "MED", "AVG", "GAUS")
filter_menu.grid(row=0, column=1, padx=10)

# selecting size/sigma
radius_label = ttk.Label(frame, text="Size/Sigma:")
radius_label.grid(row=1, column=1, padx=5)
param_entry = ttk.Entry(frame, width=5)
param_entry.grid(row=1, column=2)
param_entry.insert(0, "3")

# selecting mode
mode_var = tk.StringVar()
mode_var.set("reflect")
mode_menu = ttk.OptionMenu(frame, mode_var, "reflect", "constant", "nearest", "mirror", "wrap")
mode_menu.grid(row=0, column=3, padx=10)

# selecting axes
radius_label = ttk.Label(frame, text="Axes:")
radius_label.grid(row=2, column=1, padx=5)
axes_var = tk.StringVar()
axes_var.set("both")
axes_menu = ttk.OptionMenu(frame, axes_var, "both", "x", "y", "both")
axes_menu.grid(row=2, column=2, padx=5)

# select order
order_label = ttk.Label(frame, text="Order:")
order_label.grid(row=3, column=1, padx=5)
order_entry = ttk.Entry(frame, width=5)
order_entry.grid(row=3, column=2)
order_entry.insert(0, "0")

# select radius
radius_label = ttk.Label(frame, text="Radius:")  ## nur sichtbar mit sigma=1 und order=1 und sehr großem Unterschied
radius_label.grid(row=4, column=1, padx=5)
radius_entry = ttk.Entry(frame, width=5)
radius_entry.grid(row=4, column=2)
radius_entry.insert(0, "1")
########################## ADDED

app.mainloop()
