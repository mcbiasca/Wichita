"""Character classes and enemy definitions for the Wichita RPG."""

import copy
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from src.items import Inventory, Weapon, Armor, RUSTY_SWORD, OAK_STAFF, DAGGER, CLOTH_ARMOR, HEALTH_POTION


# ---------------------------------------------------------------------------
# Spells
# ---------------------------------------------------------------------------

@dataclass
class Spell:
    name: str
    mp_cost: int
    base_damage: int
    description: str
    target_type: str = "enemy"  # "enemy" or "self"

    def apply(self, caster, target) -> str:
        if caster.mp < self.mp_cost:
            return f"Not enough MP to cast {self.name}!"
        caster.mp -= self.mp_cost
        if self.target_type == "enemy":
            dmg = self.base_damage + random.randint(0, caster.level * 3)
            target.hp = max(0, target.hp - dmg)
            return f"{caster.name} casts {self.name}! {target.name} takes {dmg} damage!"
        else:
            heal = self.base_damage + random.randint(0, caster.level * 2)
            caster.hp = min(caster.max_hp, caster.hp + heal)
            return f"{caster.name} casts {self.name}! Recovers {heal} HP!"


FIREBALL = Spell("Fireball", 8, 20, "A blazing ball of fire.", "enemy")
ICE_SHARD = Spell("Ice Shard", 6, 15, "A piercing shard of ice.", "enemy")
THUNDER = Spell("Thunder", 12, 35, "A bolt of lightning.", "enemy")
HEAL = Spell("Heal", 5, 20, "Restores HP.", "self")
BACKSTAB = Spell("Backstab", 4, 18, "Strike from the shadows.", "enemy")
POISON_STRIKE = Spell("Poison Strike", 6, 12, "A strike laced with poison.", "enemy")


CLASS_SPELLS: Dict[str, List[Spell]] = {
    "Warrior": [],
    "Mage": [FIREBALL, ICE_SHARD, THUNDER, HEAL],
    "Rogue": [BACKSTAB, POISON_STRIKE],
}

CLASS_STARTING_WEAPON = {
    "Warrior": RUSTY_SWORD,
    "Mage": OAK_STAFF,
    "Rogue": DAGGER,
}

CLASS_BASE_STATS = {
    "Warrior": {"max_hp": 80, "max_mp": 10, "attack": 14, "defense": 8, "speed": 6},
    "Mage":    {"max_hp": 45, "max_mp": 50, "attack": 6,  "defense": 4, "speed": 7},
    "Rogue":   {"max_hp": 60, "max_mp": 25, "attack": 11, "defense": 5, "speed": 12},
}

LEVEL_UP_STATS = {
    "Warrior": {"max_hp": 15, "max_mp": 2,  "attack": 3, "defense": 2, "speed": 1},
    "Mage":    {"max_hp": 8,  "max_mp": 10, "attack": 2, "defense": 1, "speed": 1},
    "Rogue":   {"max_hp": 10, "max_mp": 4,  "attack": 3, "defense": 1, "speed": 2},
}

EXP_TO_LEVEL = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200]


# ---------------------------------------------------------------------------
# Base character
# ---------------------------------------------------------------------------

