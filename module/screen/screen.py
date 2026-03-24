"""
Module: screen.py
Description: Handles window handle, window state monitoring and coordinates translation between global screen space
and game client space.
"""
import win32gui
import win32con
from win32api import GetMonitorInfo, MonitorFromWindow
from utils.singletonmeta import SingletonMeta
from module.logger.logger import logger


# no need to be singleton because following class Screen has been set to singleton
# setting both result in return hollow instance which hasn't finished its setup, or skips init_handle call
# Thus, the tasks scripts won't work
class Handle:
    """
    Provides a unified interface for getting window information.
    """

    def __init__(self) -> None:
        # instantiation of window handle hwnd
        self._hwnd = 0
        self.title = "LimbusCompany"
        # Correct class name for Limbus Company, validated by test_game_class, so it will actually
        # fetch the right window instead of other classes of software who has the title "LimbusCompany"
        self.class_name = "UnityWndClass"

    def init_handle(self) -> int:
        """
        Gets the window handle.
        """
        self._hwnd = win32gui.FindWindow(self.class_name, self.title)
        if self._hwnd:
            logger.debug(f"Window Handle Found: {self._hwnd}")
        else:
            logger.error(f"Target window '{self.title}' not found.")
        return self._hwnd

    @property
    def hwnd(self) -> int:
        """
        Try to find again if hwnd is 0.
        """
        if self._hwnd == 0:
            return self.init_handle()
        return self._hwnd

    @property
    def isMinimized(self) -> bool:
        """
        Check if game window is minimized.
        """
        return win32gui.IsIconic(self.hwnd)

    @property
    def monitor_info(self) -> dict:
        """
        Retrieves hardware monitor metadata (resolution etc...).

        Essential for GDI ScreenShot.
        """
        monitor = MonitorFromWindow(self.hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        return GetMonitorInfo(monitor)

    def rect(self, client: bool = False) -> tuple[int, int, int, int]:
        """
        Calculates x1,x2,y1,y2 of game window.

        if Client = True, using offsets to bypass areas of borders.
        This is critical for GDI based screen capture because using former method would result in GDI method captures
        Black screen and ensures coordinates alignment for automated clicks(Align global coordinate system: mouse with
        client coordinates system: game icons).
        """
        hwnd = self.hwnd
        if hwnd == 0:
            return 0, 0, 0, 0

        # Get the actual screen position of the window(including borders)
        rect = win32gui.GetWindowRect(hwnd)
        x, y = rect[0], rect[1]

        # Get the client area size
        _, _, w, h = win32gui.GetClientRect(hwnd)

        if client:
            # Add necessary offsets because of the border, otherwise automate click would click wrong area
            # 8px is the standard Windows invisible border
            # 31px is the standard Unity/Windows Title Bar height
            return x + 8, y + 30, x + 8 + w, y + 30 + h
        return rect


class Screen(metaclass=SingletonMeta):
    """
        Singleton Screen class that guarantees only one instance of coordinates window access.
    """

    def __init__(self) -> None:
        self.handle = Handle()
        # Auto-initiate, if we don't do so, we have to call it in every tasks' file, now corrected
        self.handle.init_handle()


# Global instance
screen = Screen()
