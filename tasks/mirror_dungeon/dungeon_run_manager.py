"""
Module: dungeon_run_manager.py
Description: Main state-machine for "In" Mirror Dungeon automation.
Handles state detection and task dispatching.
"""
import time
from module.logger.logger import logger
from module.automation.controller import Controller
from module.config.config import get_asset_path
from tasks.mirror_dungeon.theme_pack_selector import ThemePackSelector
from tasks.mirror_dungeon.road_in_dungeon import RoadInDungeon
from tasks.mirror_dungeon.battle import Battle
from tasks.mirror_dungeon.identities_selector import IdentitiesSelector
from tasks.mirror_dungeon.event import Event
from tasks.mirror_dungeon.event_failsafe import EventFailsafe
from tasks.mirror_dungeon.shop import Shop
from tasks.mirror_dungeon.gift_selector import GiftSelector
from tasks.mirror_dungeon.reward_selector import RewardSelector
from tasks.mirror_dungeon.result_claim import ResultClaim


class DungeonRunStateManager:
    """
    Manages the detection of game states using template matching and
    predefined bounding boxes for performance optimization.
    """
    def __init__(self):
        # If it's possible, use only 1 definitely appear and distinguishable assets
        # alone with bbox to optimize efficiency

        # "Pack search icon"
        self.is_theme_pack_state = get_asset_path("images/mirror_dungeon/theme_pack/pack_search.png")
        self.bbox_theme_pack_state = (172, 64, 399, 157)

        # "Legend" icon(explain node's details)
        self.is_map_state_1 = get_asset_path("images/mirror_dungeon/road_in_dungeon/is_node_selection_state_1.png")
        self.bbox_map_state_1 = (1813, 153, 1891, 221)
        # Bus icon
        self.is_map_state_2 = get_asset_path("images/mirror_dungeon/road_in_dungeon/current_location.png")

        # "To Battle!" icon
        self.is_identity_state = get_asset_path("images/identity_select/in_identities_selection_state_1.png")
        self.bbox_identity_state = (1579, 854, 1861, 984)

        # "Turn" icon, because after entering battle, it's always standby phase,
        # so we only look for "Turn" appears during.
        self.is_battle_state = get_asset_path("images/battle/standby_phase_1.png")
        self.bbox_battle_state = (10, 56, 170, 182)

        # "EGO Gift" icon
        self.is_event_state = get_asset_path("images/mirror_dungeon/event/ego_gift_icon.png")
        self.bbox_event_state = (38, 47, 131, 129)

        # "Shop" icon
        self.is_shop_state = get_asset_path("images/mirror_dungeon/shop/shop.png")
        self.bbox_shop_state = (176, 164, 614, 275)

        # "Acquire gift" icon appears at the top of the EGO gift
        self.is_gift_select_state = get_asset_path("images/mirror_dungeon/gift_acquire/acquire_gift.png")
        self.bbox_gift_select_state = (12, 234, 1907, 325)

        # "Select Encounter Reward Card" icon
        self.is_reward_state = get_asset_path("images/mirror_dungeon/encounter_reward/encounter_reward_1.png")
        self.bbox_reward_state = (336, 182, 1264, 294)

        # "Combat tips" icon
        self.is_loading = get_asset_path("images/mirror_dungeon/road_to_dungeon/loading.png")
        self.bbox_loading = (1595, 437, 1900, 542)

        # "ictory" without V icon
        self.is_result_state = get_asset_path("images/mirror_dungeon/result/result_state_1.png")
        self.bbox_result = (1475, 180, 1786, 292)

    def get_state(self):
        """
        Scans the screen for known UI anchors to determine the current game state.
        """

        # Order if according to frequencies of the states occur, optimizes efficiency
        if (Controller.find_element(self.is_map_state_2) or
                Controller.find_element(self.is_map_state_1, bbox=self.bbox_map_state_1)):
            return "Map navigation state"
        if Controller.find_element(self.is_identity_state, bbox=self.bbox_identity_state):
            return "Identity selection state"
        if Controller.find_element(self.is_battle_state, bbox=self.bbox_battle_state):
            return "Battle state"
        if Controller.find_element(self.is_event_state, bbox=self.bbox_event_state):
            return "Event state"
        if Controller.find_element(self.is_reward_state, bbox=self.bbox_reward_state):
            return "Reward selection state"
        if Controller.find_element(self.is_gift_select_state, bbox=self.bbox_gift_select_state):
            return "Gift selection state"
        if Controller.find_element(self.is_theme_pack_state, bbox=self.bbox_theme_pack_state):
            return "Theme pack state"
        if Controller.find_element(self.is_shop_state, bbox=self.bbox_shop_state):
            return "Shop state"
        if Controller.find_element(self.is_loading, bbox=self.bbox_loading):
            return "Loading state"
        if Controller.find_element(self.is_result_state, bbox=self.bbox_result):
            return "result state"

        return "Unknown state"


def run_dungeon():
    """
    Main execution loop. Continuously checks the game state and
    executes the relevant sub-task until the dungeon is cleared.
    """

    state_manager_instance = DungeonRunStateManager()
    theme_pack_selector_instance = ThemePackSelector()
    road_in_dungeon_instance = RoadInDungeon()
    identities_selector_instance = IdentitiesSelector()
    battle_instance = Battle()
    event_instance = Event()
    event_failsafe_instance = EventFailsafe()
    shop_instance = Shop()
    gift_selector_instance = GiftSelector()
    reward_selector_instance = RewardSelector()
    result_claim_instance = ResultClaim()

    while True:
        Controller.validate_environment()
        current_state = state_manager_instance.get_state()
        logger.info(f"Current game state: {current_state}")

        try:
            if current_state == "Theme pack state":
                theme_pack_selector_instance.select_theme()

            elif current_state == "Map navigation state":
                road_in_dungeon_instance.select_node()

            elif current_state == "Identity selection state":
                identities_selector_instance.select_identity()

            elif current_state == "Battle state":
                battle_instance.battle()

            elif current_state == "Event state":
                # Primary logic first, if it returns False, then use Failsafe
                if not event_instance.pass_event():
                    logger.warning("Primary event logic failed, switching to Failsafe...")
                    event_failsafe_instance.pass_event()

            elif current_state == "Shop state":
                shop_instance.shopping()

            elif current_state == "Gift selection state":
                gift_selector_instance.select_gift()

            elif current_state == "Reward selection state":
                reward_selector_instance.select_reward()

            elif current_state == "Loading state":
                logger.info("Game is loading...")
                time.sleep(10)

            elif current_state == "Unknown state":
                logger.warning("Unknown state detected. Might be connecting...")
                time.sleep(10)

            elif current_state == "result state":
                result_claim_instance.claim_result()
                logger.info("Dungeon run completed, exit.")
                break

        except Exception as e:
            logger.error(f"Crawl Loop Error: {e}")
            time.sleep(2)

        time.sleep(1)


if __name__ == '__main__':
    run_dungeon()
