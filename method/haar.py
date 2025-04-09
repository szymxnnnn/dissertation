import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, Button
from PIL import Image, ImageTk

# Load Haar cascades for face detection
face_cascade_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Function for gamma correction
def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

# Function for contrast and brightness adjustment
def adjust_contrast_brightness(image, contrast=1.0, brightness=0):
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

# Function to start the camera
def start_camera():
    global cap, running
    if not running:
        cap = cv2.VideoCapture(0)
        running = True
        update_frame()

# Function to stop the camera
def stop_camera():
    global cap, running
    if running:
        running = False
        cap.release()
        canvas.create_image(0, 0, anchor="nw", image=tk_img_placeholder)

# Function to update the video feed
def update_frame():
    global cap, running
    if running:
        ret, frame = cap.read()
        if not ret:
            return

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces from multiple angles
        faces_frontal = face_cascade_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40))
        faces_profile = face_cascade_profile.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        faces = list(faces_frontal) + list(faces_profile)

        # Get values from GUI sliders
        gamma = gamma_slider.get() / 10.0
        contrast = contrast_slider.get() / 10.0
        brightness = brightness_slider.get() - 50

        for (x, y, w, h) in faces:
            # Expand face box slightly
            x, y, w, h = max(x-10, 0), max(y-10, 0), min(w+20, frame.shape[1] - x), min(h+20, frame.shape[0] - y)

            # Extract and adjust face region
            face_roi = frame[y:y+h, x:x+w]
            face_roi = adjust_gamma(face_roi, gamma=gamma)
            face_roi = adjust_contrast_brightness(face_roi, contrast=contrast, brightness=brightness)

            # Replace the processed face back
            frame[y:y+h, x:x+w] = face_roi

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert frame to Tkinter format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)

        # Update canvas with new frame
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.img = img  # Keep a reference

        # Continue updating
        root.after(10, update_frame)

# Initialize Tkinter window
root = tk.Tk()
root.title("Face Tracking App")

# Set background color
root.configure(bg="#17153B")

# Create a canvas for video feed
canvas = tk.Canvas(root, width=640, height=480, bg="#17153B", highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=3, pady=10)

# Placeholder image when camera is off
placeholder_img = Image.new("RGB", (640, 480), "#17153B")
tk_img_placeholder = ImageTk.PhotoImage(placeholder_img)

# Define widget styles
slider_bg = "#2E236C"
slider_fg = "white"
button_bg = "#2E236C"
button_fg = "white"

# Add sliders for gamma, contrast, and brightness
gamma_slider = Scale(root, from_=1, to=30, orient="horizontal", label="Gamma", bg=slider_bg, fg=slider_fg, troughcolor="#17153B")
gamma_slider.set(10)
gamma_slider.grid(row=1, column=0, padx=5, pady=5)

contrast_slider = Scale(root, from_=1, to=30, orient="horizontal", label="Contrast", bg=slider_bg, fg=slider_fg, troughcolor="#17153B")
contrast_slider.set(10)
contrast_slider.grid(row=1, column=1, padx=5, pady=5)

brightness_slider = Scale(root, from_=0, to=100, orient="horizontal", label="Brightness", bg=slider_bg, fg=slider_fg, troughcolor="#17153B")
brightness_slider.set(50)
brightness_slider.grid(row=1, column=2, padx=5, pady=5)

# Add buttons to start/stop the camera
start_button = Button(root, text="Start Camera", command=start_camera, bg=button_bg, fg=button_fg, relief="raised")
start_button.grid(row=2, column=0, padx=5, pady=10)

stop_button = Button(root, text="Stop Camera", command=stop_camera, bg=button_bg, fg=button_fg, relief="raised")
stop_button.grid(row=2, column=1, padx=5, pady=10)

exit_button = Button(root, text="Exit", command=root.quit, bg=button_bg, fg=button_fg, relief="raised")
exit_button.grid(row=2, column=2, padx=5, pady=10)

# Global variables for camera
cap = None
running = False

# Run the Tkinter main loop
root.mainloop()
