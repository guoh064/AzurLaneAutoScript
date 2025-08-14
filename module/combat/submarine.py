from module.base.timer import Timer
from module.combat.assets import *
from module.combat_ui.assets import *
from module.combat_ui.combat_ui import CombatUI, SUBMARINE_CALLED, SUBMARINE_READY
from module.logger import logger


class SubmarineCall(CombatUI):
    submarine_call_flag = False
    submarine_call_timer = Timer(5)
    submarine_call_click_timer = Timer(1)

    def submarine_call_reset(self):
        """
        Call this method after in battle_execute.
        """
        self.submarine_call_timer.reset()
        self.submarine_call_flag = False

    def handle_submarine_call(self, submarine='do_not_use'):
        """
        Returns:
            str: If call.
        """
        if self.submarine_call_flag:
            return False
        if submarine in ['do_not_use', 'hunt_only', 'hunt_and_boss']:
            self.submarine_call_flag = True
            return False
        if self.submarine_call_timer.reached():
            logger.info('Submarine call timer reached')
            self.submarine_call_flag = True
            return False

        pause_theme = self.get_current_pause_theme()
        if not pause_theme in ['Old']:
            logger.info(f'Submarine call not supported for theme {pause_theme}')
            return False
        else:
            if not self.appear(SUBMARINE_AVAILABLE_CHECK_1) or not self.appear(SUBMARINE_AVAILABLE_CHECK_2):
                return False

        if self.appear(SUBMARINE_CALLED[pause_theme]):
            logger.info('Submarine called')
            self.submarine_call_flag = True
            return False
        elif self.submarine_call_click_timer.reached():
            if not self.appear_then_click(SUBMARINE_READY[pause_theme]):
                logger.info('Incorrect submarine icon')
                self.device.click(SUBMARINE_READY[pause_theme])
            logger.info('Call submarine')
            self.submarine_call_click_timer.reset()
            return True
