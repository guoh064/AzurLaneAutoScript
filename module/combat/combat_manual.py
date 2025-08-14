from module.combat.assets import *
from module.combat_ui.assets import *
from module.combat_ui.combat_ui import CombatUI, READY_AIR_RAID, READY_TORPEDO
from module.logger import logger


class CombatManual(CombatUI):
    auto_mode_checked = False
    auto_mode_switched = False
    manual_executed = False

    def combat_manual_reset(self):
        self.manual_executed = False

    def handle_combat_stand_still_in_the_middle(self, auto):
        """
        Args:
            auto (str): Combat auto mode.

        Returns:
            bool: If executed
        """
        if auto != 'stand_still_in_the_middle':
            return False
        # When switching from auto to manual, fleets are usually in the middle, no need to move down
        # Otherwise fleet will be moved to the bottom
        if self.auto_mode_switched:
            return False

        self.device.long_click(MOVE_DOWN, duration=0.8)
        return True

    def handle_combat_stand_still_bottom_left(self, auto):
        """
        Args:
            auto (str): Combat auto mode.

        Returns:
            bool: If executed
        """
        if auto != 'hide_in_bottom_left':
            return False

        self.device.long_click(MOVE_LEFT_DOWN, duration=(3.5, 5.5))
        return True

    def handle_combat_weapon_release(self):
        pause_theme = self.get_current_pause_theme()
        if not pause_theme in ['Old']:
            logger.info(f'Manual Combat not supported for theme {pause_theme}')
            return False

        if self.appear_then_click(READY_AIR_RAID[pause_theme], interval=10):
            return True
        if self.appear_then_click(READY_TORPEDO[pause_theme], interval=10):
            return True

        return False

    def handle_combat_manual(self, auto):
        """
        Args:
            auto (str): Combat auto mode.

        Returns:
            bool: If executed
        """
        if self.manual_executed or not self.auto_mode_checked:
            return False

        if self.handle_combat_stand_still_in_the_middle(auto):
            self.manual_executed = True
            return True
        if self.handle_combat_stand_still_bottom_left(auto):
            self.manual_executed = True
            return True

        return False
