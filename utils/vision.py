"""
Module: vision.py
Description: Vision engine of AutoBus. Implements multi-model image recognition including Template Matching,
Feature Matching(ORB), and homographic Transformation
"""
from utils.singletonmeta import SingletonMeta
import cv2
import numpy as np


class Vision(metaclass=SingletonMeta):
    """
    Vision Engine of AutoBus.

    Handles image normalization,
    cropping, and template localization.
    """

    @staticmethod
    def get_grey_normalized_pic(img_array):
        """
        Converts input to grayscale and applies CLAHE (Adaptive histogram equalization).
        This ensures bot is resistant to lighting changes and flashes.

        :return cl1: Grayscale test_images processed with adaptive histogram equalization.
        """
        # Check if the input test_images is color, if so, convert to grayscale
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            img = img_array.copy()

        # Create CLAHE object
        # clipLimit = 2.0 sets contrast limit, tileGridSize=(8, 8) sets grid size
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # Apply CLAHE
        return clahe.apply(img)

    @staticmethod
    def feature_matching(template_img, target_img, min_matches=8):
        """
        Uses ORB feature detection and FLANN matching to find a template within a target.
        """
        # Resize images for better feature detection performance
        template = cv2.resize(template_img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        target = cv2.resize(target_img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # Initialize ORB feature detector
        orb = cv2.ORB_create(nfeatures=1000, scaleFactor=1.2, edgeThreshold=10)

        # Detect keypoints and compute descriptors
        kp1, des1 = orb.detectAndCompute(template, None)
        kp2, des2 = orb.detectAndCompute(target, None)

        # FLANN matcher for high-speed high-dimensional vector matching
        index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        # Apply ratio test to filter matches and unpack only if we have at least 2 matches per point
        # Previous version would result in vision.py crashes when run battle.py since matching template
        # for "battle end" state icon sometimes returns an empty list(0 match)
        good_matches = []
        for match in matches:
            if len(match) == 2:
                m, n = match
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

        if len(good_matches) >= min_matches:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])

            # RANSAC filters out 'outliers' (false feature matches)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 2.0)

            # Validation: check if the found points actually form a consistent shape
            inlier_ratio = np.sum(mask) / len(mask)
            if inlier_ratio < 0.8:
                return False, None

            # Calculate center:
            h, w = template.shape[:2]
            # Define corners of the template
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            # Project them into the target screenshot
            dst = cv2.perspectiveTransform(pts, M)

            # Revert the 2x upscale for actual clicking coordinates
            # Divide by 2 because of resizing
            center_x = int(np.mean(dst[:, :, 0]) / 2)
            center_y = int(np.mean(dst[:, :, 1]) / 2)

            return True, (center_x, center_y)
        return False, None

    @staticmethod
    def match_template(screenshot, template, bbox, model="focused"):
        """
        Standard Template Matching (TM_CCOEFF_NORMED).

        Finds a template within a screenshot, Supports localized search via Bounding Box (bbox)
        to increase speed and accuracy.

        Models:
            - "focused": Tight search (30px padding) for static UI.
            - "relaxed": Moderate search (100px padding) for shifting UI.
            - "global": Full screen scan for unknown positions.
        """
        try:
            h_s, w_s = screenshot.shape[:2]
            h_t, w_t = template.shape[:2]

            # Determine Search Area
            if model == "global" or bbox is None:
                search_area = screenshot
                offset_x, offset_y = 0, 0
            else:
                padding = 30 if model == "focused" else 100
                x1, y1, x2, y2 = (
                    max(bbox[0] - padding, 0),
                    max(bbox[1] - padding, 0),
                    min(bbox[2] + padding, w_s),
                    min(bbox[3] + padding, h_s)
                )
                # Added this because after we set bbox, an OpenCV error appears
                # says the search are is smaller than template
                if (x2 - x1) < w_t or (y2 - y1) < h_t:
                    # If search area is too small, back to full screen scan
                    search_area = screenshot
                    offset_x, offset_y = 0, 0
                else:
                    search_area = screenshot[y1:y2, x1:x2]
                    offset_x, offset_y = x1, y1

            # Execute Template Matching
            res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Calculate center relative to original screenshot
            center = (offset_x + max_loc[0] + w_t // 2, offset_y + max_loc[1] + h_t // 2)

            return center, max_val

        except Exception as e:
            print(f"Vision Template Match Error: {e}")
            return None, 0

    @staticmethod
    def crop(image, area, copy=True):
        """
        Crops a specified area from the images.

        Automatically handles out-of-bounds coordinates by padding with black pixels.
        Critical for UI elements on screen edges.
        """
        # Convert coordinates to integers
        x1, y1, x2, y2 = map(int, map(round, area))

        # Get test_images dimensions
        h, w = image.shape[:2]

        # Calculate padding needed if coordinates are outside bounds
        border = np.maximum((0 - y1, y2 - h, 0 - x1, x2 - w), 0)

        # Clamp coordinates to test_images boundaries
        x1, y1, x2, y2 = np.maximum((x1, y1, x2, y2), 0)

        # Crop the valid area
        image = image[y1:y2, x1:x2]

        # Apply padding if necessary
        if sum(border) > 0:
            image = cv2.copyMakeBorder(image, *border, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        if copy:
            image = image.copy()
        return image
