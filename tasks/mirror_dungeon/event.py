"""
Module: event.py
Description: Hard coded module that handles events by prioritizing EGO Gift gains.
"""
import time
import os
from module.logger.logger import logger
from module.config.config import get_asset_path
from module.automation.controller import Controller


class Event:
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
        self.choice = get_asset_path("images/mirror_dungeon/event/choice_icon.png")
        self.result = get_asset_path("images/mirror_dungeon/event/result.png")
        self.gain = [
            get_asset_path("images/mirror_dungeon/event/to_gain_1.png"),
            get_asset_path("images/mirror_dungeon/event/to_gain_2.png"),
            get_asset_path("images/mirror_dungeon/event/maybe_gain.png"),
            get_asset_path("images/mirror_dungeon/event/gain.png"),
            get_asset_path("images/mirror_dungeon/event/unknown_gift.png")
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

    def confirm_gain(self):
        """
        Helper that confirms acquired EGO gifts with 2 scenario
        """
        # Wait 5 sec for exit animation transition
        time.sleep(5)
        # Scenario 1: Gained EGO gifts successfully
        if Controller.find_element(self.confirm_after_gain):
            Controller.click_with_retry(self.confirm_after_gain)
            logger.info("Gain EGO gift successfully!")
            return True
        # Scenario 2: Not gained
        else:
            logger.info("EGO gift not gained.")
            return True

    def click_skips(self, count, interval=0.5):
        """
        Helper that handles repetitive skip clicking.
        """
        for x in range(count):
            Controller.click_element(self.skip)
            time.sleep(interval)

    def get_current_gain_icon(self):
        """
        Helper that scans the current game client and returns the path of the first
        matching gain icon found. Returns None if nothing is found.
        """
        return next((path for path in self.gain if Controller.find_element(path)), None)

    def try_highest_odds(self):
        """
        Helper that handles odds check and clicks the highest odds to ensure EGO gifts gain
        """
        # Wait 2 sec for sinners' icon with odds pops out
        time.sleep(2)
        logger.info("Selecting highest odds...")
        # Check for highest odds and clicks it
        for odds_path in self.predicted_odds:
            if Controller.find_element(odds_path, bbox=self.bbox_odds):
                odds_name = os.path.splitext(os.path.basename(odds_path))[0]
                logger.info(f"Highest odds {odds_name} found, clicking...")
                Controller.click_with_retry(odds_path, bbox=self.bbox_odds)
                break
        # Waiting for commence button appear
        time.sleep(2)
        # Using for loop in case sometimes commence button pops up too slow, or it requires skipping event logs
        for i in range(5):
            if Controller.find_element(self.commence):
                Controller.click_with_retry(self.commence)
                break
            if i < 5:
                Controller.click_with_retry(self.skip)
                time.sleep(2)
        # Waiting for odds check's coins flipping ends
        time.sleep(5)
        # Skipping following logs, 8 is the most ideal count
        self.click_skips(8, 0.2)

    def pass_event(self):
        """
        Hard coded event logic tree to pass event

        Handles actions based on different scenario.
        Optimize efficiency compared to event_failsafe.py (State machine version).
        """
        event_state = any(Controller.find_element(path) for path in self.in_event_state)

        Controller.validate_environment()

        # Ensure we are in correct state by checking "skip", EGO gift icon, handle of event
        if not event_state:
            logger.warning("Not in event state.")
            return False
        else:
            logger.info("Icon detected, in event state, processing...")

        # Click skip 5 times to ensure skipping logs
        self.click_skips(5, 0.5)

        while True:
            Controller.validate_environment()

            if Controller.find_element(self.choice):
                # Gain icon might be changing, so we need to scan for current icon
                current_gain_path = self.get_current_gain_icon()

                if current_gain_path:
                    logger.info("Try proceeding advantages check or gain EGO gift directly.")
                    Controller.click_with_retry(current_gain_path)
                    time.sleep(2)
                    self.click_skips(5, 0.5)

                    # 2 scenario right after we enter event: 1. Result icon pops out
                    # if the event goes to result directly, it means we have an event
                    # that may gain EGO gifts directly or requiring interaction
                    if Controller.find_element(self.result):
                        logger.info("Result detected, checking for proceed or continue...")

                        # Check between proceed and continue up to 8 times(with clicking skip since
                        # they might both not exists without skipping enough logs)
                        for a in range(8):

                            # In this scenario, we gain EGO gift directly (Tattoo gift type of event)
                            if Controller.find_element(self.continue_btn):
                                logger.info("Continue button found, gain EGO gift directly.")
                                Controller.click_with_retry(self.continue_btn)
                                return self.confirm_gain()

                            # In this scenario, event requiring interaction, either odds check, gain or simply choosing
                            if Controller.find_element(self.proceed):
                                logger.info("Proceed button found, run check.")
                                Controller.click_with_retry(self.proceed)
                                time.sleep(2)
                                self.click_skips(5, 0.5)

                                # In this scenario, event requiring clicking gain or simply choosing
                                if Controller.find_element(self.choice):
                                    # Refresh the scan to get current icon
                                    current_gain_path = self.get_current_gain_icon()
                                    # Clicking gain
                                    if Controller.click_with_retry(current_gain_path):
                                        self.click_skips(5, 0.5)
                                        Controller.click_with_retry(self.continue_btn)
                                        time.sleep(2)
                                        return self.confirm_gain()

                                    # kqe(village robot) type of event, event flow: proceed->choice but no gain icon
                                    else:
                                        # Clicking with offsets because there is no gain icon in the choice bar
                                        # Following logic is the logic to gain the max costs and EGO gift
                                        Controller.click_element(self.choice, y_offset=130)
                                        time.sleep(2)
                                        self.click_skips(5, 0.5)
                                        Controller.click_element(self.proceed)
                                        time.sleep(2)
                                        self.click_skips(5, 0.5)
                                        Controller.click_element(self.choice, y_offset=290)
                                        time.sleep(2)
                                        self.click_skips(3, 0.5)
                                        Controller.click_with_retry(self.continue_btn)
                                        time.sleep(2)
                                        return self.confirm_gain()

                                # In this scenario, event requiring running an odds check
                                else:
                                    self.try_highest_odds()
                                    Controller.click_with_retry(self.continue_btn)
                                    time.sleep(2)
                                    self.click_skips(5, 0.5)
                                    # Blade Lineage type of event, after running first odds check, requiring interaction
                                    # and running second odds check
                                    if Controller.find_element(self.choice):
                                        # Refresh the scan
                                        current_gain_path = self.get_current_gain_icon()
                                        Controller.click_with_retry(current_gain_path)
                                        time.sleep(2)
                                        self.click_skips(5, 0.5)
                                        Controller.click_with_retry(self.proceed)

                                        self.try_highest_odds()

                                        # Skips logs until we find continue button
                                        for z in range(5):
                                            if Controller.find_element(self.continue_btn):
                                                logger.info("Continue.")
                                                Controller.click_element(self.continue_btn)
                                                time.sleep(2)
                                                return self.confirm_gain()
                                            if z < 5:
                                                Controller.click_element(self.skip)
                                                time.sleep(0.5)
                                    return self.confirm_gain()

                            else:
                                return False
                        # All other scenarios return false, so we can pass to failsafe version later
                        else:
                            logger.warning("Neither continue nor proceed found, might stuck.")
                            return False

                    # 2 scenario right after we enter event: 2. Choice icon pops out
                    elif Controller.find_element(self.choice):
                        # gain icon might be changing, so we need to re-scan for current one
                        # next() take an iterator and return first item it finds
                        current_gain_path = self.get_current_gain_icon()

                        # Choice scenario always asks for running odds check
                        if current_gain_path:
                            logger.info("Run check to gain EGO gift.")
                            Controller.click_element(current_gain_path)
                            time.sleep(2)

                            # Skip logs until proceed button is found
                            for b in range(5):
                                if Controller.find_element(self.proceed):
                                    logger.info("Proceeding...")
                                    Controller.click_element(self.proceed)
                                    break
                                if b < 5:
                                    Controller.click_element(self.skip)
                                    time.sleep(0.5)

                            self.try_highest_odds()

                            # Skip logs until continue button is found
                            for c in range(5):
                                if Controller.find_element(self.continue_btn):
                                    logger.info("continue")
                                    Controller.click_element(self.continue_btn)
                                    time.sleep(2)
                                    return self.confirm_gain()
                                if c < 5:
                                    Controller.click_element(self.skip)
                                    time.sleep(0.5)
                    else:
                        return False
                else:
                    return False
            # All other scenarios return false, so we can pass to failsafe version later
            else:
                return False


if __name__ == '__main__':
    event_instance = Event()
    event_instance.pass_event()
