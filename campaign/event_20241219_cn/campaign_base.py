from campaign.event_20241024_cn.campaign_base import MODE_SWITCH_20240725
from module.campaign.assets import *
from module.campaign.campaign_base import CampaignBase as CampaignBase_
from module.campaign.campaign_ui import ModeSwitch
from module.logger import logger

CHAPTER_SWITCH_20241219 = ModeSwitch('Chapter_switch_20241219', is_selector=True, offset=(30, 30))
CHAPTER_SWITCH_20241219.add_state('ac', CHAPTER_20241024_AB)
CHAPTER_SWITCH_20241219.add_state('bd', CHAPTER_20241024_CD)
CHAPTER_SWITCH_20241219.add_state('sp', CHAPTER_20241024_SP)
CHAPTER_SWITCH_20241219.add_state('ex', CHAPTER_20241024_EX)


class CampaignBase(CampaignBase_):
    def campaign_set_chapter(self, name, mode='normal'):
        """
        Args:
            name (str): Campaign name, such as '7-2', 'd3', 'sp3'.
            mode (str): 'normal' or 'hard'.
        """
        chapter, stage = self._campaign_separate_name(name)
        logger.info([chapter, stage])

        if chapter in ['a', 'c']:
            self.ui_goto_event()
            MODE_SWITCH_20240725.set('combat', main=self)
            CHAPTER_SWITCH_20241219.set('ac', main=self)
            self.campaign_ensure_chapter(index=chapter)
        elif chapter in ['b', 'd']:
            self.ui_goto_event()
            MODE_SWITCH_20240725.set('combat', main=self)
            CHAPTER_SWITCH_20241219.set('bd', main=self)
            self.campaign_ensure_chapter(index=chapter)
        elif chapter in ['sp']:
            self.ui_goto_event()
            MODE_SWITCH_20240725.set('combat', main=self)
            CHAPTER_SWITCH_20241219.set('sp', main=self)
            self.campaign_ensure_chapter(index=chapter)
        elif chapter in ['ex']:
            self.ui_goto_event()
            MODE_SWITCH_20240725.set('combat', main=self)
            CHAPTER_SWITCH_20241219.set('ex', main=self)
            self.campaign_ensure_chapter(index=chapter)
        else:
            logger.warning(f'Unknown chapter {chapter}')