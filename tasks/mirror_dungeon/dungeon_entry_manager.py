"""
Module: dungeon_entry_manager.py
Description: Handles the sequence of actions required to enter a Mirror Dungeon,
from the Home screen through team and gift selection.
"""
import time
from module.config.config import get_asset_path
from tasks.mirror_dungeon.enter_mirror_dungeon import Enter_Mirror_Dungeon
from tasks.mirror_dungeon.team_selector import Team_Selector
from module.automation.controller import Controller
from module.logger.logger import logger
from tasks.mirror_dungeon.star_buff_selector import StarBuffSelector
from tasks.mirror_dungeon.start_gift_selector import GiftSelector


class ToDungeonStateManager:
    """
    Identifies the UI state during the 'Road to Dungeon' phase.
    Uses localized Bounding Boxes to optimize efficiency.
    """

    def __init__(self):
        # If it's possible, use only 1 definitely appear and distinguishable assets
        # alone with bbox to optimize efficiency

        # Bottom bar in home page
        self.is_home_state_1 = get_asset_path("images/mirror_dungeon/road_to_dungeon/is_home_state.png")
        self.bbox_home_state_1 = (1146, 930, 1906, 1070)

        # "Drive" button in when it's not pressed
        self.is_home_state_2 = get_asset_path("images/home/drive_not_pressed.png")
        self.bbox_home_state_2 = (1397, 931, 1563, 1073)

        # Sidebar of Mirror Dungeon UI
        self.is_home_state_3 = get_asset_path("images/mirror_dungeon/road_to_dungeon/is_mirror_dungeon_state.png")
        self.bbox_home_state_3 = (68, 286, 521, 928)

        # "Starlight bonus" only appears at dungeon team selection, won't mix with identities selection state
        self.is_dungeon_team_select_state_1 = get_asset_path("images/teams/is_dungeon_team_selection_state.png")
        self.bbox_dungeon_team_select_state_1 = (1576, 789, 1869, 997)

        # "Confirm" button at specific are
        self.is_dungeon_team_select_state_2 = get_asset_path("images/teams/teams_confirm.png")
        self.bbox_dungeon_team_select_state_2 = (1591, 857, 1853, 981)

        # "Select All Graces" UI
        self.is_star_buff_state = get_asset_path("images/mirror_dungeon/star_buff/is_star_buff_state_2.png")
        self.bbox_star_buff_state = (1692, 741, 1899, 993)

        # "Selected EGO Gift" icon
        self.is_start_gift_state = get_asset_path("images/mirror_dungeon/start_gift/select_gift_anchor.png")
        self.bbox_start_gift_state = (1102, 216, 1563, 334)

        # "Combat tips" icon
        self.is_loading_state = get_asset_path("images/mirror_dungeon/road_to_dungeon/loading.png")
        self.bbox_loading = (1595, 437, 1900, 542)

        # "Pack search icon"
        self.is_theme_pack_state = get_asset_path("images/mirror_dungeon/theme_pack/pack_search.png")
        self.bbox_theme_pack_state = (172, 64, 399, 157)

    def get_state(self):
        """
        Scans the screen for known UI anchors to determine the current game state.
        """

        # Order if according to procedure of the states occur, optimizes efficiency
        if (Controller.find_element(self.is_home_state_1, bbox=self.bbox_home_state_1)
                or Controller.find_element(self.is_home_state_2, bbox=self.bbox_home_state_2)
                or Controller.find_element(self.is_home_state_3, bbox=self.bbox_home_state_3)):
            return "Home state"
        if (Controller.find_element(self.is_dungeon_team_select_state_1, bbox=self.bbox_dungeon_team_select_state_1)
                and Controller.find_element(self.is_dungeon_team_select_state_2,
                                            bbox=self.bbox_dungeon_team_select_state_2)):
            return "Dungeon team selection state"
        if Controller.find_element(self.is_star_buff_state, bbox=self.bbox_star_buff_state):
            return "Star buff selection state"
        if Controller.find_element(self.is_start_gift_state, bbox=self.bbox_start_gift_state):
            return "Start gift selection state"
        if Controller.find_element(self.is_loading_state, bbox=self.bbox_loading):
            return "Loading state"

        return "Unknown state"


def to_dungeon():
    """
    Executes the entry sequence before entering Mirror Dungeon.
    Loops until the bot successfully enters the Mirror Dungeon(Unknow state).
    """
    logger.info("--- Starting One Dungeon Loop ---")

    state_manager_instance = ToDungeonStateManager()
    team_selector_instance = Team_Selector()
    enter_mirror_dungeon_instance = Enter_Mirror_Dungeon()
    star_buff_selector_instance = StarBuffSelector()
    gift_selector_instance = GiftSelector()

    while True:
        Controller.validate_environment()
        current_state = state_manager_instance.get_state()
        logger.info(f"Current game state: {current_state}")

        try:
            if current_state == "Home state":
                enter_mirror_dungeon_instance.enter_mirror_dungeon()

            elif current_state == "Dungeon team selection state":
                team_selector_instance.select_team()

            elif current_state == "Star buff selection state":
                star_buff_selector_instance.select_buff()

            elif current_state == "Start gift selection state":
                gift_selector_instance.select_gift()

            elif current_state == "Loading state":
                logger.info("Loading to enter mirror dungeon... please wait")
                time.sleep(5)

            # We don't check or use theme pack state here because the dungeon might already been in progress
            # So any other state other than these states result in breaking the loop, so we can proceed dungeon run
            elif current_state == "Unknown state":
                logger.info("Enter Mirror Dungeon successfully!")
                break

        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(2)

        time.sleep(1)


if __name__ == '__main__':
    to_dungeon()
