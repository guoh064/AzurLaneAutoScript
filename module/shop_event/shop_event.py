from module.logger import logger
from module.shop_event.clerk import EventShopClerk
from module.shop_event.selector import EventShopSelector


class EventShop(EventShopClerk, EventShopSelector):
    """
    Class for Event Shop operations with blind methods.
    """
    pt_preserve = 0

    def ur_ship_costs(ships, buy=0):
        total_price = sum([ship.price for ship in ships])
        if buy == 1:
            if total_price == 500:
                total_price = 200
            elif total_price != 0:
                total_price = 0
        elif buy == 0:
            total_price = 0
        return total_price

    def cal_pt_ur_should_buy(self, ships, pt_ur_stock=0):
        total_price = self.ur_ship_costs(ships, buy=self.config.EventShop_BuyShipUR)
        if self.event_remain_days > 0:
            logger.info(f"Current UR pt: {self._pt_ur}, UR pt stock: {pt_ur_stock}, Total price: {total_price}")
            return min(max(total_price - self._pt_ur, 0), pt_ur_stock)
        
        pt_ur_can_obtain = pt_ur_stock + self._pt_ur
        buy_plan = self.config.EventShop_BuyShipUR
        while buy_plan >= 0:
            if pt_ur_can_obtain >= total_price:
                return max(total_price - self._pt_ur, 0)
            else:
                logger.warning("Current UR pt cannot buy all wanted items.")
                logger.info(f"Current UR pt: {self._pt_ur}, UR pt stock: {pt_ur_stock}, Total price: {total_price}")
                logger.info("Try buying fewer things.")
                buy_plan -= 1
                total_price = self.ur_ship_costs(ships, buy=buy_plan)
        return 0        

    def should_buy_ship_ur(self, ships):
        if self.event_remain_days > 0 or ships == []:
            return False
        else:
            return self.config.EventShop_BuyShipUR > 0 and len(ships) == 2

    def handle_buy_items_with_pt_ur(self, items):
        """
        Handle UR ship buying.
        Will postpone UR ship buying before event ends,
        and preserve necessary Pts for UR ship.
        Will buy UR pts and UR ships after event ends,
        and also postpone buying UR Coins to the last.

        Returns:
            list[EventShopItem]: items with UR ships deleted, and UR pt/coin items added to the end if necessary.
        """
        if not self.event_shop_has_pt_ur:
            return items
        
        ships = self.items_get_items(items, name="ShipUR", cost="URPt")
        pt_ur_item = self.items_get_items(items, name="PtUR", cost="Pt")
        coin_ur_item = self.items_get_items(items, name="Coin", cost="URPt")

        _items = []
        for item in items:
            if not (item in ships or item in pt_ur_item or item in coin_ur_item):
                _items.append(item)

        if pt_ur_item == []:
            pt_ur_stock = 0
            pt_ur_should_buy = 0
        else:
            pt_ur_item = pt_ur_item[0]
            pt_ur_stock = pt_ur_item.count
            pt_ur_should_buy = self.cal_pt_ur_should_buy(ships, pt_ur_stock)

        if pt_ur_should_buy > 0:
            if self.event_remain_days > 0:
                self.pt_preserve += pt_ur_should_buy * pt_ur_item.price
            else:
                self.event_shop_buy(pt_ur_item, amount=pt_ur_should_buy)
            pt_ur_stock -= pt_ur_should_buy
            pt_ur_item.count = pt_ur_stock
            self._pt_ur = self.event_shop_get_pt_ur()

        if self.should_buy_ship_ur(ships):
            for idx in range(self.config.EventShop_BuyShipUR):
                self.event_shop_buy(ship[idx])
                self._pt_ur = self.event_shop_get_pt_ur()

        # If event ends and there is extra UR pt, add UR coin buys to last.        
        if coin_ur_item != [] and self.event_remain_days <= 0:
            coin_ur_item = coin_ur_item[0]
            if pt_ur_stock > 0:
                _items.append(pt_ur_item)
            _items.append(coin_ur_item)

        return _items    

    def should_unlock_ship_ssr(self, ship):
        if ship == []:
            return False
        else:
            return ship[0].tag == "unobtained" and self.config.EventShop_UnlockShipSSR

    def handle_buy_ship_ssr_unlock(self, items):
        """
        Will delete all ssr ship items if not unlocking any in the setting.
        """
        ships = self.items_get_items(items, name="ShipSSR")

        if ships == []:
            return items
        
        _items = []
        for item in items:
            if not item.name in ["ShipSSR"]:
                _items.append(item)

        if not self.config.EventShop_UnlockShipSSR:
            return _items
            
        parse_ships = [ship for ship in ships if ship.tag == "unobtained"]
        if self.event_remain_days > 0:
            self.pt_preserve += sum([ship.price for ship in parse_ships])
        else:
            for ship in parse_ships:
                self.event_shop_buy(ship)
                self._pt = self.event_shop_get_pt()
                ship.count -= 1
                if ship.count > 0:
                    _items = [ship] + _items
        
        return _items

    def run(self):
        """
        Pages:
            in: shop_event
        """
        if not self.config.EventShop_Enable:
            return False
        self.event_shop_load_ensure()
        self.record_event_shop_cost()
        items = self.scan_all()
        if not len(items):
            logger.warning('Empty Event shop.')
            return False
        logger.hr("Event Shop buy", level=2)
        self._pt = self.event_shop_get_pt()
        if self.event_shop_has_pt_ur:
            self._pt_ur = self.event_shop_get_pt_ur()
        logger.attr("Event_remain_days", self.event_remain_days)
        items = self.handle_buy_items_with_pt_ur(items)
        items = self.handle_buy_ship_ssr_unlock(items)
        if len(items) and items[-1].cost == "URPt":
            if len(items) >= 2 and items[-2].name == "PtUR":
                items = self.items_filter_in_event_shop(items[:-2]) + items[-2:]
            else:
                items = self.items_filter_in_event_shop(items[:-1]) + items[-1:]
        else:
            items = self.items_filter_in_event_shop(items)
        if not len(items):
            logger.warning('Nothing to buy.')
        self._pt = self.event_shop_get_pt()
        logger.attr("Pt_preserve", self.pt_preserve)
        skip_get_pts = True
        items.reverse()
        while len(items):
            item = items.pop()
            if not skip_get_pts:
                self._pt = self.event_shop_get_pt()
            if item.cost == "Pt" and item.price + self.pt_preserve > self._pt\
                    or item.cost == "URPt" and item.price > self._pt_ur:
                if self.event_remain_days > 0:
                    logger.info(f"Pt: {self._pt}, Pt preserve: {self.pt_preserve}, price: {item.price}")
                    logger.info(f'Not enough pts to buy item: {item.name}, stop.')
                    break
                else:
                    logger.info(f"URPt: {self._pt_ur}, price: {item.price}")
                    logger.info(f'Not enough pts to buy item: {item.name}, skip.')
                    continue
            skip_get_pts = not self.event_shop_buy(item)
        return True