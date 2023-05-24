from module.base.timer import Timer
from module.base.button import *
from module.combat.combat import Combat
from module.logger import logger
from module.ocr.ocr import Digit
from module.os_collection.achievement_data import LIST_OS_ACHIEVEMENT
from module.os_collection.archive_data import SAFE_ARCHIVE
from module.os_collection.assets import *
from module.ui.ui import UI


ZONE_ID = Digit(OCR_ZONE_ID, name='OCR_ZONE_ID')


class OSAchievement:
    def is_safe(self, zone, index):
        if LIST_OS_ACHIEVEMENT[zone][index] is None:
            return zone in SAFE_ARCHIVE
        else:
            return LIST_OS_ACHIEVEMENT[zone][index]


class OSAchievementHandler(OSAchievement, Combat, UI):
    def switch_to_unachieved(self):
        """
        Switch to zones with unachieved stars.
        """
        self.ui_click(INFO_UNFINISHED, INFO_UNFINISHED_CHECK, INFO_UNFINISHED)
        
    def switch_to_all(self):
        """
        Switch to all zones.
        """
        self.ui_click(INFO_ALL, INFO_ALL_CHECK, INFO_ALL)

    def _receive_reward_all(self, skip_first_screenshot=True):
        """
        Receive all achievement rewards if there are to or more.
        
        Returns:
            bools: if received
        """
        confirm_timer = Timer(1, count=3).start()
        received = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = True
            else:
                self.device.screenshot()
            
            if self.appear_then_click(RECEIVE_ALL, offset=(10, 10), interval=3):
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
            if self.image_color_count(RECEIVE_ALL, color=(230, 187, 67), threshold=220, count=400):
                if confirm_timer.reached():
                    break

        return received

    def find_unreceived_zone(self, skip_first_screenshot=True):
        """
        Toggle to zone with reward.
        """
        self.switch_to_all()  # ensure 
        found = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.appear(RECEIVE_SINGLE):
                found = True
                break
            if not self.appear(JUMP_RIGHT) and not self.appear(JUMP_LEFT):
                break
            

            if self.appear_then_click(JUMP_RIGHT):
                self.device.sleep(0.5)
                continue
            if self.appear_then_click(JUMP_LEFT):
                self.device.sleep(0.5)
                continue        
        return found

    def _receive_reward_single(self, skip_first_screenshot=True):
        """
        Receive single achievement reward if there is only one.
        
        Returns:
            bools: if received
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
            if self.appear_then_click(RECEIVE_SINGLE, offset=(10, 10), interval=3):
                confirm_timer.reset()
                continue
            
            # End
            if not self.image_color_count(RECEIVE_SINGLE, color=(76, 117, 184), threshold=220, count=400):
                if confirm_timer.reached():
                    break

        return received

    def receive_reward(self):
        """
        Receive achievement rewards.
        
        Returns:
            bool: if received.
        """
        logger.hr('OS Achievement Reward Receive', level=1)
        self.device.screenshot()
        received = False
        if self.appear(RECEIVE_ALL):
            received = self._receive_reward_all()
        elif self.find_unreceived_zone():
            received = self._receive_reward_single()
        
        return received
    
    def _is_finished(self, area):
        return self.image_color_count(area, color=(255, 239, 156), threshold=221, count=100)
        
    def _star_grid(self):
        return ButtonGrid(
            origin=(665, 405),
            delta=(32, 41),
            button_shape=(32, 30),
            grid_shape=(1, 5)
        )

    def find_unfinished_safe_star_zone(self, skip_first_screenshot=True):
        """
        Toggle to zone with unfinished safe star.

        Returns:
            found_zone(int): The zone_id with unfinished safe star
        """
        self.switch_to_unachieved()
        found_zone = None
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
           
            zone_id = ZONE_ID.ocr(self.device.image)
            finished = [self._is_finished(button.area) for button in self._star_grid().buttons]
            logger.info(f'Zone {zone_id}: {str(finished)}')
            for index in range(1, 5):  # The first area is control and is finished after os_explore, skip checking
                if not finished[index]:
                    logger.info(f'index: {index}, found_zone: {found_zone}')
                    if self.is_safe(zone_id, index):
                        logger.info(f'No. {index+1} of Zone {zone_id} is safe for MeowfficerFarming.')
                        found_zone = zone_id
                        break
            if found_zone is not None:
                break
            else:
                self.device.sleep(0.3)
                self.device.screenshot()
                if not self.appear(RIGHT_BUTTON):
                    logger.info(f'All remaining stars can only be finished at os_explore')
                    break
                else:
                    self.device.click(RIGHT_BUTTON)
                    continue
        
        return found_zone
            
    def run(self):
        """
        Main process, receiving rewards and finding next zone for MewofficerFarming.
        
        Returns: 
            zone(int): next zone to be set.
        """
        self.receive_reward()

        zone = self.find_unfinished_safe_star_zone()
        return zone
            