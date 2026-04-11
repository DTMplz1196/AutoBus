"""
Module: star_buff_selector.py
Description: Handles Star Buff selection at the start of a Mirror Dungeon run.
"""
import time
from module.logger.logger import logger
from module.config.config import config_manager, get_asset_path
from module.automation.controller import Controller


class StarBuffSelector:
    def __init__(self):
        # Map JSON config keys to actual image paths
        self.buff_assets = {
            f"buff{i}": get_asset_path(f"images/mirror_dungeon/star_buff/buff_{i}.png")
            for i in range(1, 11)
        }
        self.star_buff_enter = get_asset_path("images/mirror_dungeon/star_buff/star_buff_enter.png")
        self.star_buff_confirm = get_asset_path("images/mirror_dungeon/star_buff/star_buff_confirm.png")
        self.is_star_buff_state_1 = get_asset_path("images/mirror_dungeon/star_buff/is_star_buff_state_1.png")
        self.is_star_buff_state_2 = get_asset_path("images/mirror_dungeon/star_buff/is_star_buff_state_2.png")
        self.bbox_buff_zone = (166, 229, 1696, 1001)

    def proceed_to_enter(self):
        """
        Helper that clicks enter and confirm buttons to start dungeon
        """
        # After validating state, the UI is very stable, so we simply run procedural actions
        # Still there might be unexpected situation(almost 100% no), so we call click_with_retry to
        # ensure this procedural action
        logger.info("Star buff selection completed, proceeding to enter Mirror Dungeon.")
        Controller.click_with_retry(self.star_buff_enter)
        time.sleep(1)
        Controller.click_with_retry(self.star_buff_confirm)

    def select_buff(self):
        """
        Selects star buff based on user preference
        Validate the environment and check if we are in correct state
        """
        Controller.validate_environment()
        buff_preference = config_manager.settings.get("buff_preference", [])

        # Check if both elements not exits, if so, we are not in correct state, return False
        if (not Controller.find_element(self.is_star_buff_state_1)
                and not Controller.find_element(self.is_star_buff_state_2)):
            logger.warning("Not in star buff selection state.")
            return False
        else:
            logger.info("Star buff selection state, acquiring user preference...")

        # If user didn't set any preference, then proceed enter directly
        if not buff_preference:
            logger.info("User decide to not select any star buffs.")
            self.proceed_to_enter()
            return True

        selected_count = 0
        target_count = len(buff_preference)

        # Iterate through preference, scan only the buff zone
        for buff_name in buff_preference:
            buff_path = self.buff_assets.get(buff_name)
            if buff_path and Controller.click_element(buff_path, bbox=self.bbox_buff_zone):
                # Using click_element in if because we increase count only if we click preferred buff successfully
                selected_count += 1
                time.sleep(0.1)

        # Check if the selected count meets target count and report to user
        if selected_count == target_count:
            logger.info(f"Successfully selected {selected_count} buff(s).")
            self.proceed_to_enter()
            return True
        # proceed to enter dungeon either way, only report to user with different log
        else:
            logger.warning(f"Failed to select all preferred star buffs, ({selected_count}/{target_count} selected.)")
            self.proceed_to_enter()
            return True


if __name__ == '__main__':
    star_buff_selector_instance = StarBuffSelector()
    star_buff_selector_instance.select_buff()
