"""
Module: coordinate_finder.py
Description: Mapping absolute game coordinates from master_screenshot.png.
Automatically calculates area and interactive area selection.
"""
import cv2
import os


def find_coordinates():
    """
    Launches an interactive OpenCV window to map coordinates on screenshot.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "master_screenshot.png")

    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not load {img_path}")
        return

    # Resize for viewing
    orig_h, orig_w = img.shape[:2]
    display_h = 800
    scale = orig_h / display_h

    display_w = int(orig_w / scale)
    resized_img = cv2.resize(img, (display_w, display_h))

    points_display = []  # Stores (x, y) from the 800px window
    display_img = resized_img.copy()

    def click_event(event, x, y, flags, params):
        """
        Mouse callback to handle point selection and visual feedback
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Record the point exactly where the mouse clicked (Display Scale)
            points_display.append((x, y))

            # Visual Feedback: Green dot
            cv2.circle(display_img, (x, y), 4, (0, 255, 0), -1)

            # Calculate Area when two points are present
            if len(points_display) == 2:
                x1, y1 = points_display[0]
                x2, y2 = points_display[1]

                # Sort to ensure min/max logic
                min_x, max_x = sorted([x1, x2])
                min_y, max_y = sorted([y1, y2])

                # Convertion, for bbox using later
                abs_min_x = int(min_x * scale)
                abs_max_x = int(max_x * scale)
                abs_min_y = int(min_y * scale)
                abs_max_y = int(max_y * scale)

                # Draw the bounding box (Red)
                cv2.rectangle(display_img, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
                cv2.imshow("Coordinate Finder", display_img)

                print(f"\n--- Resulting ICON_AREA ---")
                print(f"Template/Crop Area: ({min_x}, {min_y}, {max_x}, {max_y})")
                # For locating bbox
                print(f"For bbox: ({abs_min_x}, {abs_min_y}, {abs_max_x}, {abs_max_y})")

    cv2.namedWindow("Coordinate Finder", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Coordinate Finder", click_event)

    print("Click Top-Left, then Bottom-Right of target area.")
    while True:
        cv2.imshow("Coordinate Finder", display_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    find_coordinates()
