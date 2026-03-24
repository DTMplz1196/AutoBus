"""
Module: controller.py
Description: Execution Layer. Integrates Perception (Vision.py) and Action (Clicking).
Implements template caching, spatial masking, and coordinate normalization.
"""
import os
import time
import numpy as np
import cv2
import pyautogui
from module.automation.screenshot import ScreenShot
from utils.vision import Vision
from utils.window_utils import ensure_resolution, activate_window, move_window_to_top_left
from module.screen.screen import screen
from module.logger.logger import logger


class Controller:
    """
    Controller class which Validate and ensure environment, implements finding and clicking.
    """
    # Cache templates in RAM to reduce disk I/O overhead.
    _template_cache = {}

    @staticmethod
    def get_template(path):
        """
        Retrieves template from cache or loads it from disk if not present
        """
        if path not in Controller._template_cache:
            Controller._template_cache[path] = cv2.imread(path)
        return Controller._template_cache[path]

    @staticmethod
    def validate_environment():
        """
        Helper to ensure game window is focused, positioned with ideal resolution.
        """
        hwnd = screen.handle.hwnd
        ensure_resolution(hwnd)
        move_window_to_top_left(hwnd)
        activate_window(hwnd)
        time.sleep(0.1)

    @staticmethod
    def find_element(template_path, threshold=0.8, bbox=None, model="clam"):
        """
        Locates UI elements using hybrid strategy: 1. Template matching(speed) 2. Feature Matching(Robustness)
        """
        # Ensure environment is valid
        Controller.validate_environment()

        # Reset mouse to prevent hover-effects
        # (5, 43) is calculated based on coordinate_finder.py, if we move to (0,0) it will actually
        # move mouse to the title bar and disrupt because of sub manu.
        pyautogui.moveTo(5, 43)
        time.sleep(0.1)

        # Use Cache
        template = Controller.get_template(template_path)
        if template is None:
            logger.error(f"Template not found at: {template_path}")
            return None

        img_data = ScreenShot.take_screenshot(gray=False)
        if img_data is None:
            return None

        # Covert PIL to Open CV format(BGR)
        screenshot = cv2.cvtColor(np.array(img_data), cv2.COLOR_RGB2BGR)

        # Spatial masking: black out the detected logo area (6, 4, 32, 35), calculated based on coordinate_finder.py
        # if we don't black out this area the script would be disrupted by sub menu because of hovering on game logo
        screenshot[4:35, 6:32] = 0

        # 1: Template Matching (Fast) using blackouted screenshot
        center, confidence = Vision.match_template(screenshot, template, bbox=bbox, model=model)

        if confidence >= threshold:
            # Immediately memory release to avoid memory leaks by running AutoBus for long period
            del screenshot
            return center

        # 2. ORB feature matching (Robustness) using blackouted screenshot
        orb_result = Vision.feature_matching(template, screenshot)
        del screenshot

        # check if result is tuple, and also if feature matching succeed
        if isinstance(orb_result, tuple) and orb_result[0]:
            # if so, returns the coordinates
            return orb_result[1]

        logger.debug(f"Target {template_path} not found.")
        return None

    @staticmethod
    def click_element(template_path, y_offset=0, x_offset=0, y_bias=-25, x_bias=-15, bbox=None, model='clam'):
        """
        Method that finds the element and clicks if found.

        Returns True if clicked, False if not found.
        """
        coor = Controller.find_element(template_path, threshold=0.8, bbox=bbox, model=model)

        if coor:
            # Get the current window origin (the top-left corner), re-verify before clicking
            win_x, win_y, _, _ = screen.handle.rect(client=True)

            # Relative coordinates
            rel_x, rel_y = coor

            # Calculate final clicking area
            # Using offsets because sometimes we need to click area relative to the target
            # Using manually calculated bias because previously couldn't locate the correct coordinates
            # Not using random to mimic human reaction because this game lacks such anti-cheat, and it might result in
            # clicking wrong are.
            abs_x = win_x + rel_x + x_bias + x_offset
            abs_y = win_y + rel_y + y_bias + y_offset

            pyautogui.click(abs_x, abs_y)
            return True

        else:
            logger.debug(f"Controller: [{template_path}] not found.")
            return False

    @staticmethod
    def click_with_retry(template_path, tries=3, interval=0.5, **kwargs):
        """
        Attempts to find and click an element multiple times.

        **kwargs allows passing bbox, offsets, and model to the click_element method.
        """
        for i in range(tries):
            if Controller.click_element(template_path, **kwargs):
                return True

            if i < tries - 1:
                time.sleep(interval)

        template_name = os.path.splitext(os.path.basename(template_path))[0]

        logger.warning(f"Failed to click {template_name} after {tries} attempts.")
        return False
