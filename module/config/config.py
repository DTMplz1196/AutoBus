"""
Module: config.py
Description: Management for assets paths and user settings
"""
import json
import os
from typing import Dict, Any, List
from utils.singletonmeta import SingletonMeta
from module.logger.logger import logger


class Config(metaclass=SingletonMeta):
    """
    Singleton class to manage assets paths and JSON file(user settings)
    """

    def __init__(self) -> None:
        # Goes to the root
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.ASSETS_DIR = os.path.join(self.BASE_DIR, "assets")
        self.CONFIG_PATH = os.path.join(self.BASE_DIR, 'config.json')

        self.current_team_index = 0
        self.team_queue: List[Dict[str, Any]] = []
        self.global_settings: Dict[str, Any] = {"target_runs": 1}
        self._active_settings: Dict[str, Any] = {}

        self.load()

    def load(self) -> None:
        """
        Loads the team queue and global settings. Sets the first team as active.
        """
        if not os.path.exists(self.CONFIG_PATH):
            logger.warning("Config file missing!")
            return

        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 1. Retrieve global settings
                self.global_settings = data.get("global_settings", {"target_runs": 1})

                # 2. Retrieve the list of teams
                self.team_queue = data.get("team_queue", [])

                # 3. Set the first team for startup
                if self.team_queue:
                    self._active_settings = self.team_queue[0]
                else:
                    self._active_settings = {}
                    logger.info("Team queue is currently empty.")

        except (json.JSONDecodeError, IOError):
            logger.error("Failed to parse config.json. Resetting to empty...")
            self.team_queue = []
            self.global_settings = {"target_runs": 1}

    def set_active_task(self, index: int):
        """
        Helper to switch which task the bot is currently reading from.
        """
        if 0 <= index < len(self.team_queue):
            self.current_team_index = index
            self._active_settings = self.team_queue[index]

    def get_asset_path(self, relative_path: str) -> str:
        """
        Normalizes and returns the absolute path to an asset.
        """
        full_path = os.path.join(self.ASSETS_DIR, relative_path)
        return os.path.normpath(full_path)

    @property
    def settings(self) -> Dict[str, Any]:
        """
        Modules in AutoBos/module will call this to get current task's info.
        """
        return self._active_settings


# Global instance now uses the correct absolute path
config_manager = Config()
get_asset_path = config_manager.get_asset_path
