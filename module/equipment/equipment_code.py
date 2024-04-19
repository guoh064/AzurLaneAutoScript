import re
import yaml

from module.config.config import AzurLaneConfig
from module.equipment.assets import *
from module.logger import logger
from module.storage.assets import EQUIPMENT_FULL
from module.storage.storage import StorageHandler


BASE64_REGEX = re.compile('^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')


def is_equip_code(string):
    if string is None:
        return True
    if not isinstance(string, str):
        return False
    return BASE64_REGEX.match(string)


class EquipmentCode:
    config: AzurLaneConfig
    config_key: str
    coded_ships: list
    
    def __setattr__(self, key, value):
        if key in ['config', 'config_key', 'coded_ships']:
            super().__setattr__(key, value)
        elif key in self.coded_ships:
            if is_equip_code(value):
                super().__setattr__(key, value)
            else:
                logger.error(f'{value} is not a gear code, skip setting {key}')
        else:
            logger.error(f'{key} is not in coded ships: {self.coded_ships}')

    def __init__(self, config, key, ships):
        """
        Args:
            config (AzurLaneConfig):
            key: location of config containing gear code configs
            ships (list of string): ships whose gear codes should be memorized
        """
        self.config = config
        self.config_key = key
        self.coded_ships = ships
        _config = config.cross_get(keys=key)
        # print(_config)
        codes = dict([(ship, None) for ship in self.coded_ships])
        for line in _config.splitlines():
            try:
                codes.update(yaml.safe_load(line))
            except Exception as e:
                logger.error(f'Failed to parse current line of the config: "{line}", skipping')
        # print(codes)
        for ship in self.coded_ships:
            code: str = codes.pop(ship, None)
            self.__setattr__(ship, code)

    def export_to_config(self):
        """
        Export current ships' gear codes to location {self.config_key} of {self.config}.
        """
        _config = {}
        for ship in self.coded_ships:
            _config.update({ship: self.__getattribute__(ship)})
        value = yaml.safe_dump(_config)
        # print(value)
        self.config.cross_set(keys=self.config_key, value=value)


class EquipmentCodeHandler(StorageHandler):
    codes: EquipmentCode

    def __init__(self, config, key, ships, device=None, task=None):
        super().__init__(config, device=device, task=task)
        self.codes = EquipmentCode(self.config, key=key, ships=ships)

    def enter_equip_code_page(self, skip_first_screenshot=True):
        """
        Pages:
            in: ship_detail
            out: gear_code
        """
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.appear(EQUIPMENT_CODE_PAGE_CHECK):
                break

            if self.appear_then_click(EQUIPMENT_CODE_ENTRANCE):
                continue

    # def exit_equip_code_page(self):
    #     """
    #     Pages:
    #         in: gear_code
    #         out: ship_detail
    #     """
    #     self.ui_back(check_button=EQUIPMENT_CODE_ENTRANCE)

    def current_ship(self):
        # Will be overridden in subclasses.
        pass

    def export_equip_code(self, ship=None, skip_first_screenshot=True):
        """
        Export current ship's gear code to config file.
        This is done by first using "export" button 
        to export gear code to clipboard,
        then update the config file using yaml.safe_dump().
        """
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.info_bar_count():
                break

            if self.appear_then_click(EQUIPMENT_CODE_EXPORT, interval=1):
                continue
        
        code = self.device.clipboard
        if not ship in self.codes.coded_ships:
            ship = self.current_ship()
        self.codes.__setattr__(ship, code)
        self.codes.export_to_config()

    def equip_preview_empty(self):
        for index in range(6):
            if not self.appear(globals()['EQUIPMENT_CODE_EQUIP_{index}'.format(index=index)]):
                return False
        return True
    
    def clear_equip_preview(self, skip_first_screenshot=True):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.equip_preview_empty():
                break

            if self.appear_then_click(EQUIPMENT_CODE_CLEAR):
                continue

    def enter_equip_code_input_mode(self, skip_first_screenshot=True):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(EQUIPMENT_CODE_ENTER):
                self.device.click(EQUIPMENT_CODE_TEXTBOX)
                continue

            # End
            if not self.appear(EQUIPMENT_CODE_ENTER):
                break

    def confirm_equip_code(self, skip_first_screenshot=False):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear_then_click(EQUIPMENT_CODE_ENTER, interval=1):
                continue

            # End
            if not self.equip_preview_empty():
                break

    def confirm_equip_preview(self, skip_first_screenshot=True):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear_then_click(EQUIPMENT_CODE_CONFIRM, interval=5):
                continue

            if self.handle_popup_confirm('GEAR_CODE'):
                continue

            # End
            if self.appear(EQUIPMENT_CODE_ENTRANCE):
                return True
            if self.appear(EQUIPMENT_FULL, offset=(30, 30)):
                return False

    def clear_all_equip(self):
        self.enter_equip_code_page()
        ship = self.current_ship()
        if self.codes.__getattribute__(ship) is None:
            self.export_equip_code(ship)
        self.clear_equip_preview()
        while 1:
            success = self.confirm_equip_preview()
            if success:
                break
            else:
                self.handle_storage_full()
                self.clear_equip_preview()

    def apply_equip_code(self, code=None):
        self.enter_equip_code_page()
        self.clear_equip_preview()
        if code is None:
            ship = self.current_ship()
            code = self.codes.__getattribute__(ship)
        while 1:
            self.enter_equip_code_input_mode()
            try:
                self.device.text_input_and_confirm(code, clear=True)
            except EnvironmentError as e:
                continue
            self.confirm_equip_code()
            success = self.confirm_equip_preview()
            if success:
                break
            else:
                self.handle_storage_full()
                self.clear_equip_preview()


if __name__=="__main__":
    config = AzurLaneConfig('alas')
    key = "GemsFarming.GemsFarming.EquipmentCode"
    ships = ['DD', 'bogue', 'hermes', 'langley', 'ranger']
    self = EquipmentCodeHandler(config, key=key, ships=ships)
    print(self.codes.hermes)
    # self.codes.export_to_config(config)
    # print(self.GemsFarming_EquipmentCode)