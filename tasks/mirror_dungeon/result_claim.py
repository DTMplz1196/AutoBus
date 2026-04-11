"""
Module: result_claim.py
Description: Handles reward claiming after complete dungeon run and returns to the main menu.
"""
import time
from module.logger.logger import logger
from module.automation.controller import Controller
from module.config.config import get_asset_path


class ResultClaim:

    def __init__(self):
        self.result_state = [
            get_asset_path(f"images/mirror_dungeon/result/result_state_{i}.png") for i in range(1, 3)
        ]
        self.result_confirm = get_asset_path("images/mirror_dungeon/result/result_confirm.png")
        self.summary_phase = [
            get_asset_path(f"images/mirror_dungeon/result/summary_phase_{i}.png") for i in range(1, 5)
        ]
        self.claim_rewards = get_asset_path("images/mirror_dungeon/result/claim_rewards.png")
        self.claim_with_enkephalin = get_asset_path("images/mirror_dungeon/result/claim_with_enkephalin.png")
        self.claim_with_confirm = get_asset_path("images/mirror_dungeon/result/claim_with_confirm.png")
        self.final_confirm = get_asset_path("images/mirror_dungeon/result/final_confirm.png")
        self.drive_unpressed = get_asset_path("images/mirror_dungeon/road_to_dungeon/drive_unpressed.png")
        self.bbox_result_confirm = (1521, 811, 1818, 945)

    def claim_result(self):
        """
        Executes the procedure required to claim reward and return to home.
        """
        Controller.validate_environment()

        # Ensure we are in correct state by checking statistic icon and "ictory", ignore v because it sometimes may be
        # covered by other UI elements like EX-clear
        if not any(Controller.find_element(path) for path in self.result_state):
            logger.warning("Not in result state.")
            return False
        else:
            logger.info("In result state, proceeding...")

        Controller.click_with_retry(self.result_confirm)
        # Wait 2 sec for secondary result window appears
        time.sleep(2)

        # Using for loop up to 5 tries in case procedural actions go wrong
        for i in range(5):
            Controller.validate_environment()
            # Report to user one dungeon run has completed
            if Controller.find_element(self.drive_unpressed):
                logger.info("Mirror Dungeon completed! Rewards have been claimed and return to home")
                return True

            # Check if we are in summary_phase by "Exploration Complete",
            # "Dungeon Progress", "Last Reached", "Total progress"
            if any(Controller.find_element(path) for path in self.summary_phase):
                logger.info("In summary phase, proceeding...")
                Controller.click_with_retry(self.claim_rewards)
                time.sleep(2)
                # Procedural actions using click_with_retry in case clicking failed
                if Controller.find_element(self.claim_with_enkephalin):
                    logger.info("Dungeon run completed, claiming rewards...")
                    Controller.click_with_retry(self.claim_with_enkephalin)
                    time.sleep(2)
                    Controller.click_with_retry(self.claim_with_confirm)
                    time.sleep(5)
                    Controller.click_with_retry(self.result_confirm)
                    time.sleep(2)
                    Controller.click_with_retry(self.final_confirm)
                    time.sleep(2)
                    Controller.click_with_retry(self.final_confirm)
                    time.sleep(10)

        logger.warning("Failed to return home after 5 tries")


if __name__ == '__main__':
    result_claim_instance = ResultClaim()
    result_claim_instance.claim_result()
