"""
Module: window_utils.py
Description: Enforce environment to be ideal(1920 * 1080)
Ensures the game client to be set to expected resolution and spatial constraints.
"""
import win32gui
import win32con
import win32api


def ensure_resolution(hwnd, target_w=1920, target_h=1080):
    """
    Forces game window to specific resolution.

    Ensure the resolution so the actual game icons/buttons matches assets.
    Calculates non-client offsets (title bars/borders) to ensure the
    rendering surface is exactly target_w x target_h.
    """
    if not hwnd: return False

    # Get current rects
    client_rect = win32gui.GetClientRect(hwnd)
    current_w, current_h = client_rect[2], client_rect[3]

    if current_w != target_w or current_h != target_h:
        print(f"Resolution dift: {current_w}*{current_h}. Correcting to {target_w}*{target_h}...")

        # Add WS_THICKFRAME style temporarily to allow resizing
        style = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
        win32api.SetWindowLong(hwnd, win32con.GWL_STYLE, style | win32con.WS_THICKFRAME)

        # Adjust window size
        # Use AdjustWindowRect to calculate the exact window size needed to get a 1920x1080 client area
        rect = win32gui.GetClientRect(hwnd)
        w_rect = win32gui.GetWindowRect(hwnd)

        # Calculate non-client area (borders/title bar)
        width_offset = (w_rect[2] - w_rect[0]) - rect[2]
        height_offset = (w_rect[3] - w_rect[1]) - rect[3]

        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOP, 0, 0,
            target_w + width_offset, target_h + height_offset,
            win32con.SWP_NOMOVE | win32con.SWP_FRAMECHANGED
        )
        return True
    return False


def activate_window(hwnd):
    """
    Brings game window to the front.
    Restore window if minimized.
    """
    try:
        # If the window is minimized, restore it
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Bring it to the front
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Failed to focus game window: {e}")


def move_window_to_top_left(hwnd):
    """
    Moves game window to (0, 0) on the monitor.

    Ensuring deterministic coordinates translation in Controller.py.
    """
    # SWP_NOSIZE = 0x0001 (don't change the window size)
    # SWP_NOZORDER = 0x0004 (don't change the Z-order)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
