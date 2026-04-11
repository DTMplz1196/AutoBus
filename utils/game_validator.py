"""
Module: game_validator.py
Description: Provides automated validation of "Limbus Company" application's status
"""

import psutil
from utils.singletonmeta import SingletonMeta


class GameValidator(metaclass=SingletonMeta):
    """
    Singleton class that verify execution status of Limbus Company.

    This class encapsulates process-checking to ensure automation only attempts
    to interact with the game when the process is active.
    """

    def __init__(self) -> None:
        # Standard professional practice: Define target process name as a constant-like attribute
        self._target_process: str = "LimbusCompany.exe"

    def check_game_running(self) -> bool:
        """
        Scans system active process to find target process and avoid case issue.
        """
        for process in psutil.process_iter(["name"]):
            try:
                if process.info["name"] and self._target_process.lower() == process.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False


if __name__ == '__main__':
    game_validator = GameValidator()

    if game_validator.check_game_running():
        print("Limbus Company is running")
    else:
        print("Process not found, please start the game")
