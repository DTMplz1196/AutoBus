"""
Module: test_game_class.py
Description: Identify the exact window title and class name of the Limbus Company process.
"""
import win32gui


def spy_limbus():
    """
    Check process' title and class, validate Limbus Company.exe
    """
    target_name = "LimbusCompany"

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            classname = win32gui.GetClassName(hwnd)

            if target_name.lower() in title.lower():
                print("Limbus Company found!")
                print(f"Title: {title}")
                print(f"Class name: {classname}")

    win32gui.EnumWindows(enum_handler, None)


if __name__ == "__main__":
    spy_limbus()
