from module.equipment.assets import *
from module.logger import logger
from module.ui.assets import BACK_ARROW
from module.ui.ui import UI

class EquipmentCode(UI):
    def enter_equipment_code_page(self, skip_first_screenshot=False):
        """
        Pages:
            in: ship_detail
            out: equipment_code
        """
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
            
            if self.appear_then_click(EQUIPMENT_CODE_ENTRANCE):
                continue
            
            # End
            if self.appear(EQUIPMENT_CODE_PAGE_CHECK):
                break

    def exit_equipment_code_page(self):
        """
        Pages:
            in: equipment_code
            out: ship_detail
        """
        self.ui_back(check_button=EQUIPMENT_CODE_ENTRANCE)

    def export_equipment_code_to_clipboard(self, skip_first_screenshot=False):
        """
        Use "export" button to export current equipment code to clipboard.
        """
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
            
            # End
            if self.info_bar_count():
                break
            
            if self.appear_then_click(EQUIPMENT_CODE_EXPORT):
                continue

    def clear_all_equipments(self):
        self.appear_then_click(EQUIPMENT_CODE_CLEAR)

    # def enter_equipment_code_input_mode(self, skip_first_screenshot=True):
    #     count = 0
    #     while 1:
    #         if skip_first_screenshot:
    #             skip_first_screenshot = False
    #         else:
    #             self.device.screenshot()
    #         
    #         # End
    #         if not self.appear(EQUIPMENT_CODE_ENTER):
    #             break
    #         if count >= 3:
    #             logger.info("Tried 3 times, assuming cursor is at textbox.")
    #             break
    #             
    #         if self.appear(EQUIPMENT_CODE_ENTER):
    #             self.appear_then_click(EQUIPMENT_CODE_TEXTBOX)
    #             count += 1
    #             continue

    def import_equipment_code(self, text=None):
        """
        Use "adb shell input text" to type in equipment code.
        If text is None, use clipboard contents to fill in equipment code.
        """
        # deprecated
        # self.enter_equipment_code_input_mode()
        self.appear_then_click(EQUIPMENT_CODE_TEXTBOX, interval=3)
        if text:
            # use text input
            logger.info(f"Use equipment code from config: {text}")
            self.device.text_input(text)
        else:
            # use clipboard input
            logger.info("Use equipment code from clipboard")
            self.device.keyevent_input(279)
        self.device.keyevent_input(66)
        self.appear_then_click(EQUIPMENT_CODE_ENTER)
        
    def equipment_code_confirm(self, skip_first_screenshot=True):
        """
        Pages:
            in: equipment_code
            out: ship_detail
        """
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.appear(EQUIPMENT_CODE_ENTRANCE):
                break
    
            if self.handle_popup_confirm('EQUIPMENT_CODE'):
                continue
            
            if self.appear_then_click(EQUIPMENT_CODE_CONFIRM, interval=5):
                continue
