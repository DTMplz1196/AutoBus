"""
Module: main.py
Description: The Master Controller for AutoBus.
Combines the entry pipeline and the dungeon run logic for a 100% automated loop.
"""
import ctypes
import os
import threading
import time
from module.automation.controller import Controller
from module.config.config import config_manager
from module.logger.logger import logger
from tasks.mirror_dungeon.dungeon_run_manager import run_dungeon
from tasks.mirror_dungeon.dungeon_entry_manager import to_dungeon


def kill_switch():
    """
    Helper function that set a kill switch so user can terminate dungeon run
    """
    while True:
        # GetAsyncKeyState checks the global state of the key
        # 0x51 is the Virtual Key Code for 'Q'
        if ctypes.windll.user32.GetAsyncKeyState(0x51) & 0x8000:
            logger.info("User terminated dungeon run by pressing q")
            os._exit(0)  # noqa, ignores the warning
        # Prevent 100% CPU usage
        time.sleep(0.1)


def start_automation():
    """
    Executes and loops the full flow: Entry Pipeline -> Dungeon Run -> Result.
    Retrieve 'target_runs' from the user configuration.
    """
    # Start kill switch thread
    threading.Thread(target=kill_switch, daemon=True).start()

    # Check if we have team sets first
    if not config_manager.team_queue:
        logger.error("No teams found! Please set team first!")
        return False

    # Retrieve target runs from config, setting default to 1 if key doesn't exist
    target_runs = config_manager.global_settings.get("target_runs", 1)
    total_teams = len(config_manager.team_queue)

    for i in range(target_runs):
        # Cycler, if user only set 2 teams with 10 runs, the switch between this 2 teams repeatedly
        current_idx = i % total_teams

        # Update config_manager to the specific team for current run
        config_manager.set_active_task(current_idx)

        # Get the name for logging
        current_team_name = config_manager.settings.get("team_set_name", f"Team #{current_idx + 1}")

        logger.info(f"--- Starting Dungeon Run {i + 1}/{target_runs} ---")
        logger.info(f"Team: {current_team_name}")
        logger.info("Charon: 'Up for an exciting ride! Vroom~ Vroom~'")

        try:
            # Enter dungeon manager
            to_dungeon()

            logger.info("Entering pipeline finished. Transitioning to Dungeon Run Manager...")

            # Dungeon run manager
            run_dungeon()

            logger.info(f"Successfully completed run {i + 1}!")

        except Exception as e:
            logger.error(f"Master Controller Error on run {i + 1}: {e}")
            break

    logger.info("All dungeon runs completed. Charon is hungary!")


if __name__ == '__main__':
    Controller.validate_environment()
    start_automation()
