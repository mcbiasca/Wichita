"""World map, locations, and encounters for the Wichita RPG."""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from src.character import create_enemy, Enemy


@dataclass
class Location:
    name: str
    description: str
    enemy_pool: List[str]  # enemy names from character.ENEMIES
    level_range: tuple  # (min, max) recommended player level
    is_safe: bool = False

    def random_encounter(self) -> Optional[Enemy]:
        # 70% chance of no encounter when randomly checking
        if not self.enemy_pool or random.random() < 0.3:
            return None
        return create_enemy(random.choice(self.enemy_pool))

    def get_encounter(self) -> Optional[Enemy]:
        """Always returns an enemy (for forced encounters)."""
        if not self.enemy_pool:
            return None
        return create_enemy(random.choice(self.enemy_pool))


# World locations
TOWN = Location(
    name="Town of Wichita",
    description=(
        "A small but lively frontier town. The smell of wood smoke fills the air.\n"
        "A tavern, blacksmith, and general store line the dusty main street."
    ),
    enemy_pool=[],
    level_range=(1, 99),
    is_safe=True,
)

WHISPERING_FOREST = Location(
    name="Whispering Forest",
    description=(
        "Tall, ancient trees block out the sun. Strange noises echo through the branches.\n"
        "Weak monsters lurk here, but the forest holds secrets."
    ),
    enemy_pool=["Goblin", "Wolf", "Skeleton"],
    level_range=(1, 3),
)

DARK_CAVES = Location(
    name="Dark Caves",
    description=(
        "A labyrinthine network of tunnels carved deep into the mountain.\n"
        "The walls glitter with strange minerals, and danger hides around every corner."
    ),
    enemy_pool=["Skeleton", "Orc", "Dark Mage", "Cave Troll"],
    level_range=(3, 6),
)

DRAGONS_LAIR = Location(
    name="Dragon's Lair",
    description=(
        "An enormous volcanic cavern. The heat is overwhelming.\n"
        "Bones of fallen heroes litter the ground. The Dragon awaits."
    ),
    enemy_pool=["Black Knight", "Dragon"],
    level_range=(7, 99),
)

WORLD_MAP: List[Location] = [
    TOWN,
    WHISPERING_FOREST,
    DARK_CAVES,
    DRAGONS_LAIR,
]
