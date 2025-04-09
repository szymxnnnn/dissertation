import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, Button
from PIL import Image, ImageTk
import threading

# Load Haar cascades for face detection
face_cascade_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Kalman Filter for smoother tracking
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

# Function for gamma correction
def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

# Function for contrast, brightness, and sharpness adjustment
def enhance_image(image, contrast=1.0, brightness=0, sharpness=1.0):
    adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) * sharpness
    sharpened = cv2.filter2D(adjusted, -1, kernel)
    return sharpened

# Adaptive Histogram Equalization (CLAHE) for better contrast
def apply_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.merge([l, a, b])

# Function to start the camera
def start_camera():
    global cap, running
    if not running:
        cap = cv2.VideoCapture(0)
        running = True
        threading.Thread(target=update_frame, daemon=True).start()

# Function to stop the camera
def stop_camera():
    global cap, running
    running = False
    if cap:
        cap.release()
    canvas.create_image(0, 0, anchor="nw", image=tk_img_placeholder)

# Function to update the video feed
def update_frame():
    global cap, running
    while running:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame = apply_clahe(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces_frontal = face_cascade_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40))
        faces_profile = face_cascade_profile.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        faces = list(faces_frontal) + list(faces_profile)
        
        gamma = gamma_slider.get() / 10.0
        contrast = contrast_slider.get() / 10.0
        brightness = brightness_slider.get() - 50
        sharpness = sharpness_slider.get() / 10.0
        
        for (x, y, w, h) in faces:
            x, y, w, h = max(x-10, 0), max(y-10, 0), min(w+20, frame.shape[1] - x), min(h+20, frame.shape[0] - y)
            
            # Kalman Filter Prediction for Smoother Tracking
            measurement = np.array([[np.float32(x + w/2)], [np.float32(y + h/2)]])
            kalman.correct(measurement)
            prediction = kalman.predict()
            x, y = int(prediction[0] - w/2), int(prediction[1] - h/2)
            
            face_roi = frame[y:y+h, x:x+w]
            face_roi = adjust_gamma(face_roi, gamma=gamma)
            face_roi = enhance_image(face_roi, contrast=contrast, brightness=brightness, sharpness=sharpness)
            frame[y:y+h, x:x+w] = face_roi
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.img = img
        root.update()

root = tk.Tk()
root.title("Enhanced Face Tracking App")
root.configure(bg="#17153B")

canvas = tk.Canvas(root, width=640, height=480, bg="#17153B", highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=4, pady=10)

placeholder_img = Image.new("RGB", (640, 480), "#17153B")
tk_img_placeholder = ImageTk.PhotoImage(placeholder_img)

gamma_slider = Scale(root, from_=1, to=30, orient="horizontal", label="Gamma")
gamma_slider.set(10)
gamma_slider.grid(row=1, column=0)

contrast_slider = Scale(root, from_=1, to=30, orient="horizontal", label="Contrast")
contrast_slider.set(10)
contrast_slider.grid(row=1, column=1)

brightness_slider = Scale(root, from_=0, to=100, orient="horizontal", label="Brightness")
brightness_slider.set(50)
brightness_slider.grid(row=1, column=2)

sharpness_slider = Scale(root, from_=0, to=20, orient="horizontal", label="Sharpness")
sharpness_slider.set(10)
sharpness_slider.grid(row=1, column=3)

start_button = Button(root, text="Start Camera", command=start_camera)
start_button.grid(row=2, column=0, pady=10)

stop_button = Button(root, text="Stop Camera", command=stop_camera)
stop_button.grid(row=2, column=1)

exit_button = Button(root, text="Exit", command=root.quit)
exit_button.grid(row=2, column=2)

cap, running = None, False
root.mainloop()
