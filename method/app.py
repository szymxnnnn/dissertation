import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
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
        alpha = 1.2  # Contrast control (1.0-3.0), reduced from 1.5 to 1.2
        beta = 10    # Brightness control (0-100), increased from 0 to 10
        corrected_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)  # Apply contrast correction

    return corrected_image

# Function to open an image and update the UI
def open_image():
    global original_image, displayed_image, is_video
    is_video = False
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])  # Open file dialog to select an image
    if not file_path:
        return
    original_image = cv2.imread(file_path)  # Read the selected image
    if original_image is None:
        messagebox.showerror("Error", "Image not found or could not be loaded.")
        return
    displayed_image = original_image.copy()
    display_image(displayed_image)
    show_buttons()
    btn_close.grid(row=0, column=2, padx=5, pady=5)  # Show the close button
    root.geometry("1000x800")  # Resize window to accommodate larger images
    btn_open_image.config(text="Re-Select Image")  # Change button text after image selection
    center_window(root, 1000, 800)  # Center window after resizing

# Function to open a video and update the UI
def open_video():
    global video_capture, is_video
    is_video = True
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])  # Open file dialog to select a video
    if not file_path:
        return
    video_capture = cv2.VideoCapture(file_path)  # Open the selected video
    if not video_capture.isOpened():
        messagebox.showerror("Error", "Video not found or could not be loaded.")
        return
    show_buttons()
    btn_close.grid(row=0, column=2, padx=5, pady=5)  # Show the close button
    root.geometry("1000x800")  # Resize window to accommodate larger images
    btn_open_video.config(text="Re-Select Video")  # Change button text after video selection
    center_window(root, 1000, 800)  # Center window after resizing
    play_video()

# Function to play the video
def play_video():
    global video_capture, is_video
    if is_video and video_capture.isOpened():
        ret, frame = video_capture.read()
        if ret:
            display_image(frame)
            label_image.after(30, play_video)  # Schedule the next frame display
        else:
            video_capture.release()
            is_video = False
            btn_close.grid_remove()  # Hide the close button
            button_frame.pack_forget()  # Hide the correction buttons
            root.geometry("500x400")  # Resize window back to initial size
            center_window(root, 500, 400)  # Center window after resizing

# Function to close the displayed image or video
def close_image():
    global original_image, displayed_image, video_capture, is_video
    original_image = None
    displayed_image = None
    if is_video:
        video_capture.release()
        is_video = False
    label_image.config(image="")  # Remove the displayed image
    btn_open_image.config(text="Select Image")  # Reset button text
    btn_open_video.config(text="Select Video")  # Reset button text
    btn_close.grid_remove()  # Hide the close button
    button_frame.pack_forget()  # Hide the correction buttons
    root.geometry("500x400")  # Resize window back to initial size
    center_window(root, 500, 400)  # Center window after resizing

# Function to apply the selected correction method
def correct_image():
    global displayed_image, correction_mode
    if is_video:
        play_video_with_correction()
    elif original_image is not None:
        displayed_image = automatic_exposure_contrast_correction(original_image, mode=correction_mode)
        display_image(displayed_image)

# Function to play the video with correction
def play_video_with_correction():
    global video_capture, is_video
    if is_video and video_capture.isOpened():
        ret, frame = video_capture.read()
        if ret:
            corrected_frame = automatic_exposure_contrast_correction(frame, mode=correction_mode)
            display_image(corrected_frame)
            label_image.after(30, play_video_with_correction)  # Schedule the next frame display
        else:
            video_capture.release()
            is_video = False
            btn_close.grid_remove()  # Hide the close button
            button_frame.pack_forget()  # Hide the correction buttons
            root.geometry("500x400")  # Resize window back to initial size
            center_window(root, 500, 400)  # Center window after resizing

# Function to reset the image back to original
def reset_image():
    global displayed_image
    if original_image is not None:
        displayed_image = original_image.copy()
        display_image(displayed_image)
    elif is_video:
        play_video()

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
video_capture = None
is_video = False
correction_mode = "exposure"

# Create the main application window
root = tk.Tk()
root.title("Exposure & Contrast Correction")
center_window(root, 500, 400)  # Center initial window
root.configure(bg="#727D73")

# Frame for image/video selection button
frame = tk.Frame(root, bg="#727D73")
frame.pack(pady=20)

# Frame for buttons (aligned in a row)
button_frame = tk.Frame(root, bg="#727D73")

# Function to create rounded buttons
def create_rounded_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg="#D0DDD0", fg="black", relief="flat", borderwidth=5, highlightbackground="#D0DDD0", highlightthickness=2, padx=10, pady=5)

# Button to open or re-select an image
btn_open_image = create_rounded_button(frame, "Select Image", open_image)
btn_open_image.grid(row=0, column=0, padx=5, pady=5)

# Button to open or re-select a video
btn_open_video = create_rounded_button(frame, "Select Video", open_video)
btn_open_video.grid(row=0, column=1, padx=5, pady=5)

# Button to close the image/video (initially hidden)
btn_close = create_rounded_button(frame, "Close Image/Video", close_image)
btn_close.grid(row=0, column=2, padx=5, pady=5)
btn_close.grid_remove()

# Correction, Reset, and Mode Switch buttons
btn_correct = create_rounded_button(button_frame, "Correct", correct_image)
btn_reset = create_rounded_button(button_frame, "Reset", reset_image)
mode_button = create_rounded_button(button_frame, f"Mode: {correction_mode.capitalize()}", switch_mode)

# Align buttons in a row
btn_correct.grid(row=0, column=0, padx=5, pady=5)
btn_reset.grid(row=0, column=1, padx=5, pady=5)
mode_button.grid(row=0, column=2, padx=5, pady=5)

# Label to display the selected image/video
label_image = tk.Label(root, bg="#727D73")
label_image.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
