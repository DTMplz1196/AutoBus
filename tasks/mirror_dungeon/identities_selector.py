"""
Module: identities_selector.py
Description: Handles Sinners identities deployment and selection order using relative coordinate offsets.
"""
import time
from module.logger.logger import logger
from module.config.config import config_manager, get_asset_path
from module.automation.controller import Controller


class IdentitiesSelector:
    def __init__(self):
        self.in_identities_selection_state_1 = get_asset_path(
            "images/identity_select/in_identities_selection_state_1.png"
        )
        self.in_identities_selection_state_2 = get_asset_path(
            "images/identity_select/in_identities_selection_state_2.png"
        )
        self.chain_to_battle = get_asset_path("images/identity_select/chain_to_battle.png")
        self.not_deployed_msg = get_asset_path("images/identity_select/not_deployed_msg.png")
        self.not_deployed_confirm_btn = get_asset_path("images/identity_select/not_deployed_confirm_btn.png")
        self.base_coor = get_asset_path("images/identity_select/base_coor.png")
        self.clear_selection = get_asset_path("images/identity_select/clear_selection.png")
        self.clear_selection_msg = get_asset_path("images/identity_select/clear_selection_msg.png")
        self.clear_selection_confirm_btn = get_asset_path("images/identity_select/clear_selection_confirm_btn.png")

        # Sinner slots offsets (calculated based on "To battle!" button)
        self.sinner_offsets = {
            "sinner#1": (-1275, -525),
            "sinner#2": (-1075, -525),
            "sinner#3": (-875, -525),
            "sinner#4": (-675, -525),
            "sinner#5": (-475, -525),
            "sinner#6": (-275, -525),
            "sinner#7": (-1275, -225),
            "sinner#8": (-1075, -225),
            "sinner#9": (-875, -225),
            "sinner#10": (-675, -225),
            "sinner#11": (-475, -225),
            "sinner#12": (-275, -225)
        }

    def select_identity(self):
        """
        Main logic for deploying Sinners in user preferred order.
        """
        Controller.validate_environment()

        # ensure we are in identity selection state by checking "To battle" and "clear selection"
        if not Controller.find_element(self.in_identities_selection_state_1) \
                and not Controller.find_element(self.in_identities_selection_state_2):
            logger.warning("Not in identity selection state.")
            return False
        else:
            logger.info("In identity selection state, proceeding...")

        # Check if not_deployed button pops out
        if Controller.find_element(self.not_deployed_msg):
            logger.info("Haven't deployed any sinners, re-deploying")
            Controller.click_with_retry(self.not_deployed_confirm_btn)
            # wait 1 sec for msg window disappear
            time.sleep(1)

        # Check if clear selection msg pops out
        if Controller.find_element(self.clear_selection_msg):
            logger.info("Reset message detected, confirming...")
            Controller.click_element(self.clear_selection_confirm_btn)
            # wait 1 sec for msg window disappear
            time.sleep(1)

        # Clear selection everytime in identities selection to ensure teammates consistency
        Controller.click_with_retry(self.clear_selection)
        # wait 1 sec for msg window pops out
        time.sleep(1)
        Controller.click_with_retry(self.clear_selection_confirm_btn)
        logger.info("Clear selection and re-select to ensure consistency")
        # wait 1 sec for msg window disappear
        time.sleep(1)

        # Maps keys(sinner) to ordered list of user preference
        identity_preference = config_manager.settings.get("identity_preference", [])

        # Verify if anchor(To battle!) exists
        base_coor = Controller.find_element(self.base_coor)
        if not base_coor:
            logger.warning("Base coordinate (To Battle!) not found, you might in team checking state")
            return False

        for sinners in identity_preference:
            if sinners in self.sinner_offsets:
                ox, oy = self.sinner_offsets[sinners]
                logger.info(f"Selecting {sinners}")
                # Click sinners based on "To battle" icon
                Controller.click_element(self.base_coor, x_offset=ox, y_offset=oy)
                time.sleep(0.3)

        # Wait 2 sec for animation transitions
        time.sleep(2)
        start_btn = Controller.find_element(self.chain_to_battle)

        # 2. Only click if it was actually found
        if start_btn:
            return Controller.click_with_retry(self.chain_to_battle)
        else:
            # If not found, wait a second and try one more time before giving up
            logger.warning("To Battle button not found.")
            time.sleep(1.5)
            return Controller.click_with_retry(self.chain_to_battle)


if __name__ == '__main__':
    identities_selector_instance = IdentitiesSelector()
    identities_selector_instance.select_identity()
