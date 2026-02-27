from __future__ import annotations

from dataclasses import dataclass

# Display
DESIRED_WIDTH = 1440
DESIRED_HEIGHT = 900
WINDOW_MARGIN_W = 40
WINDOW_MARGIN_H = 80
FPS = 60

# World
TILE_SIZE = 64
WORLD_TILES_X = 60
WORLD_TILES_Y = 40
WORLD_WIDTH = WORLD_TILES_X * TILE_SIZE
WORLD_HEIGHT = WORLD_TILES_Y * TILE_SIZE

# Player
PLAYER_SPEED = 220
PLAYER_MAX_HP = 120
PLAYER_MAX_MANA = 80
PLAYER_BASE_DAMAGE = 12
PLAYER_BASE_DEFENSE = 2
PLAYER_ATTACK_RANGE = 80
PLAYER_MELEE_COOLDOWN = 0.45
PLAYER_MELEE_WINDUP = 0.12
PLAYER_SPELL_COOLDOWN = 0.7
PLAYER_SPELL_COST = 12

# Enemy
ENEMY_SPEED = 140
ENEMY_MAX_HP = 50
ENEMY_DAMAGE = 8
ENEMY_ATTACK_RANGE = 48
ENEMY_ATTACK_COOLDOWN = 0.9
ENEMY_SPAWN_WAVE_SIZE = 6
ENEMY_SPAWN_WAVE_GROWTH = 2

# Projectile
PROJECTILE_SPEED = 420
PROJECTILE_DAMAGE = 18
PROJECTILE_LIFETIME = 1.6

# Ammo
AMMO_MAX = 200
AMMO_GIFT_AMOUNT = 200
AMMO_GIFT_COUNT = 3
AMMO_BULLET_DAMAGE = 999
KILLS_PER_LEVEL = 20

# Inventory
INV_COLS = 5
INV_ROWS = 4
INV_SLOT_SIZE = 56

# Minimap
MINIMAP_SIZE = 180
MINIMAP_MARGIN = 16

# Assets
ASSET_ROOT = "assets/kenney"

PLAYER_SPRITE = "characters/hero.png"
ENEMY_SPRITE = "enemies/goblin.png"
FLOOR_TILE = "tiles/floor.png"
WALL_TILE = "tiles/wall.png"
PROP_CRATE = "props/crate.png"
PROP_BARREL = "props/barrel.png"
PROP_ROCK = "props/rock.png"
PROP_BUSH = "props/bush.png"
PROP_FLOWER = "props/flower.png"
PROP_MUSHROOM = "props/mushroom.png"
PROJECTILE_SPRITE = "fx/projectile.png"
MELEE_SPRITE = "fx/swing.png"
UI_PANEL = "ui/panel.png"
UI_ICON_HP = "ui/heart.png"
UI_ICON_MANA = "ui/mana.png"
UI_ICON_GOLD = "ui/gold.png"
UI_ICON_XP = "ui/xp.png"
UI_ICON_GIFT = "ui/gift.png"

ITEM_ICON_HP_POTION = "ui/potion_red.png"
ITEM_ICON_MANA_POTION = "ui/potion_blue.png"
ITEM_ICON_SWORD = "ui/sword.png"
ITEM_ICON_ARMOR = "ui/armor.png"
ITEM_ICON_APPLE = "ui/apple.png"

SAVE_FILE = "savegame.json"


@dataclass(frozen=True)
class Colors:
    bg: tuple[int, int, int] = (18, 18, 24)
    hud_bg: tuple[int, int, int] = (20, 20, 28)
    hud_border: tuple[int, int, int] = (70, 70, 90)
    hp: tuple[int, int, int] = (190, 60, 60)
    mana: tuple[int, int, int] = (60, 90, 180)
    xp: tuple[int, int, int] = (180, 160, 60)
    gold: tuple[int, int, int] = (210, 180, 60)
    text: tuple[int, int, int] = (235, 235, 240)
    shadow: tuple[int, int, int] = (10, 10, 12)
    minimap_bg: tuple[int, int, int] = (12, 12, 18)
    minimap_border: tuple[int, int, int] = (85, 85, 110)
    minimap_player: tuple[int, int, int] = (110, 220, 140)
    minimap_enemy: tuple[int, int, int] = (210, 90, 90)


COLORS = Colors()
