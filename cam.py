# rpi_ocr_serial.py
# A Raspberry Pi-specific script that performs OCR on a live video feed
# and sends the first recognized alphabetic word over a serial port.
# Inspired by the user's provided Windows/ESP32 script.

import cv2
import pytesseract
import serial
import serial.tools.list_ports
import time
import sys


SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# Tesseract configuration for speed and accuracy on single words/lines.
TESSERACT_CONFIG = r'--oem 3 --psm 7'

# --- Serial Port Initialization ---
ser = None
try:
    print(f"Attempting to connect to serial device on {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
    print("Successfully connected to serial device.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
    # List available ports to help the user find the correct one.
    available_ports = serial.tools.list_ports.comports()
    print("Available serial ports:", [port.device for port in available_ports])
    # We don't exit here, allowing the OCR part to run for testing.
    print("Warning: Serial communication is disabled. The script will run in OCR-only mode.")


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
print("3. Press the [SPACEBAR] to capture, recognize, and send the text.")
print("4. Press [q] to quit the application.")
print("--------------------\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Define and draw Region of Interest (ROI) for user guidance
    frame_height, frame_width, _ = frame.shape
    roi_width = int(frame_width * 0.8)
    roi_height = int(frame_height * 0.3)
    roi_x = int((frame_width - roi_width) / 2)
    roi_y = int((frame_height - roi_height) / 2)

    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
    cv2.imshow('Live OCR Feed - Press SPACE to Send', frame)

    key = cv2.waitKey(1) & 0xFF

    # --- On Spacebar Press ---
    if key == 32:  # 32 is ASCII for spacebar
        print("\n--- Capturing Frame ---")
        # Crop the image to the ROI
        roi_frame = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

        # Pre-process image for better Tesseract accuracy
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Get text from Tesseract
        print("Performing OCR...")
        text = pytesseract.image_to_string(thresh, config=TESSERACT_CONFIG)
        print(f"Tesseract raw output: '{text.strip()}'")

        # Clean the text to get the first valid alphabetic word
        clean_word = ""
        if text.strip():
            # Find the first sequence of letters and join them
            clean_word = "".join(filter(str.isalpha, text.strip().split()[0]))

        # Check if a valid word was found and the serial port is open
        if clean_word and ser and ser.is_open:
            # Prepare the data with a newline character, which is common for serial protocols
            data_to_send = (clean_word.lower() + '\n').encode('utf-8')

            print(f">>> Word to send: '{clean_word.lower()}'")
            print(">>> Sending over serial...")
            ser.write(data_to_send)
            print(">>> Sent successfully!")
        elif clean_word:
            print(f"[Recognized '{clean_word.lower()}', but serial port is not available to send]")
        else:
            print("[No valid alphabetic word found to send]")

        # Show the pre-processed image that was analyzed for debugging
        cv2.imshow('Analyzed ROI', thresh)

    # --- On 'q' Press ---
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
