"""
Module: theme_pack_selector.py
Description: Handles Theme Pack selection each using drag gestures.
"""
from module.config.config import get_asset_path
from module.automation.controller import Controller
from module.logger.logger import logger
import os.path
import pyautogui


class ThemePackSelector:
    def __init__(self):
        self.packs = {
            "easy": [get_asset_path(f"images/mirror_dungeon/theme_pack/easy/easy_{i}.png") for i in range(1, 17)],
            "medium": [get_asset_path(f"images/mirror_dungeon/theme_pack/medium/medium_{i}.png") for i in range(1, 11)],
            "hard": [get_asset_path(f"images/mirror_dungeon/theme_pack/hard/hard_{i}.png") for i in range(1, 23)],
        }
        self.is_theme_pack_selection_state = get_asset_path("images/mirror_dungeon/theme_pack/pack_search.png")
        self.bbox_theme_pack_acre = (121, 253, 1773, 988)
        self.bbox_state = (171, 60, 394, 153)

    def drag_to_enter(self, pack_path):
        """
        Clicks the selected pack and drags it down to confirm entry.
        """

        coor = Controller.find_element(pack_path, bbox=self.bbox_theme_pack_acre)

        if coor:
            # Validate environment here, so we can use pyautogui directly without
            # calculating offsets if game window is not in the top-left corner
            Controller.validate_environment()
            # Only keeps assets name before .png
            pack_name = os.path.splitext(os.path.basename(pack_path))[0]
            logger.info(f"Theme pack selected, rank: {pack_name}, entering...")
            x, y = coor
            pyautogui.move(x, y)
            # Dragging using left mouse
            pyautogui.dragTo(x, y + 500, duration=0.5, button='left')
            return True
        else:
            logger.warning("Theme pack not found, did you refreshed?")
            return False

    def select_theme(self):
        """
        Selects theme pack based on priority: easy > medium > hard to optimize efficiency
        Validate the environment and check if we are in correct state
        """
        Controller.validate_environment()

        if not Controller.find_element(self.is_theme_pack_selection_state, bbox=self.bbox_state):
            logger.warning("Not in theme pack selection state.")
            return False

        for rank in ["easy", "medium", "hard"]:
            for pack_path in self.packs[rank]:
                if Controller.find_element(pack_path, bbox=self.bbox_theme_pack_acre):
                    logger.info(f"Identified {rank} pack.")
                    return self.drag_to_enter(pack_path)

        else:
            logger.warning("No theme pack detected based on current assets, check for update.")
            return False


if __name__ == '__main__':
    theme_pack_selector_instance = ThemePackSelector()
    theme_pack_selector_instance.select_theme()
