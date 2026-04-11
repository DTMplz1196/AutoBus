"""
Module: cropper.py
Description: Extract assets for future use
Slices the master_screenshot.png using coordinates calculated by coordinate_finder
to create assets files for the Vision module.
"""
import cv2
import os
from utils.vision import Vision

ICON_AREA = (1614, 966, 1788, 1043)


def crop_asset(output_name="cropped_icon.png"):
    """
    Extracts a specific area from the master screenshot.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(script_dir, "master_screenshot.png")
    output_path = os.path.join(script_dir, output_name)

    # Load image
    master = cv2.imread(master_path)
    if master is None:
        print("Couldn't find image")
        return

    # Cropping using vision.crop
    icon = Vision.crop(master, ICON_AREA)

    cv2.imwrite(output_path, icon)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    crop_asset()
