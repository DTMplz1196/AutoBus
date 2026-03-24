"""
Module: shop.py
Description: Handles Mirror Dungeon Shop interactions including skill replacement,
keyword-based refreshing, and gift purchasing.
"""
import time
from module.logger.logger import logger
from module.automation.controller import Controller
from module.config.config import config_manager, get_asset_path


class Shop:
    def __init__(self):
        self.gift_type = {
            f"gift{i}": get_asset_path(f"images/mirror_dungeon/shop/gift_{i}.png")
            for i in range(1, 8)
        }
        self.confirm = get_asset_path("images/mirror_dungeon/shop/confirm.png")
        self.confirm_leave = get_asset_path("images/mirror_dungeon/shop/confirm_leave.png")
        self.purchase = get_asset_path("images/mirror_dungeon/shop/purchase.png")
        self.leave = get_asset_path("images/mirror_dungeon/shop/leave.png")
        self.replace_skill_UI = get_asset_path("images/mirror_dungeon/shop/replace_skill.png")
        self.cancel = get_asset_path("images/mirror_dungeon/shop/cancel.png")
        self.shop_state = get_asset_path("images/mirror_dungeon/shop/shop.png")
        self.skill_type = {
            f"skill_type{x}": get_asset_path(f"images/mirror_dungeon/shop/skill_type_{x}.png")
            for x in range(1, 4)
        }
        self.refresh_not_enough_cost = get_asset_path("images/mirror_dungeon/shop/refresh_1.png")
        self.refresh_enough_cost = get_asset_path("images/mirror_dungeon/shop/refresh_2.png")
        self.keyword_refresh = get_asset_path("images/mirror_dungeon/shop/keyword_refresh.png")
        self.refresh_btn = get_asset_path("images/mirror_dungeon/shop/refresh_btn.png")
        self.bbox_shop = (176, 164, 614, 275)
        self.bbox_keyword_refresh = (378, 166, 1201, 286)
        self.bbox_refresh_btn = (1607, 176, 1819, 260)

    def purchase_gift(self, gift_path):
        """
        Helper that handles purchasing EGO gifts based on user preference
        The essence of idea is purchased gifts is shadowed a little bit, so the template matching
        will almost always match the un-purchased gifts
        """
        if Controller.find_element(gift_path):
            logger.info("Preferred gift found, purchasing...")
            Controller.click_with_retry(gift_path)
            # Wait 1 sec for msg pops out
            time.sleep(1)

            # Check if EGO gift has already been purchased by "purchase"
            if Controller.find_element(self.purchase):
                Controller.click_with_retry(self.purchase)
                # Wait 1 sec for confirm msg pops out
                time.sleep(2)
                Controller.click_with_retry(self.confirm)
                logger.info("Gift purchased!")
                # Returns True if it's purchasing scenario, so later the total count are correct increased
                return True

            # If Ego gifts already purchased or not enough costs, then only confirm msg would pop out
            elif Controller.find_element(self.confirm):
                Controller.click_element(self.confirm)
                logger.info("Gift already purchased or not enough cost.")

        return False

    def replace_skill(self):
        """
        Helper that handles replacing skill using offset based clicking
        """
        Controller.validate_environment()
        # Maps skill type key to user preference
        skill_preference = config_manager.settings.get("skill_preference")
        skill_path = self.skill_type.get(skill_preference)

        # If user didn't set any preference, skip replacing skill
        if not skill_preference:
            logger.info("No skill preference set, skipping replacing...")

        # was planning using replace skill UI icon, but after several testing, due to
        # unknown reason the icon couldn't be found even they looks exactly same,
        # so we use offset based on shop icon to replace skill
        if Controller.find_element(self.shop_state, bbox=self.bbox_shop):
            logger.info(f"Replacing available, preference: {skill_preference}")
            Controller.click_element(self.shop_state, bbox=self.bbox_shop, x_offset=550, y_offset=200)
            # Wait 2 sec for replacing skill UI pops out
            time.sleep(2)
            # Check if corresponding replacing type exists by "pay a moderate/large/tremendous price"
            if Controller.find_element(skill_path):
                Controller.click_with_retry(skill_path)
                # Wait 1 sec for specific type UI pops out, animation transition almost instant
                time.sleep(1)
                # Check and dismiss confirm msg
                Controller.click_with_retry(self.confirm)
                # Add a rather long delay since here requires confirmation to the server
                time.sleep(5)
                # Add a 5 tris with 5 sec interval and if failsafe in case internet connection lost scenario
                if not Controller.click_with_retry(self.confirm, 5, 5):
                    logger.warning("Skill replacing failed, check your internet connection!")
                logger.info("Skill replaced")
                return True
            else:
                # In case template matching failed in very rare case, clicking cancel to exit replacing skill
                logger.info("Couldn't find preferred replacing type, canceling...")
                Controller.click_element(self.cancel)
                # Wait 2 sec for replacing skill UI disappear
                time.sleep(2)
                return True

    def leave_shop(self):
        """
        Helper that handles standardized leaving shop procedural actions
        """
        Controller.validate_environment()
        logger.info("Leaving shop...")
        Controller.click_with_retry(self.leave)
        # Wait 1 sec for confirm msg pops out
        time.sleep(1)
        Controller.click_with_retry(self.confirm_leave)
        # Wait 2 sec for animation transition to road state
        time.sleep(2)

    def shopping(self):
        """
        Main execution logic for shop node
        Ensure we are in correct state and handles skill replacing, gift purchasing
        keyword refresh using offsets based on user preference
        """
        Controller.validate_environment()

        # Ensure we are in correct state by checking "Shop" in bbox
        if not Controller.find_element(self.shop_state, bbox=self.bbox_shop):
            logger.warning("Not in shop state.")
            return False
        else:
            logger.info("In shop state, proceeding...")

        # Retrieves the gift path based on the user preference
        gift_preference = config_manager.settings.get("gift_preference")
        gift_path = self.gift_type.get(gift_preference)

        # Keyword refresh offsets relative to "Shop - Keyword Refresh"
        refresh_offsets = {
            "gift1": (-285, 250),
            "gift2": (-50, 250),
            "gift3": (185, 250),
            "gift4": (410, 250),
            "gift5": (640, 250),
            "gift6": (-285, 450),
            "gift7": (-50, 450),
        }

        # If user didn't set any preference, leave shop directly
        if not gift_preference:
            logger.info("No gift preference are set, skipping shopping...")
            self.leave_shop()
            return True

        # Replace skill by calling helper function
        self.replace_skill()
        # Wait 2 sec for stability
        time.sleep(2)

        # Try purchasing preferred EGO gifts up to 3 times upon entering shop
        total_gift_count = 0
        for i in range(3):
            if self.purchase_gift(gift_path):
                total_gift_count += 1
            time.sleep(1)

        # Refresh and purchase loop until "not enough cost" is found
        while True:
            Controller.validate_environment()

            # If not enough cost is found, break the loop
            if Controller.find_element(self.refresh_not_enough_cost):
                logger.info("Not enough cost to refresh, leaving...")
                break

            # If refresh is available
            if Controller.find_element(self.refresh_enough_cost):
                logger.info("Refresh available, refreshing...")
                Controller.click_with_retry(self.refresh_enough_cost)
                # Wait 1 sec for refresh UI pops out
                time.sleep(1)
                ox, oy = refresh_offsets.get(gift_preference)
                # Clicking offsets based on "Shop - Keyword Refresh" with user preference
                # Using bbox to optimize efficiency and in case of mixing
                Controller.click_with_retry(self.keyword_refresh, x_offset=ox, y_offset=oy, bbox=self.bbox_keyword_refresh)
                # Wait 1 sec for clicking to specific icon based on offsets
                time.sleep(1)
                Controller.click_with_retry(self.refresh_btn)
                # Wait a rather long delay for refreshing
                time.sleep(3)

                # Try purchasing EGO Gifts up to 3 times for every refresh
                for a in range(3):
                    if self.purchase_gift(gift_path):
                        total_gift_count += 1
                    # Wait 1 sec for UI stability
                    time.sleep(1)

            else:
                logger.warning("Refresh not found, might lose connection!")
                return False

        # Report to user how many gifts we have purchased based on how many "purchase" template matched
        logger.info(f"Shopping completed, gained {total_gift_count} gifts")
        self.leave_shop()
        return True


if __name__ == '__main__':
    shop_instance = Shop()
    shop_instance.shopping()
