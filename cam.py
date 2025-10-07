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
        print("Error: Could not open video stream.")
        print("Please ensure a USB camera is connected and recognized by the Raspberry Pi.")
        print("You can check by running 'ls /dev/video*' in the terminal.")
        return

    # Set camera properties (optional, but can improve performance)
    # You can experiment with these values.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Camera initialized successfully.")

    # --- Main Loop for Video Display ---
    # This loop will run continuously until the 'q' key is pressed.
    while True:
        # Capture frame-by-frame
        # ret is a boolean that is True if the frame was read successfully
        # frame is the captured image data
        ret, frame = cap.read()

        # If the frame was not captured correctly, break the loop
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        # Display the resulting frame in a window named "USB Camera Feed"
        cv2.imshow('USB Camera Feed (Press "q" to quit)', frame)

        # Wait for a key press.
        # cv2.waitKey(1) waits for 1 millisecond for a key event.
        # We check if the pressed key was 'q' (by comparing its ASCII value).
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("'q' pressed. Closing the application.")
            break

    # --- Cleanup ---
    # When everything is done, release the camera capture object
    print("Releasing camera resources...")
    cap.release()
    # Destroy all the windows created by OpenCV
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    main()

