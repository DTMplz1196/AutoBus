"""
Module: test_capture_screen.py
Description: Verify different window capture methods.
"""
import cv2
import numpy as np
import time
from module.automation.screenshot import ScreenShot


def test_diagnostic_capture():
    """
    Main diagnostic loop for verifying screen capture integrity and performance.
    """

    # start with the full pipeline
    mode = "AUTO (Full Pipeline)"

    print("1: Test GDI Only")
    print("2: Test PrintWindow Only")
    print("3: Test PyAutoGUI Only")
    print("0: Test AUTO Pipeline")
    print("Q: Quit")

    cv2.namedWindow("AutoBus Diagnostic")

    while True:
        start_time = time.time()

        try:
            if mode == "GDI":
                img_pil = ScreenShot.take_screenshot_gdi(gray=False)
            elif mode == "PrintWindow":
                img_pil = ScreenShot.background_screenshot(gray=False)
            elif mode == "PyAutoGUI":
                img_pil = ScreenShot.take_screenshot_pyautogui(gray=False)
            else:
                img_pil = ScreenShot.take_screenshot(gray=False)

            if img_pil is None:
                raise ValueError("None returned")

            img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        except Exception as e:
            print(f"Exception: {e}")

        # Compare performance
        fps = 1.0 / (time.time() - start_time)

        cv2.putText(img_cv, f"Mode: {mode} | FPS: {fps:.1f}", (11, 31),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.imshow("AutoBus Diagnostic", img_cv)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            mode = "GDI"
        elif key == ord('2'):
            mode = "PrintWindow"
        elif key == ord('3'):
            mode = "PyAutoGUI"
        elif key == ord('0'):
            mode = "AUTO (Full Pipeline)"

    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_diagnostic_capture()
