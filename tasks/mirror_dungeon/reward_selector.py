"""
Module: reward_selector.py
Description: Handles reward selection after battle based on user preference (Cost, EGO Gifts, Starlight, EGO resources).
"""
import time
from module.logger.logger import logger
from module.automation.controller import Controller
from module.config.config import config_manager, get_asset_path


class RewardSelector:
    def __init__(self):
        self.reward_state = get_asset_path("images/mirror_dungeon/encounter_reward/encounter_reward_1.png")
        self.reward_type = {
            f"reward{i}": get_asset_path(f"images/mirror_dungeon/encounter_reward/reward_{i}.png")
            for i in range(1, 6)
        }
        self.select_reward_card = get_asset_path("images/mirror_dungeon/encounter_reward/select_reward_card.png")
        self.confirm = get_asset_path("images/mirror_dungeon/encounter_reward/confirm.png")
        self.ego_gift_get = get_asset_path("images/mirror_dungeon/encounter_reward/ego_gift_get.png")
        self.bbox_reward_area = (201, 334, 1780, 552)

    def select_reward(self):
        """
        Detects reward state and handles selecting the best available option based on user preference.
        """
        Controller.validate_environment()

        # Check if we are in correct state by "Select Encounter Reward Card"
        if not Controller.find_element(self.reward_state):
            logger.warning("Not in reward selection state,")
            return False
        else:
            logger.info("In reward selection state, proceeding...")

        # Map reward keys to an ordered list with user preference
        reward_preference = config_manager.settings.get("reward_preference", [])
        reward_path = None

        # Check which reward that user preferred exists in the game client, if not, check next preference
        for preference in reward_preference:
            path = self.reward_type.get(preference)
            # Add a bbox to restrain search area to optimize efficiency
            if path and Controller.find_element(path, bbox=self.bbox_reward_area):
                reward_path = path
                break

        # If we found corresponding preference both in config file and game client are, click it
        if reward_path:
            logger.info(f"preferred reward type {reward_preference} found, selecting...")
            # Using click_with_retry method to ensure clicking the preferred reward since sometimes its background
            # brightness may vary due to the level of reward
            Controller.click_with_retry(reward_path, bbox=self.bbox_reward_area)
        # If not, click the middle one using calculated offsets based on "Select Encounter Reward Card"
        else:
            logger.info("preferred reward type not found or user didn't set preference. Choosing randomly...")
            Controller.click_element(self.select_reward_card, x_offset=185, y_offset=300)

        # Wait 1 sec for confirm btn lights up
        time.sleep(1)
        # Check and click confirm btn in normal scenario
        if Controller.find_element(self.confirm):
            Controller.click_with_retry(self.confirm)
            logger.info("Reward selected, confirming...")
            # Wait 1 sec in case it's a gaining EGO gift reward to let msg pops out
            time.sleep(1)
            # In case of gaining EGO gift reward by checking if there's "EGO Gift Get!",
            # if so, clicks confirm to dismiss msg
            if Controller.find_element(self.ego_gift_get):
                logger.info("The reward acquired is EGO gift.")
                Controller.click_with_retry(self.confirm)
            Controller.click_with_retry(self.confirm)
            # Wait 3 sec for animation transition to road/acquire gift after boss state, etc...
            time.sleep(3)
            return True
        else:
            logger.warning("Confirm not found, might stuck.")
            return False


if __name__ == '__main__':
    reward_selector_instance = RewardSelector()
    reward_selector_instance.select_reward()
