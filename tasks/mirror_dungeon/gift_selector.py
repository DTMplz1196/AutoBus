"""
Module: gift_selector.py
Description: Handles EGO Gift selection scenario.
"""
import time
from module.logger.logger import logger
from module.automation.controller import Controller
from module.config.config import config_manager, get_asset_path


class GiftSelector:
    def __init__(self):
        self.acquire_gift = get_asset_path("images/mirror_dungeon/gift_acquire/acquire_gift.png")
        self.select = get_asset_path("images/mirror_dungeon/gift_acquire/select.png")
        self.confirm = get_asset_path("images/mirror_dungeon/gift_acquire/confirm.png")

        self.gift_type = {
            f"gift{i}": get_asset_path(f"images/mirror_dungeon/gift_acquire/gift_{i}.png")
            for i in range(1, 8)
        }
        self.bbox_gift_type = (17, 243, 1902, 459)

    def select_gift(self):
        """
        Detects gift selection scenario and clicks preferred type based on user config.
        """

        Controller.validate_environment()

        # Ensure we are in correct state by checking "acquire_gift"
        if not Controller.find_element(self.acquire_gift):
            logger.warning("Not in gift selection state.")
            return False
        else:
            logger.info("In gift selection state, proceeding...")

        # Retrieve preference from config
        gift_preference = config_manager.settings.get("gift_preference")
        gift_path = self.gift_type.get(gift_preference)

        if not gift_preference:
            logger.warning("User preference not set, set preference first!")

        # Choose according to user preference, setting a bbox to
        # avoid matching template to the similar icon in EGO gift description
        if gift_path and Controller.find_element(gift_path, bbox=self.bbox_gift_type):
            logger.info(f"Preferred gift type {gift_preference} found, selecting...")
            Controller.click_with_retry(gift_path, bbox=self.bbox_gift_type)
        # If no preference or preferred gift not found, choosing randomly(acquire_gift icon)
        else:
            logger.info("Preferred gift type not found or user didn't set preference. Choosing randomly...")
            Controller.click_with_retry(self.acquire_gift)

        # Wait 1 sec for select button lights up
        time.sleep(1)

        # Click select button
        if Controller.find_element(self.select):
            Controller.click_with_retry(self.select)
            time.sleep(2)
        else:
            logger.warning("Select not found.")
            return False

        # Click confirm button
        if Controller.find_element(self.confirm):
            logger.info("Ego gift get!")
            Controller.click_element(self.confirm)
            return True

        else:
            logger.warning("Fail to confirm, might stuck")
            return False


if __name__ == '__main__':
    gift_selector_instance = GiftSelector()
    gift_selector_instance.select_gift()
