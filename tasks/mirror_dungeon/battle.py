"""
Module: battle.py
Description: Automates battle using "win rate" and "damage" according to scenario.
"""
import time
import pyautogui
from module.logger.logger import logger
from module.config.config import get_asset_path
from module.automation.controller import Controller


class Battle:
    def __init__(self):
        self.battle_end = [get_asset_path(f"images/battle/battle_end_{i}.png") for i in range(1, 6)]
        self.standby_phases = [get_asset_path(f"images/battle/standby_phase_{i}.png") for i in range(1, 3)]
        self.moving_phases = [get_asset_path(f"images/battle/moving_phase_{i}.png") for i in range(1, 5)]
        self.both_phase = get_asset_path("images/battle/setting.png")
        self.win_rate = get_asset_path("images/battle/win_rate.png")
        self.damage = get_asset_path("images/battle/damage.png")
        self.start_activate = get_asset_path("images/battle/start_activate.png")
        self.broken_part = get_asset_path("images/battle/broken_part.png")
        self.ego_gift_get = get_asset_path("images/battle/ego_gift_get.png")
        self.confirm = get_asset_path("images/battle/confirm.png")
        self.skip = get_asset_path("images/mirror_dungeon/event/event_skip.png")
        self.bbox_setting = (1809, 56, 1903, 136)
        self.bbox_chain_area = (8, 966, 1909, 1076)

    def check_battle_state(self):
        """
        Check current phase of the battle, handles according to scenario.
        """
        # Check: Setting icon, exists consistently except EGO animation phase, but similar to setting icon in road state
        # Adding a bbox because other interface like road also have setting icon, but the location is different
        both_phase = Controller.find_element(self.both_phase, bbox=self.bbox_setting)

        # Check: Turn icon(consistent at standby_phase), golden bough(may vary at standby_phase)
        standby_phases = any(Controller.find_element(path) for path in self.standby_phases)

        # Check: Different parts of chain icons(exists at moving_phase, but varies during moving_phase)
        # Adding a bbox because chain icon parts only appear at the bottom of the game window, avoid mixing with others
        moving_phases = any(Controller.find_element(path, bbox=self.bbox_chain_area) for path in self.moving_phases)

        # Check: Bus icon(in dungeon road), select enter reward card(after fight), victory(dungeon run finishes)
        # acquire EGO gifts(gain gifts), EGO gift get(gained directly)
        battle_end_phase = any(Controller.find_element(path) for path in self.battle_end)

        # Sometimes there might be event requiring interation during battle
        event_phase = Controller.find_element(self.skip)

        Controller.validate_environment()
        # Order if so we check standby first then moving phase, battle end and EGO animation phase last since these
        # two phases are rare case, optimize efficiency
        if both_phase and standby_phases:
            logger.info("Battle state: Standby phase.")
            return "standby"

        if both_phase and moving_phases:
            logger.info(f"Battle state: Moving phase.")
            return "moving"

        if battle_end_phase:
            logger.info("Battle concluded, result state")
            return "Battle concluded"

        if event_phase:
            logger.info("Battle state: Event phase.")
            return "event"

        # Sometimes during EGO animation, all icons disappear and no consistent icon,
        # Loading phase after battle concluded can also result in this scenario
        if not both_phase and not standby_phases and not moving_phases and not event_phase:
            logger.info("Might in EGO animation phase or battle has concluded, loading...")
            return "EGO, loading"

        # Always return moving instead of None until result icon is found
        # in case some scenario where the logic is correct but
        # script ended, happened once when testing
        return "moving"

    def battle(self):
        """
        Main execution loop for battle encounters

        Handles actions based on state, default using win-rate, but use damage when broken parts are detected.
        """
        while True:
            Controller.validate_environment()
            state = self.check_battle_state()

            # Using click_with_retry to ensure clicking since there are many effects or battle text during battle
            if state == "standby":
                # Check if broken part exists, using damage if it exists, significantly optimize efficiency
                if Controller.find_element(self.broken_part):
                    logger.info("Broken part detected, centralizing fire power...")
                    Controller.click_with_retry(self.damage)
                    time.sleep(0.5)
                    Controller.click_with_retry(self.start_activate)
                # Check if win rate exits, click it and start_activate if it does
                elif Controller.find_element(self.win_rate):
                    Controller.click_with_retry(self.win_rate)
                    time.sleep(0.5)
                    Controller.click_with_retry(self.start_activate)
                    logger.info("Battling based on win rate...")
                # If template matching failed, simply use keyboard shortcuts for win-rate button
                else:
                    logger.info("Couldn't find win rate button, trying keyboard shortcuts (P + Enter)...")
                    pyautogui.press('p')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                logger.info("Actions taken, waiting for animation...")
                # Add waiting time, according to test, 20s is the most ideal interval, since attacking staggered enemy
                # is really fast and short
                time.sleep(20)

            # Since it's a state machine, and we have added 20s delay after actions taken, so we set only 5s delay
            # for moving phase and check state again, so it can optimize efficiency
            elif state == "moving":
                logger.info("Moving phases, waiting for animation...")
                time.sleep(5)
            # Add 25s to wait for EGO animation transition
            elif state == "EGO, loading":
                logger.info("Waiting for EGO animation or loading...")
                time.sleep(25)

            elif state == "Battle concluded":
                logger.info("Battle loop ended.")
                # Sometimes we gain EGO gift after battle, especially in event->battle scenario,
                # add a check to handle such scenario
                if Controller.find_element(self.ego_gift_get):
                    Controller.click_with_retry(self.confirm)
                    logger.info("Battle concluded and an EGO gift gained!")
                return True

            # Sometimes there might be event requiring interation during battle, return True to end battle module
            elif state == "event":
                logger.info("Event phase, exiting battle module to event module...")
                return True


if __name__ == '__main__':
    battle_instance = Battle()
    battle_instance.battle()
