"""
Module: screenshot.py
Description: Screen capture engine for AutoBus, using failsafe method from PrintWindow, GDI to PyAutoGui
"""
from utils.singletonmeta import SingletonMeta
import numpy as np
import win32gui
import win32ui
import win32con
import pyautogui
from ctypes import windll
from PIL import Image
from module.screen.screen import screen
from utils.game_validator import GameValidator
from typing import Optional
from module.logger.logger import logger


class ScreenShot(metaclass=SingletonMeta):
    """
    Main entry point for capturing game window.

    Apply failsafe logic across multiple windows graphics APIs to ensure capture is successful.
    """

    @staticmethod
    def take_screenshot_gdi(gray: bool = True) -> Image.Image:
        """
        Captures the screen using a full-desktop device context, then crops the target window.

        Bypasses GPU-protected window buffers.
        """
        # Ensure high-resolution scaling
        windll.user32.SetProcessDPIAware()

        # Get the handle and the correct screen coordinates
        hwnd = screen.handle.hwnd
        # This retrieves the monitor where the window is actually located, associated with
        # screen.handle.monitor_info, the previous method would result in GDI method captures
        # all black screen due to border math error
        monitor_info = screen.handle.monitor_info
        x1, y1, x2, y2 = monitor_info["Monitor"]

        # Setup Device Contexts
        hdc_screen = windll.user32.GetDC(0)
        hdc_mem = windll.gdi32.CreateCompatibleDC(hdc_screen)
        hbitmap = windll.gdi32.CreateCompatibleBitmap(hdc_screen, x2 - x1, y2 - y1)

        try:
            windll.gdi32.SelectObject(hdc_mem, hbitmap)
            # Capture the entire monitor to avoid "black screen" on individual window hooks
            windll.gdi32.BitBlt(hdc_mem, 0, 0, x2 - x1, y2 - y1, hdc_screen, x1, y1, win32con.SRCCOPY)

            # Convert to PIL via buffer
            bmp = win32ui.CreateBitmapFromHandle(hbitmap)
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

            # Crop using fixed rect of offsets
            win_x1, win_y1, win_x2, win_y2 = screen.handle.rect(client=True)
            # Shift coordinates relative to the monitor origin
            relative_rect = (win_x1 - x1, win_y1 - y1, win_x2 - x1, win_y2 - y1)
            img = img.crop(relative_rect)

        finally:
            # Cleanup to prevent memory leaks
            windll.gdi32.DeleteObject(hbitmap)
            windll.gdi32.DeleteDC(hdc_mem)
            windll.user32.ReleaseDC(0, hdc_screen)

        return img.convert("L") if gray else img

    @staticmethod
    def background_screenshot(gray: bool = True) -> Image.Image:
        """
        Uses PrintWindow (PW_RENDERFULLCONTENT) to capture game window.

        Uses PrintWindow to capture game window by the consideration of efficiency and reliability.
        Efficiency: GDI > PrintWindow > PyAutoGui
        reliability: PyAutoGui > PrintWindow > GDI
        Tested by the test_capture_screen.py where GDI has the highest FPS followed by PrintWindow and PyAutoGui.
        """
        hwnd = screen.handle.hwnd
        x1, y1, x2, y2 = screen.handle.rect(client=True)
        w, h = x2 - x1, y2 - y1

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)

        # Flag 2 = PW_RENDERFULLCONTENT, supports hardware acceleration
        windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer("RGB", (w, h), bmpstr, "raw", "BGRX", 0, 1)

        # Cleanup to prevent memory leaks
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        return img.convert("L") if gray else img

    @staticmethod
    def take_screenshot_pyautogui(gray: bool = True) -> Image.Image:
        """
        Desktop Duplication Wrapper.

        Utilize PyAutoGui to capture game window. This method
        serves as a fail-safe, as it handles Windows DPI scaling and
        Desktop Duplication API calls internally. While slower than GDI and
        PrintWindow, it offers the highest compatibility across different
        Windows display configurations.
        """
        x1, y1, x2, y2 = screen.handle.rect(client=True)
        # PyAutoGUI handles the complex Win32 calls internally
        img = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        return img.convert("L") if gray else img

    @staticmethod
    def take_screenshot(gray: bool = True) -> Optional[Image.Image]:
        """
        Main entry point for capturing game window.

        Uses failsafe method that tries PrintWindow method first, then GDI method, finally PyAutoGui if previous 2 all
        failed. This ensures the game window can be captured successfully.
        """
        windll.user32.SetProcessDPIAware()

        # Always check if game is running before capturing
        if not GameValidator().check_game_running():
            logger.warning("Game is not running.")
            return None

        # Primary: PrintWindow method
        # This works even if the window is partially covered.
        try:
            img = ScreenShot.background_screenshot(gray)
            if np.any(np.array(img)):
                return img
        except Exception as e:
            logger.debug(f"PrintWindow capture failed: {e}")

        # Secondary: GDI method
        # This bypasses rendering blocks.
        try:
            img = ScreenShot.take_screenshot_gdi(gray)
            if np.any(np.array(img)):
                return img
        except Exception as e:
            logger.debug(f"GDI capture failed: {e}")

        # Tertiary: PyAutoGUI method, failsafe
        # This captures the desktop directly, slowest but most reliable.
        logger.warning("PrintWindow, GDI capture methods failed. Falling back to PyAutoGUI.")
        try:
            return ScreenShot.take_screenshot_pyautogui(gray)
        except Exception as e:
            logger.error(f"Critical Error: All capture methods failed: {e}")
            return None
