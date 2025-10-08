# rpi_ocr_tts.py
# An enhanced version of the OCR script that adds text-to-speech (TTS)
# functionality to speak the recognized word aloud.

import cv2
import pytesseract
import serial
import serial.tools.list_ports
import time
import sys
import pyttsx3  # <-- New import for Text-to-Speech

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
TESSERACT_CONFIG = r'--oem 3 --psm 7'

# --- TTS Initialization ---
# Initialize the TTS engine once at the start.
print("Initializing Text-to-Speech engine...")
try:
    tts_engine = pyttsx3.init()
    # Optional: Adjust the speech rate (words per minute)
    # tts_engine.setProperty('rate', 150)
    print("TTS engine initialized successfully.")
except Exception as e:
    print(f"Could not initialize TTS engine: {e}")
    tts_engine = None

# --- Serial Port Initialization ---
ser = None
try:
    print(f"Attempting to connect to serial device on {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
    print("Successfully connected to serial device.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
    available_ports = serial.tools.list_ports.comports()
    print("Available serial ports:", [port.device for port in available_ports])
    print("Warning: Serial communication is disabled.")

# --- Camera Initialization ---
camera_index = 0
if len(sys.argv) > 1:
    try:
        camera_index = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid camera index. Using default 0.")

print(f"Attempting to initialize camera at index: {camera_index}...")
cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

if not cap.isOpened():
    print(f"Error: Could not open camera at index {camera_index}.")
    if ser and ser.is_open:
        ser.close()
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("Camera initialized successfully.")

# --- Main Application Loop ---
print("\n--- INSTRUCTIONS ---")
print("1. A window with the camera feed will open.")
print("2. Position the text you want to read inside the green rectangle.")
print("3. Press the [SPACEBAR] to capture, recognize, speak, and send the text.")
print("4. Press [q] to quit the application.")
print("--------------------\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    frame_height, frame_width, _ = frame.shape
    roi_width = int(frame_width * 0.8)
    roi_height = int(frame_height * 0.3)
    roi_x = int((frame_width - roi_width) / 2)
    roi_y = int((frame_height - roi_height) / 2)

    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
    cv2.imshow('Live OCR Feed - Press SPACE', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 32:  # Spacebar
        print("\n--- Capturing Frame ---")
        roi_frame = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        print("Performing OCR...")
        text = pytesseract.image_to_string(thresh, config=TESSERACT_CONFIG)
        print(f"Tesseract raw output: '{text.strip()}'")

        clean_word = ""
        if text.strip():
            clean_word = "".join(filter(str.isalpha, text.strip().split()[0]))

        # --- NEW: Speak the word if it exists ---
        if clean_word:
            # Speak the word first
            if tts_engine:
                print(f"Speaking: '{clean_word.lower()}'")
                tts_engine.say(clean_word.lower())
                tts_engine.runAndWait()  # Blocks while the word is being spoken

            # Then, send it over serial if the port is available
            if ser and ser.is_open:
                data_to_send = (clean_word.lower() + '\n').encode('utf-8')
                print(f">>> Sending '{clean_word.lower()}' over serial...")
                ser.write(data_to_send)
                print(">>> Sent successfully!")
            else:
                print("[Serial port not available to send]")
        else:
            print("[No valid alphabetic word found]")

        cv2.imshow('Analyzed ROI', thresh)

    elif key == ord('q'):
        break

# --- Cleanup ---
print("\nClosing application...")
if ser and ser.is_open:
    ser.close()
    print("Serial port closed.")
cap.release()
cv2.destroyAllWindows()
print("Done.")
