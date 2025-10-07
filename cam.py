# main.py
# This script captures video from a USB camera connected to a Raspberry Pi
# and displays it in a window on the Raspberry Pi's desktop.

import cv2
import sys

def main():
    """
    Initializes the USB camera, captures the video feed frame by frame,
    and displays it in a window.
    Accepts an optional command-line argument for the camera index.
    """
    # --- Determine Camera Index ---
    # Default to camera index 0
    camera_index = 0
    # If a command-line argument is provided, use it as the camera index
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid camera index '{sys.argv[1]}'. Please provide an integer.")
            return

    # --- Camera Initialization ---
    # cv2.VideoCapture() attempts to access the camera at the given index.
    # We also specify the CAP_V4L2 backend, which is standard for Video4Linux on Raspberry Pi.
    print(f"Attempting to initialize camera at index: {camera_index}...")
    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

    # --- Check if Camera Opened Successfully ---
    if not cap.isOpened():
        print(f"Error: Could not open video stream from camera index {camera_index}.")
        print("Please ensure a USB camera is connected and the index is correct.")
        return

    # Set camera properties (optional, but can improve performance)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Camera initialized successfully.")

    # --- Main Loop for Video Display ---
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If the frame was not captured correctly, break the loop
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        # Display the resulting frame in a window
        cv2.imshow(f'USB Camera Feed (Index {camera_index}) - Press "q" to quit', frame)

        # Wait for 'q' key to be pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("'q' pressed. Closing the application.")
            break

    # --- Cleanup ---
    print("Releasing camera resources...")
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    main()

