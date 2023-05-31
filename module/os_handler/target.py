from module.base.timer import Timer
from module.base.button import *
from module.combat.combat import Combat
from module.logger import logger
from module.ocr.ocr import Digit
from module.os_handler.assets import (
    OCR_TARGET_ZONE_ID, TARGET_ENTER, 
    TARGET_INFO_ALL, TARGET_INFO_ALL_CHECK, TARGET_INFO_UNFINISHED, TARGET_INFO_UNFINISHED_CHECK, 
    TARGET_NEXT_REWARD, TARGET_NEXT_ZONE, TARGET_PREVIOUS_REWARD, TARGET_PREVIOUS_ZONE, 
    TARGET_RECEIVE_ALL, TARGET_RECEIVE_SINGLE, TARGET_RED_DOT
)
from module.os_handler.target_data import DIC_OS_TARGET
from module.ui.ui import UI, page_os


ZONE_ID = Digit(OCR_TARGET_ZONE_ID, name='TARGET_ZONE_ID')

class OSTarget:
    def is_file(self, zone, index):
        return not isinstance(DIC_OS_TARGET[zone][index], bool)
    
    def is_safe(self, zone, index):
        return DIC_OS_TARGET[zone][index] == True

class OSTargetHandler(OSTarget, Combat, UI):
    def switch_to_unfinished(self):
        """
        Switch to unfinished zone list.
        """
        self.ui_click(TARGET_INFO_UNFINISHED, TARGET_INFO_UNFINISHED_CHECK, TARGET_INFO_UNFINISHED)

    def switch_to_all(self):
        """
        Swtich to all zone list.
        """
        self.ui_click(TARGET_INFO_ALL, TARGET_INFO_ALL_CHECK, TARGET_INFO_ALL)

    def _receive_reward_all(self, skip_first_screenshot=True):
        """
        Receive all target rewards if there are two or more.
        
        Returns:
            bool: if received
        """
        confirm_timer = Timer(1, count=3).start()
        received = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear_then_click(TARGET_RECEIVE_ALL, offset=(10, 10), interval=3):
                confirm_timer.reset()
                continue
            if self.handle_popup_confirm('RECEIVE_ALL'):
                confirm_timer.reset()
                continue
            if self.handle_get_items():
                received = True
                confirm_timer.reset()
                continue
                
            # End
            if self.image_color_count(TARGET_RECEIVE_ALL, color=(230, 187, 67), threshold=220, count=400):
                if confirm_timer.reached():
                    break

        return received
    
    def find_unreceived_zone(self, skip_first_screenshot=True):
        """
        Switch to zone with reward if only one needs to be collected.

        Returns:
            bool: if found
        """
        # Ensure at all zone list
        self.switch_to_all()  

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(TARGET_RECEIVE_SINGLE):
                return True
            
            if self.appear_then_click(TARGET_NEXT_REWARD, offset=(10, 10), interval=2):
                continue
            if self.appear_then_click(TARGET_PREVIOUS_REWARD, offset=(10, 10), interval=2):
                continue
            
            if not self.appear(TARGET_PREVIOUS_REWARD) and not self.appear(TARGET_NEXT_REWARD):
                return False
        
    def _receive_reward_single(self, skip_first_screenshot=True):
        """
        Receive single target reward.
        
        Returns:
            bool: if received
        """
        confirm_timer = Timer(1, count=3).start()
        received = False

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
            
            if self.handle_get_items():
                received = True
                confirm_timer.reset()
                continue
            if self.appear_then_click(TARGET_RECEIVE_SINGLE, offset=(10, 10), interval=3):
                confirm_timer.reset()
                continue

            # End
            if not self.image_color_count(TARGET_RECEIVE_SINGLE, color=(76, 117, 184), threshold=220, count=400):
                if confirm_timer.reached():
                    break
        
        return received

    def receive_reward(self):
        """
        Receive target rewards.
        
        Returns:
            bool: if received.
        """
        logger.hr('OS Achievement Reward Receive', level=2)
        self.device.screenshot()
        if self.appear(TARGET_RECEIVE_ALL):
            return self._receive_reward_all()
        elif self.find_unreceived_zone():
            return self._receive_reward_single()
        else:
            return False
    
    def _is_finished(self, area):
        return self.image_color_count(area, color=(255, 239, 156), threshold=221, count=100)
    
    def _star_grid(self):
        return ButtonGrid(
            origin=(665, 405),
            delta=(32, 41),
            button_shape=(32, 30),
            grid_shape=(1, 5)
        )
    
    def scan_current_zone(self):
        """
        Scan current zone information.
        
        Returns:
            zone_id: int
            finished: list(bool)
        """
        zone_id = ZONE_ID.ocr(self.device.image)
        finished = [self._is_finished(button.area) for button in self._star_grid().buttons]
        logger.info(f'Zone {zone_id} target progress: {str(finished)}')

    def find_unfinished_safe_star_zone(self, skip_first_screenshot=True):
        """
        Find a zone with unfinished safe star by searching through unfinished zone.
        
        Returns:
            found_zone(int): The zone id with unfinished safe star. If such zone does not exist, return 0.
        """
        self.switch_to_unfinished()
        
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            zone_id, finished = self.scan_current_zone()
            for index in range(1, 5):
                if not finished[index]:
                    if self.is_file(zone_id, index):
                        logger.info(f'No. {index+1} of Zone {zone_id} is a file target, skipped.')
                        continue
                    elif self.is_safe(zone_id, index):
                        logger.info(f'No. {index+1} of Zone {zone_id} is safe for MeowfficerFarming.')
                        return zone_id
                    else:
                        logger.info(f"No. {index+1} of Zone {zone_id} can only be done in danger zone, skipped.")
                        continue
            if self.appear_then_click(TARGET_NEXT_ZONE, offset=(10, 10), interval=3):
                # It is possible to click more than 15 times.
                self.device.click_record.pop()
                continue
            else:
                logger.info(f'All remaining stars can only be finished in danger zone.')
                return 0

    def run(self, receive=True, find=False):
        if receive and self.appear(TARGET_RED_DOT):
            logger.info('Found Target red dot, enter target reward page.')
            self.ui_click(TARGET_ENTER, TARGET_INFO_ALL_CHECK)
            received = self.receive_reward()
            self.ui_back(page_os.check_button)
            return received
        if find:
            self.ui_click(TARGET_ENTER, TARGET_INFO_ALL_CHECK)
            logger.info('Find possible safe zone for MeowfficerFarming.')
            zone = self.find_unfinished_safe_star_zone()
            self.ui_back(page_os.check_button)
            return zone
