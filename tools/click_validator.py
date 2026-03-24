"""
Module: click_validator.py
Description: Verification tool for clicking
Tests if the bots can find and click on cropped target, integrate Controller module
"""
import os
from module.config.config import get_asset_path
from module.automation.controller import Controller


def click_validator():
    """
    Attempts to locate and click a specific template
    to verify if cropped target matches and click accuracy
    """
    asset_path = get_asset_path("../tools/cropped_icon.png")

    if not os.path.exists(asset_path):
        print(f"File not found at {asset_path}")
        return

    success = Controller.click_element(asset_path)

    if success:
        print("Successfully found and clicked the target.")
    else:
        print("Target not found.")


if __name__ == '__main__':
    click_validator()
