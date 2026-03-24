"""
Module: enter_mirror_dungeon.py
Description: Navigation module of entering from Home to Mirror Dungeon
"""
import time
from module.config.config import get_asset_path
from module.automation.controller import Controller
from module.logger.logger import logger


class Enter_Mirror_Dungeon:
    """
    Manages procedural navigation into mirror dungeon.

    Uses hybrid of state machine and procedural steps
    """
    def __init__(self):
        self.is_home_state = get_asset_path("images/mirror_dungeon/road_to_dungeon/is_home_state.png")
        self.drive_unpressed = get_asset_path("images/mirror_dungeon/road_to_dungeon/drive_unpressed.png")
        self.drive_pressed = get_asset_path("images/mirror_dungeon/road_to_dungeon/drive_pressed.png")
        self.mirror_dungeon_icon= get_asset_path("images/mirror_dungeon/road_to_dungeon/mirror_dungeon_icon1.png")
        self.is_mirror_dungeon_state = (
            get_asset_path("images/mirror_dungeon/road_to_dungeon/is_mirror_dungeon_state.png")
        )
        self.enter_btn = get_asset_path("images/mirror_dungeon/road_to_dungeon/enter_mirror_dungeon.png")
        self.confirm_enter = get_asset_path("images/mirror_dungeon/road_to_dungeon/confirm_enter.png")
        self.resume = get_asset_path("images/mirror_dungeon/road_to_dungeon/resume.png")
        self.bbox_drive_btn = (1413, 942, 1540, 1069)
        self.bbox_mirror_dungeon_icon = (515, 390, 841, 603)

    def enter_mirror_dungeon(self):
        """
        Navigates through home to mirror dungeon
        """
        logger.info("Task: Navigating to Mirror Dungeon...")
        step = 0
        loop_count = 5

        while loop_count > 0:
            Controller.validate_environment()

            # Sometimes the dungeon is already in process
            # once "resume" is found click it and return true(pipeline finished)
            if Controller.find_element(self.resume):
                logger.info("Mirror dungeon already in progress, clicking Resume.")
                Controller.click_element(self.resume)
                logger.info("Mirror dungeon entered...")
                return True

            if step == 0:
                # Check if bottom UI for home exists, if so, clicks drive btn, proceeds to step 1
                if Controller.find_element(self.is_home_state):
                    logger.info("At home page, clicking Drive.")
                    # Add bbox to scan only a specific area to avoid similar button noise, also for performance
                    Controller.click_element(self.drive_unpressed, bbox=self.bbox_drive_btn)
                    step = 1
                    continue

                # If we found drive btn already pressed, then we proceed to step 1
                elif Controller.find_element(self.drive_pressed, bbox=self.bbox_drive_btn):
                    logger.info("Drive already pressed, looking for mirror dungeon Icon.")
                    step = 1
                    continue

                # Check if sidebar of mirror dungeon interface exists, if exits, clicks enter and proceed to step 2
                elif Controller.find_element(self.is_mirror_dungeon_state):
                    logger.info("Already in mirror dungeon interface, clicking Enter.")
                    Controller.click_element(self.enter_btn)
                    step = 2
                    continue

            # State where we head to drive btn pressed interface
            elif step == 1:
                # Execute procedural actions to enter Mirror Dungeon, then proceeds to step2
                if Controller.click_element(self.mirror_dungeon_icon, bbox=self.bbox_mirror_dungeon_icon):
                    logger.info("Clicking mirror dungeon icon and enter.")
                    # Waiting 2 sec for the slashing animation ended
                    time.sleep(2)
                    Controller.click_element(self.enter_btn)
                    step = 2
                    continue

            # State where we head after clicking enter btn
            elif step == 2:
                # Confirm enter and return True, pipeline finished
                if Controller.find_element(self.confirm_enter):
                    logger.info("Confirming Enter...")
                    Controller.click_element(self.confirm_enter)
                    logger.info("Mirror dungeon entered.")
                    return True

            # Try up to 5 times if we fail to find any elements like resume, or elements in step 0
            loop_count -= 1
            logger.warning(f"Enter failed, Retrying... ({loop_count} attempts left)")
            time.sleep(1)

        logger.info("Fail to enter mirror dungeon.")
        return False


if __name__ == '__main__':
    enter_mirror_dungeon_instance = Enter_Mirror_Dungeon()
    enter_mirror_dungeon_instance.enter_mirror_dungeon()