class Character:
    def __init__(self, name: str, max_hp: int, max_mp: int, attack: int, defense: int, speed: int):
        self.name = name
        self.max_hp = max_hp
        self.max_mp = max_mp
        self.hp = max_hp
        self.mp = max_mp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.level = 1

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        reduction = max(0, self.defense - random.randint(0, 3))
        actual = max(1, damage - reduction)
        self.hp = max(0, self.hp - actual)
        return actual

    def basic_attack(self, target: "Character") -> str:
        dmg = self.attack + random.randint(-2, 4)
        actual = target.take_damage(dmg)
        return f"{self.name} attacks {target.name} for {actual} damage!"


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player(Character):
    def __init__(self, name: str, char_class: str):
        stats = CLASS_BASE_STATS[char_class]
        super().__init__(name, **stats)
        self.char_class = char_class
        self.exp = 0
        self.inventory = Inventory(gold=50)
        self.spells: List[Spell] = list(CLASS_SPELLS[char_class])
        # Equip fresh copies of starting gear so each player has independent items
        self.inventory.weapon = copy.copy(CLASS_STARTING_WEAPON[char_class])
        self.inventory.armor = copy.copy(CLOTH_ARMOR)
        # Give a starting potion
        self.inventory.add_item(HEALTH_POTION())

    @property
    def total_attack(self) -> int:
        return self.attack + self.inventory.attack_bonus

    @property
    def total_defense(self) -> int:
        return self.defense + self.inventory.defense_bonus

    def take_damage(self, damage: int) -> int:
        reduction = max(0, self.total_defense - random.randint(0, 3))
        actual = max(1, damage - reduction)
        self.hp = max(0, self.hp - actual)
        return actual

    def basic_attack(self, target: "Character") -> str:
        dmg = self.total_attack + random.randint(-2, 4)
        actual = target.take_damage(dmg)
        return f"{self.name} attacks {target.name} for {actual} damage!"

    def gain_exp(self, amount: int) -> List[str]:
        messages = []
        self.exp += amount
        messages.append(f"Gained {amount} EXP!")
        while self.level < len(EXP_TO_LEVEL) and self.exp >= EXP_TO_LEVEL[self.level]:
            self.level_up()
            messages.append(f"*** LEVEL UP! {self.name} is now level {self.level}! ***")
        return messages

    def level_up(self):
        self.level += 1
        gains = LEVEL_UP_STATS[self.char_class]
        self.max_hp += gains["max_hp"]
        self.max_mp += gains["max_mp"]
        self.attack += gains["attack"]
        self.defense += gains["defense"]
        self.speed += gains["speed"]
        self.hp = self.max_hp
        self.mp = self.max_mp


# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------

class Enemy(Character):
    def __init__(self, name: str, max_hp: int, attack: int, defense: int,
                 speed: int, exp_reward: int, gold_reward: int,
                 level: int = 1, max_mp: int = 0):
        super().__init__(name, max_hp=max_hp, max_mp=max_mp,
                         attack=attack, defense=defense, speed=speed)
        self.level = level
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def choose_action(self, target: Player) -> str:
        return self.basic_attack(target)


# Enemy factory functions (called to create fresh instances)
ENEMIES = {
    "Goblin":       lambda: Enemy("Goblin",       max_hp=22,  attack=8,  defense=2,  speed=8,  exp_reward=30,  gold_reward=random.randint(5, 12),    level=1),
    "Skeleton":     lambda: Enemy("Skeleton",     max_hp=30,  attack=10, defense=4,  speed=5,  exp_reward=45,  gold_reward=random.randint(8, 18),    level=2),
    "Wolf":         lambda: Enemy("Wolf",         max_hp=28,  attack=12, defense=3,  speed=11, exp_reward=40,  gold_reward=random.randint(5, 10),    level=2),
    "Orc":          lambda: Enemy("Orc",          max_hp=50,  attack=15, defense=6,  speed=4,  exp_reward=80,  gold_reward=random.randint(15, 30),   level=3),
    "Dark Mage":    lambda: Enemy("Dark Mage",    max_hp=40,  attack=18, defense=3,  speed=7,  exp_reward=100, gold_reward=random.randint(20, 40),   level=4),
    "Cave Troll":   lambda: Enemy("Cave Troll",   max_hp=70,  attack=20, defense=8,  speed=3,  exp_reward=120, gold_reward=random.randint(25, 50),   level=4),
    "Black Knight": lambda: Enemy("Black Knight", max_hp=90,  attack=25, defense=12, speed=6,  exp_reward=200, gold_reward=random.randint(50, 80),   level=6),
    "Dragon":       lambda: Enemy("Dragon",       max_hp=160, attack=35, defense=15, speed=8,  exp_reward=500, gold_reward=random.randint(100, 200), level=9),
}


def create_enemy(name: str) -> Enemy:
    """Create a fresh instance of a named enemy."""
    if name not in ENEMIES:
        raise ValueError(f"Unknown enemy: {name}")
    return ENEMIES[name]()
