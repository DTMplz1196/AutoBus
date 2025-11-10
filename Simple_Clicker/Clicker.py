# Handles all the complex mathematical operations required to understand what's on the screen
# 和image processing选修上面是类似的, 比如cv2.cvtColor(), cv2.imread(), cv2.matchTemplate()等等
import cv2
# Since images are just massive arrays of numbers (pixel color values), NumPy is crucial for handling them quickly.
import numpy as np
# pyautogui.screenshot()	Takes a screenshot, acting as the script's "camera"
# pyautogui.moveTo()	Controls the mouse to move to the calculated coordinates.
# pyautogui.click()	Simulates a mouse click.
import pyautogui
import time
# using function time.sleep() to pause script for each attempt, prevent it from running at max speed
import os

# !!! can't use \ in python since it recognize it as escape sequence
Image1_path = 'D:/Thesis_Project/Playground/AutoBus/Simple_Clicker/Chain_to_battle_1.png'
Image2_path = 'D:/Thesis_Project/Playground/AutoBus/Simple_Clicker/Chain_to_battle_2.png'
Image_Test_path = 'D:/Thesis_Project/Playground/AutoBus/Simple_Clicker/Test.png'
Confidence_Threshold = 0.8


def find_and_click_image_1(target_path):
    """
        Finds the target image on the screen and clicks its center point.
    """
    print(f"Attempting to find target image: {target_path}")

    if not os.path.exists(target_path):
        print(f"Error: Couldn't find image file '{target_path}'")
        return False

    try:
        # take screenshot of whole screen
        # it shows warning, but in fact the function exists, I've tested using Screenshot_Function_Test
        screenshot = pyautogui.screenshot()

        # Convert PIL image to numpy array processable by OpenCV
        screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)

        # Load target image
        template = cv2.imread(target_path)

        # From previous we only check if the image exits, but don't know if the image is valid
        # or whether OpenCV can read it, so we need this
        if template is None:
            print(f"Error: Faild to load template image '{target_path}'.")
            return False

        # Convert to gray scale
        screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # .shape gives (rows, cols) which corresponds to (height, width).
        # [::-1] reverse the tuple, so it becomes (width, height)
        # Or just use h, w = template_gray.shape, as long as I remember the order is (h, w)
        w, h = template_gray.shape[::-1]

        # TM_CCOEFF_NORMED, one of the template matching methods in OpenCV
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Find the location of best match
        # min_val: Lowest similarity score. -1 to 1; max_val: Highest similarity score, close to 1 means strong
        # min_loc: Coordinates(x,y) of the location where min_val occur; max_loc where max_val occur
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # check how similar they are by comparing set threshold
        if max_val > Confidence_Threshold:
            # Find top-left coordinates of matching area
            top_left = max_loc

            # Calculate coordinates of the matching area
            # 0 means x-coordinate of the top_left corner, 1 means y
            # where the template starts: top_left, how big the template is (w, h)
            # !!!: if we simply use top 0,1 then we are clicking corner, by adding
            # the half of the image width and height we can click the center
            center_x = top_left[0] + w // 2
            center_y = top_left[1] + h // 2

            print(f"Image Match, the confidence is: {max_val:.2f}. Center Coordinates: ({center_x}, {center_y})")

            # move to center point
            # !!!:inhuman move and click, might be detected by anti-cheat, how to solve it?
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.click(center_x, center_y)

            return True
        else:
            print(
                f"Image doesn't matck, the confidence is: {max_val:.2f}, lower than threshold: {Confidence_Threshold}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    print("Processing...")

    run_count = 0
    max_runs = 3

    while run_count < max_runs:
        success = find_and_click_image_1(Image_Test_path)

        if success:
            print("Successful, wait 5 sec")
        else:
            print("Faild, writing 5 sec to retry")

        time.sleep(5)
        run_count += 1

    print("Script finished running")
