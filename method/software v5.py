import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Function to perform automatic exposure and contrast correction
def automatic_exposure_contrast_correction(image, mode="exposure"):
    if mode == "exposure":
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)  # Convert to LAB color space
        l, a, b = cv2.split(lab)  # Split channels
        l = cv2.equalizeHist(l)  # Apply histogram equalization to the L channel
        corrected_image = cv2.merge((l, a, b))  # Merge channels back
        corrected_image = cv2.cvtColor(corrected_image, cv2.COLOR_LAB2BGR)  # Convert back to BGR
    else:
        alpha = 1.5  # Contrast control (1.0-3.0)
        beta = 0    # Brightness control (0-100)
        corrected_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)  # Apply contrast correction
    
    return corrected_image

# Function to open an image and update the UI
def open_image():
    global original_image, displayed_image
    file_path = filedialog.askopenfilename()  # Open file dialog to select an image
    if not file_path:
        return
    original_image = cv2.imread(file_path)  # Read the selected image
    if original_image is None:
        print("Error: Image not found or could not be loaded.")
        return
    displayed_image = original_image.copy()
    display_image(displayed_image)
    show_buttons()
    btn_close.grid(row=0, column=1, padx=5, pady=5)  # Show the close button
    root.geometry("1000x800")  # Resize window to accommodate larger images
    btn_open.config(text="Re-Select Image")  # Change button text after image selection
    center_window(root, 1000, 800)  # Center window after resizing

# Function to close the displayed image
def close_image():
    global original_image, displayed_image
    original_image = None
    displayed_image = None
    label_image.config(image="")  # Remove the displayed image
    btn_open.config(text="Select Image")  # Reset button text
    btn_close.grid_remove()  # Hide the close button
    button_frame.pack_forget()  # Hide the correction buttons
    root.geometry("500x400")  # Resize window back to initial size
    center_window(root, 500, 400)  # Center window after resizing

# Function to apply the selected correction method
def correct_image():
    global displayed_image, correction_mode
    if original_image is not None:
        displayed_image = automatic_exposure_contrast_correction(original_image, mode=correction_mode)
        display_image(displayed_image)

# Function to reset the image back to original
def reset_image():
    global displayed_image
    if original_image is not None:
        displayed_image = original_image.copy()
        display_image(displayed_image)

# Function to switch between exposure and contrast correction
def switch_mode():
    global correction_mode
    correction_mode = "contrast" if correction_mode == "exposure" else "exposure"
    mode_button.config(text=f"Mode: {correction_mode.capitalize()}")

# Function to display an image in the GUI
def display_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for Tkinter compatibility
    image = ImageTk.PhotoImage(Image.fromarray(image))
    label_image.config(image=image)
    label_image.image = image  # Keep reference to avoid garbage collection

# Function to show buttons after an image is selected
def show_buttons():
    button_frame.pack()

# Function to center the window on the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Initialize global variables
original_image = None
displayed_image = None
correction_mode = "exposure"

# Create the main application window
root = tk.Tk()
root.title("Vulnerablility scanner")
center_window(root, 500, 400)  # Center initial window
root.configure(bg="#727D73")

# Frame for image selection button
frame = tk.Frame(root, bg="#727D73")
frame.pack(pady=20)

# Frame for buttons (aligned in a row)
button_frame = tk.Frame(root, bg="#727D73")

# Function to create rounded buttons
def create_rounded_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg="#D0DDD0", fg="black", relief="flat", borderwidth=5, highlightbackground="#D0DDD0", highlightthickness=2, padx=10, pady=5)

# Button to open or re-select an image
btn_open = create_rounded_button(frame, "Load Dataset", open_image)
btn_open.grid(row=0, column=0, padx=5, pady=5)

# Button to open or re-select an image
btn_open = create_rounded_button(frame, "Run vulnerablility Scan", open_image)
btn_open.grid(row=10, column=0, padx=5, pady=5)


# Button to open or re-select an image
btn_open = create_rounded_button(frame, "Generate Report", open_image)
btn_open.grid(row=20, column=0, padx=5, pady=5)

# Button to open or re-select an image
btn_open = create_rounded_button(frame, "Exit", open_image)
btn_open.grid(row=30, column=0, padx=5, pady=5)





# Button to close the image (initially hidden)
btn_close = create_rounded_button(frame, "Close Image", close_image)
btn_close.grid(row=0, column=1, padx=5, pady=5)
btn_close.grid_remove()

# Correction, Reset, and Mode Switch buttons
btn_correct = create_rounded_button(button_frame, "Correct", correct_image)
btn_reset = create_rounded_button(button_frame, "Reset", reset_image)
mode_button = create_rounded_button(button_frame, f"Mode: {correction_mode.capitalize()}", switch_mode)

# Align buttons in a row
btn_correct.grid(row=0, column=0, padx=5, pady=5)
btn_reset.grid(row=0, column=1, padx=5, pady=5)
mode_button.grid(row=0, column=2, padx=5, pady=5)

# Label to display the selected image
label_image = tk.Label(root, bg="#727D73")
label_image.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
