"""
Module: road_in_dungeon.py
Description: Navigation in Mirror Dungeon using Priority and Geometric Fallback.
"""
import time
from module.logger.logger import logger
from module.config.config import config_manager, get_asset_path
from module.automation.controller import Controller


class RoadInDungeon:
    def __init__(self):
        # Set fallback navigation as default since it saves time
        self.strategy = config_manager.settings.get("road_strategy", "fallback")
        self.dungeon_nodes = {
            "event_nodes": [get_asset_path(f"images/mirror_dungeon/road_in_dungeon/event/event_{i}.png")
                            for i in range(1, 10)],
            "regular_encounter": [
                get_asset_path(f"images/mirror_dungeon/road_in_dungeon/battle/regular_encounter_{i}.png")
                for i in range(1, 10)],
            "focused_encounter": [
                get_asset_path(f"images/mirror_dungeon/road_in_dungeon/battle/focused_encounter_{i}.png")
                for i in range(1, 10)]
        }
        self.is_node_selection_state_1 = get_asset_path(
            "images/mirror_dungeon/road_in_dungeon/is_node_selection_state_1.png")
        self.is_node_selection_state_2 = get_asset_path(
            "images/mirror_dungeon/road_in_dungeon/is_node_selection_state_2.png")
        self.current_location = get_asset_path("images/mirror_dungeon/road_in_dungeon/current_location.png")
        self.enter_btn = get_asset_path("images/mirror_dungeon/road_in_dungeon/enter.png")
        self.bbox_state_2 = (1810, 330, 1888, 407)

    def select_node(self):
        """
        Navigates to different nodes based on priority: event > regular > focused to optimize efficiency
        if matching failed, clicking different direction based on bus location using offsets
        Validate the environment and check if we are in correct state
        """
        Controller.validate_environment()

        current_location = Controller.find_element(self.current_location)

        # If bus icon and "node info" and "active effects" are all missing, we are not in correct state
        # Set bbox for state_2 because "active effects" are similar to event node
        if not current_location and not Controller.find_element(self.is_node_selection_state_1) \
                and not Controller.find_element(self.is_node_selection_state_2, bbox=self.bbox_state_2):
            logger.warning("Not in node selection state.")
            return False

        # Check if current node hasn't been passed
        if current_location:
            Controller.click_element(self.current_location)
            time.sleep(1)
            if Controller.find_element(self.enter_btn):
                logger.info("Resuming unpassed node...")
                Controller.click_with_retry(self.enter_btn)
                return True
            else:
                logger.info("Current node passed, navigating to next node...")

        # If enter btn is found, we enter directly
        if Controller.find_element(self.enter_btn):
            logger.info("Entering nodes")
            return Controller.click_with_retry(self.enter_btn)

        priority_order = [
            "event_nodes", "regular_encounter", "focused_encounter"
        ]

        # If preferred strategy is fallback we call fallback_navigation to move to next node based on clicking
        # different direction using offsets based on current location, optimize efficiency
        if self.strategy == "fallback":
            logger.info("Using Fallback navigation strategy: skipping nodes matching, using offsets.")
            return self.fallback_navigation()

        # If preferred strategy is priority we match template from event to regular encounter to focused encounter
        # Because of time spending: event < regular < focused
        if self.strategy == "priority":
            logger.info("Using priority strategy.")
            for nodes in priority_order:
                for nodes_path in self.dungeon_nodes.get(nodes, []):
                    if Controller.click_element(nodes_path):
                        logger.info(f"{nodes} found, clicking...")
                        # Wait for UI transition
                        time.sleep(2)

                        if Controller.find_element(self.enter_btn):
                            Controller.click_with_retry(self.enter_btn)
                            return True
                        else:
                            # However, it may result in clicking an unreachable nodes
                            # If this is the case, we use fallback strategy
                            logger.info(f"{nodes} found, but clicking seems failed, using fallback navigation.")
                            return self.fallback_navigation()
            # Globally fallback,  if none of the assets match
            # we might in a new theme pack, use fallback strategy in this case
            return self.fallback_navigation()
        logger.error(f"Invalid strategy: {self.strategy}.")
        return False

    def fallback_navigation(self):
        """
        Geometric navigation: Clicks relative to the Bus position if nodes don't match.
        """
        Controller.validate_environment()

        current_location = Controller.find_element(self.current_location)

        # Sometimes the map is dragged so the bus isn't in current client area, add a check and inform user
        if not current_location:
            logger.warning("Couldn't find bus coordinates, try dragging map until it appears.")

        logger.info(f"Nodes matching failed, attempting fallback navigation(based on bus location:{current_location})...")

        # Calculated using click_validator.py
        offsets = [
            (390, 0, "Right"),
            (390, -300, "Top-Right-normal"),
            (390, 300, "Bottom-Right-normal")
        ]

        # Trying different offsets if fails
        for ox, oy, direction in offsets:
            logger.info(f"Trying {direction} direction...")
            Controller.click_with_retry(self.current_location, x_offset=ox, y_offset=oy)
            # Wait for UI transition
            time.sleep(2)
            # If enter btn appears, the navigation succeeds, if not, trying next offsets
            if Controller.click_element(self.enter_btn):
                logger.info(f"Fallback navigation {direction} succeeded, entering nodes...")
                return True
        else:
            logger.warning("Fallback navigation failed.")
            return False


if __name__ == '__main__':
    road_in_dungeon_instance = RoadInDungeon()
    road_in_dungeon_instance.select_node()
