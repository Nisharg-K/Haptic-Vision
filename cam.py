# rpi_ocr.py
# A script inspired by the user's code, adapted and optimized for Raspberry Pi.
# It performs real-time Optical Character Recognition (OCR) on a video feed.

import cv2
import pytesseract
import sys

def main():
    """
    Initializes a camera, displays a live feed with a Region of Interest (ROI),
    and performs OCR on the ROI when the spacebar is pressed.
    """
    # --- Camera Initialization ---
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid camera index '{sys.argv[1]}'. Using default index 0.")

    print(f"Attempting to initialize camera at index: {camera_index}...")
    # Using CAP_V4L2 is good practice on Linux/Raspberry Pi
    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {camera_index}.")
        print("Please check if the camera is connected and try a different index (e.g., 0, 1).")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Camera initialized successfully.")

    # --- Tesseract Configuration ---
    # --psm 7: Treat the image as a single text line. This is fast and effective for single words.
    TESSERACT_CONFIG = r'--oem 3 --psm 7'

    # --- Main Application Loop ---
    print("\n--- INSTRUCTIONS ---")
    print("1. A window with the camera feed will open.")
    print("2. Position the text you want to read inside the green rectangle.")
    print("3. Press the [SPACEBAR] to capture and recognize the text.")
    print("4. Press [q] to quit the application.")
    print("--------------------\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame from camera.")
            break
        
        # --- Define and Draw Region of Interest (ROI) ---
        # This helps the user know where to place the text.
        frame_height, frame_width, _ = frame.shape
        roi_width = int(frame_width * 0.8)
        roi_height = int(frame_height * 0.3)
        roi_x = int((frame_width - roi_width) / 2)
        roi_y = int((frame_height - roi_height) / 2)
        
        # Draw the ROI rectangle on the live feed
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
        cv2.imshow('Live OCR Feed - Press SPACE to read', frame)

        key = cv2.waitKey(1) & 0xFF

        # --- On Spacebar Press: Capture and Process ---
        if key == 32: # 32 is the ASCII code for spacebar
            print("\n--- Capturing Frame ---")
            # Crop the image to the defined ROI for faster processing
            roi_frame = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
            
            # Pre-process the image for better OCR accuracy
            # 1. Convert to grayscale
            gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
            # 2. Apply thresholding to get a black and white image
            #    Otsu's thresholding is great for varying light conditions.
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Perform OCR using Tesseract
            print("Performing OCR...")
            text = pytesseract.image_to_string(thresh, config=TESSERACT_CONFIG)
            
            cleaned_text = text.strip()
            
            if cleaned_text:
                print(f"--> Recognized Text: '{cleaned_text}'")
            else:
                print("[No text found in the ROI]")

            # Display the processed, black-and-white image for debugging
            cv2.imshow('Processed ROI for Tesseract', thresh)

        # --- On 'q' Press: Quit ---
        elif key == ord('q'):
            print("'q' pressed. Exiting...")
            break

    # --- Cleanup ---
    print("Closing application and releasing resources.")
    cap.release()
    cv2.destroyAllWindows()
    print("Done.")

if __name__ == "__main__":
    main()
