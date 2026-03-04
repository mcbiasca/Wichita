"""Items, weapons, armor, and inventory for the Wichita RPG."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Item:
    name: str
    description: str
    price: int

    def use(self, target) -> str:
        return f"Nothing happens when you use the {self.name}."


@dataclass
class Consumable(Item):
    hp_restore: int = 0
    mp_restore: int = 0

    def use(self, target) -> str:
        messages = []
        if self.hp_restore > 0:
            healed = min(self.hp_restore, target.max_hp - target.hp)
            target.hp += healed
            messages.append(f"{target.name} recovers {healed} HP!")
        if self.mp_restore > 0:
            restored = min(self.mp_restore, target.max_mp - target.mp)
            target.mp += restored
            messages.append(f"{target.name} recovers {restored} MP!")
        return " ".join(messages) if messages else f"No effect on {target.name}."


@dataclass
class Weapon(Item):
    attack_bonus: int = 0
    weapon_type: str = "sword"

    def equip_message(self) -> str:
        return f"You equip the {self.name}. (+{self.attack_bonus} ATK)"


@dataclass
class Armor(Item):
    defense_bonus: int = 0

    def equip_message(self) -> str:
        return f"You equip the {self.name}. (+{self.defense_bonus} DEF)"


@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)
    gold: int = 0
    weapon: Optional[Weapon] = None
    armor: Optional[Armor] = None

    def add_item(self, item: Item) -> str:
        self.items.append(item)
        return f"Obtained: {item.name}!"

    def remove_item(self, item: Item) -> bool:
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def equip_weapon(self, weapon: Weapon) -> str:
        if weapon in self.items:
            self.items.remove(weapon)
            if self.weapon:
                self.items.append(self.weapon)
            self.weapon = weapon
            return weapon.equip_message()
        return "You don't have that weapon."

    def equip_armor(self, armor: Armor) -> str:
        if armor in self.items:
            self.items.remove(armor)
            if self.armor:
                self.items.append(self.armor)
            self.armor = armor
            return armor.equip_message()
        return "You don't have that armor."

    @property
    def attack_bonus(self) -> int:
        return self.weapon.attack_bonus if self.weapon else 0

    @property
    def defense_bonus(self) -> int:
        return self.armor.defense_bonus if self.armor else 0

    def list_items(self) -> List[Item]:
        return self.items


# Item definitions
HEALTH_POTION = lambda: Consumable("Health Potion", "Restores 30 HP.", 20, hp_restore=30)
ELIXIR = lambda: Consumable("Elixir", "Restores 60 HP and 20 MP.", 60, hp_restore=60, mp_restore=20)
MANA_POTION = lambda: Consumable("Mana Potion", "Restores 25 MP.", 25, mp_restore=25)
ANTIDOTE = lambda: Consumable("Antidote", "Cures poison.", 15)

RUSTY_SWORD = Weapon("Rusty Sword", "An old, worn blade.", 0, attack_bonus=5)
IRON_SWORD = lambda: Weapon("Iron Sword", "A reliable iron sword.", 80, attack_bonus=12)
SILVER_SWORD = lambda: Weapon("Silver Sword", "A finely crafted silver blade.", 200, attack_bonus=22)
OAK_STAFF = Weapon("Oak Staff", "A gnarled wooden staff.", 0, attack_bonus=4, weapon_type="staff")
IRON_STAFF = lambda: Weapon("Iron Staff", "A staff tipped with iron.", 70, attack_bonus=10, weapon_type="staff")
CRYSTAL_STAFF = lambda: Weapon("Crystal Staff", "A staff pulsing with magic.", 220, attack_bonus=20, weapon_type="staff")
DAGGER = Weapon("Dagger", "A small but quick blade.", 0, attack_bonus=4, weapon_type="dagger")
SHORT_SWORD = lambda: Weapon("Short Sword", "A nimble short sword.", 75, attack_bonus=11, weapon_type="dagger")
SHADOW_BLADE = lambda: Weapon("Shadow Blade", "A blade forged in darkness.", 210, attack_bonus=21, weapon_type="dagger")

CLOTH_ARMOR = Armor("Cloth Armor", "Basic cloth protection.", 0, defense_bonus=2)
LEATHER_ARMOR = lambda: Armor("Leather Armor", "Toughened leather armor.", 60, defense_bonus=8)
CHAIN_MAIL = lambda: Armor("Chain Mail", "Interlocked metal rings.", 160, defense_bonus=16)

SHOP_ITEMS = [
    HEALTH_POTION,
    MANA_POTION,
    ELIXIR,
    ANTIDOTE,
    IRON_SWORD,
    IRON_STAFF,
    SHORT_SWORD,
    LEATHER_ARMOR,
    CHAIN_MAIL,
    CRYSTAL_STAFF,
    SILVER_SWORD,
    SHADOW_BLADE,
]
