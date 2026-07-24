from module.base.button import ButtonGrid
from module.coalition.assets import EMPTY_FLAGSHIP, EMPTY_VANGUARD
from module.coalition.coalition import Coalition
from module.coalition.combat import CoalitionCombat
from module.combat.assets import BATTLE_PREPARATION, BATTLE_STATUS_D, EXP_INFO_D, OPTS_INFO_D
from module.exception import CampaignEnd
from module.logger import logger
from module.retire.assets import DOCK_CHECK
from module.retire.dock import Dock
from module.retire.scanner import ShipScanner
from module.ui.assets import BACK_ARROW
from module.ui.navbar import Navbar


class CoalitionScuttleCombat(CoalitionCombat):
    triggered_normal_end = False

    def auto_search_combat_end(self):
        if self.appear(BATTLE_STATUS_D) or self.appear(EXP_INFO_D):
            self.device.screenshot_interval_set()
            return True
        return super().auto_search_combat_end()

    def handle_battle_status(self, drop=None):
        """
        Args:
            drop (DropImage):

        Returns:
            bool:
        """
        if self.is_combat_executing():
            return False
        if self.appear(BATTLE_STATUS_D, interval=self.battle_status_click_interval):
            if drop:
                drop.handle_add(self)
            else:
                self.device.sleep((0.25, 0.5))
            self.device.click(BATTLE_STATUS_D)
            return True
        if self.appear(OPTS_INFO_D, interval=self.battle_status_click_interval):
            if drop:
                drop.handle_add(self)
            else:
                self.device.sleep((0.25, 0.5))
            self.device.click(OPTS_INFO_D)
            return True
        if super().handle_battle_status(drop=drop):
            if self.battle_count >= self._scuttle_battle_total - 1:
                logger.warning("Triggered normal end")
                self.triggered_normal_end = True
            return True

        return False

    def handle_exp_info(self):
        """
        Returns:
            bool:
        """
        if self.is_combat_executing():
            return False
        if self.appear_then_click(EXP_INFO_D):
            self.device.sleep((0.25, 0.5))
            return True
        if super().handle_exp_info():
            return True

        return False

    def handle_combat_weapon_release(self):
        return False


class CoalitionScuttleRun(Coalition, CoalitionScuttleCombat, Dock):
    @property
    def _coalition_fleet_navbar(self):
        grids = ButtonGrid(
            origin=(63, 148),
            delta=(141.5, 0),
            button_shape=(110, 36),
            grid_shape=(self._scuttle_battle_total + 1, 1),
            name='COALITION_FLEET_NAVBAR_GRID',
        )
        return Navbar(grids=grids, active_color=(180, 180, 180), active_count=1500, name='COALITION_FLEET_NAVBAR')

    @property
    def manual_mode(self):
        return self.config.Fleet_Fleet1Mode

    @property
    def change_vanguard(self):
        return 'vanguard' in self.config.CoalitionScuttle_Sacrifice

    @property
    def change_flagship(self):
        return 'flagship' in self.config.CoalitionScuttle_Sacrifice

    def triggered_stop_condition(self, pt_check=False, oil_check=False, coin_check=False):
        if self.triggered_normal_end:
            return True
        return super().triggered_stop_condition(pt_check=pt_check, oil_check=oil_check)

    def coalition_combat(self):
        """
        Run prerequisite battles in auto mode and switch to the configured
        manual mode for the last battle only.

        Pages:
            in: is_coalition
            out: is_coalition
        """
        self.battle_count = 0
        battle_total = self._scuttle_battle_total
        manual_mode = self.manual_mode
        self.combat_preparation(emotion_reduce=False, auto='combat_auto')

        try:
            while 1:
                logger.hr(f'{self.FUNCTION_NAME_BASE}{self.battle_count}', level=2)
                final_battle = self.battle_count >= battle_total - 1
                self.config.override(
                    Fleet_Fleet1Mode=manual_mode if final_battle else 'combat_auto'
                )
                logger.attr('CombatMode', self.config.Fleet_Fleet1Mode)
                self.auto_search_combat_execute(
                    emotion_reduce=self.battle_count == 0,
                    fleet_index=1,
                )
                self.coalition_combat_re_enter()
                self.battle_count += 1
        except CampaignEnd:
            logger.info('Coalition combat end.')

    def coalition_enter_fleet_preparation(self, event, stage, fleet):
        """
        Enter a coalition map, then return from battle preparation to the
        coalition-specific fleet preparation screen.

        Pages:
            in: in_coalition
            out: coalition-specific fleet preparation
        """
        self.enter_map(event=event, stage=stage, mode=fleet)
        fleet_preparation = self.coalition_get_fleet_preparation(event)
        for _ in self.loop():
            if self.appear(fleet_preparation, offset=(20, 50)):
                break
            if self.appear(BATTLE_PREPARATION, offset=(20, 20), interval=3):
                self.device.click(BACK_ARROW)
                continue

    def get_common_rarity_ship(self, index='all'):
        self.dock_favourite_set(False, wait_loading=False)
        self.dock_sort_method_dsc_set(False, wait_loading=False)
        self.dock_filter_set(
            index=index, rarity='common', extra='enhanceable', sort='total'
        )

        logger.hr('FINDING SHIP')

        scanner = ShipScanner(level=(1, 31), fleet=0, status='free')
        scanner.disable('rarity')

        return scanner.scan(self.device.image)

    def _coalition_ship_change(self, button, index):
        fleet_preparation = self.coalition_get_fleet_preparation(self._scuttle_event)
        for _ in self.loop():
            if self.appear(DOCK_CHECK, offset=(20, 20)):
                break
            if self.appear(fleet_preparation, offset=(20, 50)):
                self.device.click(button)
                continue

        ship = self.get_common_rarity_ship(index=index)
        if ship:
            ship = min(ship, key=lambda s: (s.level, -s.emotion))
            self.dock_select_one(ship.button)
            self.dock_reset()
            self.dock_select_confirm(check_button=fleet_preparation)
            return True

        self.dock_reset()
        self.ui_back(check_button=fleet_preparation)
        return False

    def vanguard_change(self):
        logger.hr('Change vanguard', level=2)
        if self._coalition_ship_change(EMPTY_VANGUARD, index='vanguard'):
            logger.info('Change vanguard success')
            return True
        logger.info('Change vanguard failed, no vanguard in common rarity.')
        return False

    def flagship_change(self):
        logger.hr('Change flagship', level=2)
        if self._coalition_ship_change(EMPTY_FLAGSHIP, index='main'):
            logger.info('Change flagship success')
            return True
        logger.info('Change flagship failed, no flagship in common rarity.')
        return False

    def run(self, event='', mode='', fleet='', total=0):
        event = event if event else self.config.Campaign_Event
        mode = mode if mode else self.config.Coalition_Mode
        fleet = fleet if fleet else self.config.Coalition_Fleet
        event, mode = self.handle_stage_name(event, mode)
        self._scuttle_event = event
        self._scuttle_battle_total = self.coalition_get_battles(event, mode)

        while 1:
            super().run(event=event, mode=mode, fleet=fleet, total=total)

            if not self.triggered_normal_end:
                break

            self.coalition_enter_fleet_preparation(event, mode, fleet)
            self._coalition_fleet_navbar.set(main=self, right=2)
            success = True
            if self.change_vanguard:
                success = self.vanguard_change()
            if self.change_flagship:
                success = success and self.flagship_change()

            self.coalition_map_exit(event)
            self.triggered_normal_end = False

            if self.config.task_switched():
                self.config.task_stop()
            elif not success:
                self.config.task_delay(minute=30)
                self.config.task_stop()
