import numpy as np

from module.base.base import ModuleBase
from module.base.utils import get_color, color_similar
from module.combat_ui.assets import *

PAUSE_NAMES = [
    'Old', 
    'New', 
    'Iridescent_Fantasy', 
    'Christmas', 
    'Neon',
    'Cyber', 
    'HolyLight', 
    'Pharaoh', 
    'Nurse', 
    'Devil', 
    'Seaside', 
    'Star',
]

PAUSE = {name: globals()[f'PAUSE_{name}'] for name in PAUSE_NAMES}

QUIT = {
    name: globals().get(f'QUIT_{name}', QUIT_New) 
    for name in PAUSE_NAMES
}

SUBMARINE_READY = {
    name: globals().get(f'SUBMARINE_READY_{name}', SUBMARINE_READY_Old)
    for name in PAUSE_NAMES
}

SUBMARINE_CALLED = {
    name: globals().get(f'SUBMARINE_CALLED_{name}', SUBMARINE_CALLED_Old)
    for name in PAUSE_NAMES
}

READY_AIR_RAID = {
    name: globals().get(f'READY_AIR_RAID_{name}', READY_AIR_RAID_Old)
    for name in PAUSE_NAMES
}

READY_TORPEDO = {
    name: globals().get(f'READY_TORPEDO_{name}', READY_TORPEDO_Old)
    for name in PAUSE_NAMES
}


class CombatUI(ModuleBase):
    def get_current_pause_theme(self):
        """
        Returns:
            string: current pause theme
        """
        self.device.stuck_record_add(PAUSE_Old)
        if self.config.SERVER in ['cn', 'en']:
            if PAUSE_Old.match_luma(self.device.image, offset=(10, 10)):
                return 'Old'
        else:
            color = get_color(self.device.image, PAUSE_Old.area)
            if color_similar(color, PAUSE_Old.color) or color_similar(color, (238, 244, 248)):
                if np.max(self.image_crop(PAUSE_DOUBLE_CHECK, copy=False)) < 153:
                    return 'Old'
        if PAUSE_New.match_template_color(self.device.image, offset=(10, 10)):
            return 'New'
        if PAUSE_Iridescent_Fantasy.match_luma(self.device.image, offset=(10, 10)):
            return 'Iridescent_Fantasy'
        if PAUSE_Christmas.match_luma(self.device.image, offset=(10, 10)):
            return 'Christmas'
        # PAUSE_New, PAUSE_Cyber, PAUSE_Neon look similar, check colors
        if PAUSE_Neon.match_template_color(self.device.image, offset=(10, 10)):
            return 'Neon'
        if PAUSE_Cyber.match_template_color(self.device.image, offset=(10, 10)):
            return 'Cyber'
        if PAUSE_HolyLight.match_template_color(self.device.image, offset=(10, 10)):
            return 'HolyLight'
        # PAUSE_Pharaoh has random animation, assets should avoid the area in the middle and use match_luma
        if PAUSE_Pharaoh.match_luma(self.device.image, offset=(10, 10)):
            return 'Pharaoh'
        # PAUSE_Star may get detected as PAUSE_Nurse, should before it
        if PAUSE_Star.match_luma(self.device.image, offset=(10, 10)):
            return 'Star'
        if PAUSE_Nurse.match_luma(self.device.image, offset=(10, 10)):
            return 'Nurse'
        # PAUSE_Devil is in red
        if PAUSE_Devil.match_template_color(self.device.image, offset=(10, 10)):
            return 'Devil'
        # PAUSE_Seaside is in light blue
        if PAUSE_Seaside.match_template_color(self.device.image, offset=(10, 10)):
            return 'Seaside'
        return None
