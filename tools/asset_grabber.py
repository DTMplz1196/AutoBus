"""
Module: asset_grabber.py
Description: Capture 1:1 real of game client that bots perceives, to be used for coordinates locating
and template cropping
"""
import time
import cv2
import numpy as np
from module.automation.screenshot import ScreenShot
from utils.game_validator import GameValidator
from module.automation.controller import Controller


def asset_grabber():
    """
    Captures current game client area that bots perceives.

    Ensures template are created from same rendering pipeline used by bot's vision module
    """
    Controller.validate_environment()

    if not GameValidator().check_game_running():
        print("LimbusCompany.exe is not running.")
        return False

    print("Waiting 1s for UI stability...")
    time.sleep(1)

    img = ScreenShot.take_screenshot(gray=False)

    if img is None:
        print("Failed to capture valid image.")
        return False

    # Convert PIL Image (RGB) to OpenCV format (BGR) for disk write
    img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imwrite("master_screenshot.png", img_bgr)
    print("Screenshot saved.")


if __name__ == "__main__":
    asset_grabber()
