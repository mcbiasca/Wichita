from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Optional

import pygame

import settings
from utils import vec2


@dataclass
class Item:
    item_id: str
    name: str
    kind: str
    stackable: bool
    max_stack: int
    damage: int = 0
    defense: int = 0
    hp_restore: int = 0
    mana_restore: int = 0
    icon_path: str = ""


@dataclass
class ItemStack:
    item: Item
    count: int

    def can_stack(self, other: Item) -> bool:
        return self.item.item_id == other.item_id and self.item.stackable

    def add(self, amount: int) -> int:
        space = self.item.max_stack - self.count
        added = min(space, amount)
        self.count += added
        return added


ITEM_DEFS: Dict[str, Item] = {
    "health_potion": Item(
        "health_potion",
        "Health Potion",
        "consumable",
        True,
        5,
        hp_restore=40,
        icon_path=settings.ITEM_ICON_HP_POTION,
    ),
    "mana_potion": Item(
        "mana_potion",
        "Mana Potion",
        "consumable",
        True,
        5,
        mana_restore=35,
        icon_path=settings.ITEM_ICON_MANA_POTION,
    ),
    "sword": Item(
        "sword",
        "Iron Sword",
        "weapon",
        False,
        1,
        damage=8,
        icon_path=settings.ITEM_ICON_SWORD,
    ),
    "armor": Item(
        "armor",
        "Leather Armor",
        "armor",
        False,
        1,
        defense=4,
        icon_path=settings.ITEM_ICON_ARMOR,
    ),
    "apple": Item(
        "apple",
        "Apple",
        "consumable",
        True,
        10,
        hp_restore=30,
        icon_path=settings.ITEM_ICON_APPLE,
    ),
}


class Inventory:
    def __init__(self, cols: int, rows: int) -> None:
        self.cols = cols
        self.rows = rows
        self.slots: list[Optional[ItemStack]] = [None] * (cols * rows)

    def add_item(self, item: Item, amount: int = 1) -> int:
        remaining = amount
        if item.stackable:
            for stack in self.slots:
                if stack and stack.can_stack(item):
                    added = stack.add(remaining)
                    remaining -= added
                    if remaining <= 0:
                        return 0
        for index, slot in enumerate(self.slots):
            if slot is None:
                to_add = min(item.max_stack, remaining)
                self.slots[index] = ItemStack(item, to_add)
                remaining -= to_add
                if remaining <= 0:
                    return 0
        return remaining

    def remove_item(self, item_id: str, amount: int = 1) -> bool:
        remaining = amount
        for index, slot in enumerate(self.slots):
            if slot and slot.item.item_id == item_id:
                take = min(slot.count, remaining)
                slot.count -= take
                remaining -= take
                if slot.count <= 0:
                    self.slots[index] = None
                if remaining <= 0:
                    return True
        return False

    def find_first(self, item_id: str) -> Optional[int]:
        for index, slot in enumerate(self.slots):
            if slot and slot.item.item_id == item_id:
                return index
        return None

    def to_dict(self) -> list[Optional[dict]]:
        data: list[Optional[dict]] = []
        for slot in self.slots:
            if slot is None:
                data.append(None)
            else:
                data.append({"item_id": slot.item.item_id, "count": slot.count})
        return data

    def from_dict(self, data: list[Optional[dict]]) -> None:
        self.slots = [None] * (self.cols * self.rows)
        for index, entry in enumerate(data):
            if entry is None:
                continue
            item = ITEM_DEFS.get(entry.get("item_id"))
            if not item:
                continue
            self.slots[index] = ItemStack(item, int(entry.get("count", 1)))


@dataclass
class Equipment:
    weapon: Optional[Item] = None
    armor: Optional[Item] = None

    def to_dict(self) -> dict:
        return {
            "weapon": self.weapon.item_id if self.weapon else None,
            "armor": self.armor.item_id if self.armor else None,
        }

    def from_dict(self, data: dict) -> None:
        weapon_id = data.get("weapon")
        armor_id = data.get("armor")
        self.weapon = ITEM_DEFS.get(weapon_id) if weapon_id else None
        self.armor = ITEM_DEFS.get(armor_id) if armor_id else None


class Pickup(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        asset_manager,
        item: Optional[Item] = None,
        gold: int = 0,
        ammo: int = 0,
        icon_size: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.item = item
        self.gold = gold
        self.ammo = ammo
        self.base_pos = vec2(pos)
        self.bob_time = 0.0
        
        if icon_size is None:
            icon_size = settings.INV_SLOT_SIZE

        if self.ammo > 0:
            self.image = asset_manager.load_icon(settings.UI_ICON_GIFT, icon_size)
        elif item is not None:
            self.image = asset_manager.load_icon(item.icon_path, icon_size)
        else:
            self.image = asset_manager.load_icon(settings.UI_ICON_GOLD, icon_size)

        self.rect = self.image.get_rect(center=self.base_pos)

    def update(self, dt: float) -> None:
        self.bob_time += dt
        offset = 4 * math.sin(self.bob_time * 3)
        self.rect.center = (self.base_pos.x, self.base_pos.y - offset)

    def set_position(self, pos: tuple[float, float]) -> None:
        self.base_pos = vec2(pos)
        self.rect.center = self.base_pos


def get_item(item_id: str) -> Optional[Item]:
    return ITEM_DEFS.get(item_id)
