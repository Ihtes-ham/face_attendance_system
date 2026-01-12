import cv2
import sys


def test_webcam():
    print("Testing webcam...")

    # Try to access webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ ERROR: Could not access webcam")
        print("Possible solutions:")
        print("1. Check if webcam is connected")
        print("2. On Linux, check permissions: sudo chmod 666 /dev/video0")
        print("3. On Windows, check device manager")
        return False

    print("✅ Webcam detected!")

    # Try to capture a frame
    ret, frame = cap.read()

    if ret:
        print("✅ Successfully captured frame from webcam")
        height, width = frame.shape[:2]
        print(f"📏 Resolution: {width} x {height}")
    else:
        print("❌ Could not capture frame")

    cap.release()
    return ret


if __name__ == "__main__":
    test_webcam()