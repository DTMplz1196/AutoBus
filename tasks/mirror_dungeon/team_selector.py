"""
Module: team_selector.py
Description: Handles team selection based on JSON configuration.
"""
import time
from module.config.config import get_asset_path
from module.automation.controller import Controller
from module.logger.logger import logger
from module.config.config import config_manager


class Team_Selector:
    def __init__(self):
        # Map JSON config keys to actual image paths
        self.team_assets = {
            f"teams#{i}": get_asset_path(f"images/teams/teams_#{i}.png")
            for i in range(1, 7)
        }
        self.teams_confirm = get_asset_path("images/teams/teams_confirm.png")
        self.lower_average_level_anchor = get_asset_path("images/teams/lower_average_level.png")
        self.is_dungeon_team_selection_state = get_asset_path("images/teams/is_dungeon_team_selection_state.png")
        self.bbox_is_dungeon_team_selection_state = (1598, 810, 1848, 980)
        self.bbox_team_sidebar = (98, 440, 297, 858)

    def select_team(self):
        """
        Selects team based on user preference
        Validate the environment and check if we are in correct state
        """
        # Get preference from the JSON
        team_preference = config_manager.settings.get("team_preference", "teams#1")
        team_path = self.team_assets.get(team_preference)

        if not team_preference:
            logger.warning(f"No team preference set.")
            return False

        loop_count = 5
        while loop_count > 0:
            Controller.validate_environment()

            # Check if we are in team selection state first with bbox filtering noise
            if not Controller.find_element(self.is_dungeon_team_selection_state,
                                           bbox=self.bbox_is_dungeon_team_selection_state):
                logger.warning("Not in team selection state.")
                time.sleep(1)
                loop_count -= 1
                continue

            # Check for different assets for different team preference focusing only sidebar area
            if Controller.click_with_retry(team_path, bbox=self.bbox_team_sidebar):
                logger.info(f"Team detected: {team_preference}. Selecting...")
                time.sleep(0.1)
                logger.info("Team selected, confirming...")
                Controller.click_with_retry(self.teams_confirm)
                time.sleep(2)
                # Wait for level window drops down and click offsets based on anchor(eventually clicks confirm)
                # Avoid clicking similar confirm btn at the same interface, can also be done with bbox
                Controller.click_element(self.lower_average_level_anchor, y_offset=325, x_offset=200)
                return True

            loop_count -= 1
            logger.info(f"Team {team_preference} not found. Retrying... ({loop_count} attempts left)")

        logger.warning(f"Could not find matching element for {team_preference} after multiple attempts.")
        return False


if __name__ == '__main__':
    team_selector_instance = Team_Selector()
    team_selector_instance.select_team()
