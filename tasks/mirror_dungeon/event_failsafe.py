"""
Module: event_failsafe.py
Description: State-machine based event handler.
Acts as a backup to the event.py logic by identifying and reacting to screen states.
"""
import time
from module.logger.logger import logger
from module.config.config import get_asset_path
from module.automation.controller import Controller
from tasks.mirror_dungeon.event import Event


class EventFailsafe:
    def __init__(self):
        self.in_event_state = [
            get_asset_path("images/mirror_dungeon/event/event_skip.png"),
            get_asset_path("images/mirror_dungeon/event/event_state_1.png"),
            get_asset_path("images/mirror_dungeon/event/ego_gift_icon.png")
        ]
        self.skip = get_asset_path("images/mirror_dungeon/event/event_skip.png")
        self.proceed = get_asset_path("images/mirror_dungeon/event/proceed.png")
        self.commence = get_asset_path("images/mirror_dungeon/event/commence.png")
        self.continue_btn = get_asset_path("images/mirror_dungeon/event/continue.png")
        self.very_high = get_asset_path("images/mirror_dungeon/event/very_high.png")
        self.high = get_asset_path("images/mirror_dungeon/event/high.png")
        self.normal = get_asset_path("images/mirror_dungeon/event/normal.png")
        self.low = get_asset_path("images/mirror_dungeon/event/low.png")
        self.very_low = get_asset_path("images/mirror_dungeon/event/very_low.png")
        self.choice = get_asset_path("images/mirror_dungeon/event/choice_icon.png")
        self.result = get_asset_path("images/mirror_dungeon/event/result.png")
        self.gain = [
            get_asset_path("images/mirror_dungeon/event/to_gain_1.png"),
            get_asset_path("images/mirror_dungeon/event/to_gain_2.png"),
            get_asset_path("images/mirror_dungeon/event/maybe_gain.png"),
            get_asset_path("images/mirror_dungeon/event/gain.png")
        ]
        self.earn = get_asset_path("images/mirror_dungeon/event/to_earn.png")
        self.predicted_odds = [
            get_asset_path("images/mirror_dungeon/event/very_high.png"),
            get_asset_path("images/mirror_dungeon/event/high.png"),
            get_asset_path("images/mirror_dungeon/event/normal.png"),
            get_asset_path("images/mirror_dungeon/event/low.png"),
            get_asset_path("images/mirror_dungeon/event/very_low.png")
        ]
        self.confirm_after_gain = get_asset_path("images/mirror_dungeon/event/confirm_after_gain.png")
        self.bbox_odds = (8, 938, 1413, 1073)

    def check_event_phase(self):
        """
        Identifies the current UI state regardless of event logic.
        """
        # Order if by the rareness of each state occurs
        if any(Controller.find_element(path) for path in self.gain):
            logger.info("Choice select phase")
            return "choice_gain"

        if Controller.find_element(self.continue_btn):
            logger.info("Continue")
            return "continue"

        if Controller.find_element(self.proceed):
            logger.info("Proceed")
            return "proceed"

        if Controller.find_element(self.confirm_after_gain):
            logger.info("Event passed")
            return "passed"

        # If we find any odds, we are in check state. Check if commence button exists to determine which phase we are in
        if any(Controller.find_element(path, bbox=self.bbox_odds) for path in self.predicted_odds):
            if not Controller.find_element(self.commence):
                logger.info("Check state, phase: incomplete")
                return "check_incomplete"
            else:
                logger.info("Check state, phase: complete")
                return "check_complete"

    def pass_event(self):
        """
        State-machine loop to pass event.

        Handles actions based on state.
        Much less efficiency but more reliability.
        """
        event_state = any(Controller.find_element(path) for path in self.in_event_state)
        Controller.validate_environment()

        # Ensure we are in correct state by checking "skip", EGO gift icon, handle of event
        if not event_state:
            logger.info("Not in event state.")
            return False
        else:
            logger.info("In event state, proceeding failsafe event handler...")

        while True:
            Controller.validate_environment()
            phase = self.check_event_phase()

            # If no phases are detected, meaning we need to skip event logs
            if not phase:
                for s in range(8):
                    if Controller.find_element(self.skip):
                        Controller.click_element(self.skip)
                        time.sleep(0.1)
                # Back to start and check phase again after skipping
                continue

            logger.info(f"State: {phase}")

            # Find which specific gain icon is visible to click it
            if phase == "choice_gain":
                current_gain_path = next((path for path in self.gain if Controller.find_element(path)), None)
                if current_gain_path:
                    logger.info("Click to gain")
                    Controller.click_element(current_gain_path)
                    time.sleep(2)
                else:
                    logger.warning("Phase was choice_gain but specific icon not found for clicking")

            elif phase == "continue":
                Controller.click_with_retry(self.continue_btn)
                time.sleep(2)

            elif phase == "proceed":
                Controller.click_with_retry(self.proceed)
                time.sleep(2)

            elif phase == "passed":
                Controller.click_with_retry(self.confirm_after_gain)
                return True

            elif phase == "check_incomplete":
                Event().try_highest_odds()

            elif phase == "check_complete":
                Controller.click_element(self.commence)
                time.sleep(2)

            # Wait 1 sec before re-starting loop
            time.sleep(1)

        return False


if __name__ == '__main__':
    event_failsafe_instance = EventFailsafe()
    event_failsafe_instance.pass_event()
