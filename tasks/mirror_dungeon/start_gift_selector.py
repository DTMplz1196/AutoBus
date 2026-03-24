"""
Module: gift_selector.py
Description: Handles initial EGO Gift selection in Mirror Dungeon.
"""
from module.automation.controller import Controller
from module.config.config import config_manager, get_asset_path
from module.logger.logger import logger
import time


class GiftSelector:
    def __init__(self):
        # Map JSON config keys to actual image paths
        self.gift_assets = {
            f"gift{i}": get_asset_path(f"images/mirror_dungeon/start_gift/gift_{i}.png")
            for i in range(1, 7)
        }
        self.search_on = get_asset_path("images/mirror_dungeon/start_gift/search_on.png")
        self.select_gift_anchor = get_asset_path(
            "images/mirror_dungeon/start_gift/select_gift_anchor.png")
        self.select_btn = get_asset_path("images/mirror_dungeon/start_gift/select_btn.png")
        self.select_confirm = get_asset_path("images/mirror_dungeon/start_gift/select_confirm.png")
        self.bbox_anchor = (1131, 214, 1802, 334)
        self.bbox_gift_type = (184, 240, 1108, 881)

    def proceed_to_select_ego_gift(self):
        """
        Clicks gift slots based on the standard anchor and confirms.
        """
        # Using "Selected EGO Gift" as anchor to select EGO gift
        # since different type of EGO gifts differ significantly
        offsets = [150, 310, 475]
        for y_off in offsets:
            Controller.click_element(self.select_gift_anchor, y_offset=y_off, bbox=self.bbox_anchor)
            time.sleep(0.2)

        Controller.click_with_retry(self.select_btn)
        # Wait for short internet connection
        time.sleep(2)

        gift_count = 0
        # Attempts to click up to 3 confirm btn because the available EGO gifts
        # may vary according to star buff selection
        for i in range(3):
            if Controller.find_element(self.select_confirm):
                logger.info("Confirm button detected, clicking...")
                gift_count += 1
                Controller.click_with_retry(self.select_confirm)
            else:
                logger.info("No more confirm button detected.")
                break
        logger.info(f"{gift_count} EGO gift acquired.")

    def select_gift(self):
        """
        Selects start EGO gifts based on user preference
        Validate the environment and check if we are in correct state
        """
        Controller.validate_environment()

        # If we can't find "Selected EGO Gift" in specific bbox, then we are not in gift selection state
        if not Controller.find_element(self.select_gift_anchor, bbox=self.bbox_anchor):
            logger.warning("Not in start gift selection state.")
            return False

        # Switch off gift search to save time and starlight, no need for normal difficulty
        if Controller.find_element(self.search_on):
            Controller.click_element(self.search_on)
            logger.info("Gift search is on, switching off...")

        gift_preference = config_manager.settings.get("gift_preference")
        gift_path = self.gift_assets.get(gift_preference)

        if not gift_preference:
            logger.warning("No gift preference set, you have to set preference first!")
            return False

        if gift_path and Controller.find_element(gift_path, bbox=self.bbox_gift_type):
            logger.info("In gift selection state. Selecting preferred EGO gift...")
            Controller.click_element(gift_path, bbox=self.bbox_gift_type)
            time.sleep(0.1)
            self.proceed_to_select_ego_gift()
            return True

        else:
            logger.warning("Preferred EGO gift not found.")
            return False


if __name__ == '__main__':
    gift_selector_instance = GiftSelector()
    gift_selector_instance.select_gift()
