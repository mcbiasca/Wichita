from __future__ import annotations

import math

import pygame

import settings
from items import Equipment, Inventory, get_item
from utils import clamp, vec2


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], asset_manager) -> None:
        super().__init__()
        self.asset_manager = asset_manager
        self.image = asset_manager.load_tile(settings.PLAYER_SPRITE)
        self.rect = self.image.get_rect(center=pos)
        self.pos = vec2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.facing = pygame.Vector2(1, 0)
        self.bob_time = 0.0

        self.max_hp = settings.PLAYER_MAX_HP
        self.hp = float(self.max_hp)
        self.max_mana = settings.PLAYER_MAX_MANA
        self.mana = float(self.max_mana)
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.max_ammo = settings.AMMO_MAX
        self.ammo = self.max_ammo
        self.kills = 0
        self.last_level = 1

        self.inventory = Inventory(settings.INV_COLS, settings.INV_ROWS)
        self.equipment = Equipment()

        self.melee_cooldown = 0.0
        self.melee_windup_timer = 0.0
        self.melee_pending = False
        self.spell_cooldown = 0.0

    def update(self, dt: float, input_dir: pygame.Vector2, walls: list[pygame.Rect], mouse_world: pygame.Vector2) -> None:
        self.bob_time += dt
        if mouse_world.length() > 0:
            aim_dir = (mouse_world - self.pos)
            if aim_dir.length() > 0:
                self.facing = aim_dir.normalize()

        if input_dir.length() > 1:
            input_dir = input_dir.normalize()
        self.velocity = input_dir * settings.PLAYER_SPEED

        self._move_and_collide(self.velocity.x * dt, 0, walls)
        self._move_and_collide(0, self.velocity.y * dt, walls)

        if self.melee_cooldown > 0:
            self.melee_cooldown = max(0.0, self.melee_cooldown - dt)
        if self.spell_cooldown > 0:
            self.spell_cooldown = max(0.0, self.spell_cooldown - dt)
        if self.melee_windup_timer > 0:
            self.melee_windup_timer = max(0.0, self.melee_windup_timer - dt)

    def _move_and_collide(self, dx: float, dy: float, walls: list[pygame.Rect]) -> None:
        self.pos.x += dx
        self.pos.y += dy
        self.rect.center = (self.pos.x, self.pos.y)
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                if dx < 0:
                    self.rect.left = wall.right
                if dy > 0:
                    self.rect.bottom = wall.top
                if dy < 0:
                    self.rect.top = wall.bottom
                self.pos = vec2(self.rect.center)

    def get_damage(self) -> int:
        bonus = self.equipment.weapon.damage if self.equipment.weapon else 0
        return settings.PLAYER_BASE_DAMAGE + bonus

    def get_defense(self) -> int:
        bonus = self.equipment.armor.defense if self.equipment.armor else 0
        return settings.PLAYER_BASE_DEFENSE + bonus

    def apply_damage(self, amount: float) -> None:
        mitigated = max(0.0, amount - self.get_defense())
        self.hp = clamp(self.hp - mitigated, 0, self.max_hp)

    def spend_mana(self, amount: float) -> bool:
        if self.mana < amount:
            return False
        self.mana -= amount
        return True

    def restore_hp(self, amount: float) -> None:
        self.hp = clamp(self.hp + amount, 0, self.max_hp)

    def restore_mana(self, amount: float) -> None:
        self.mana = clamp(self.mana + amount, 0, self.max_mana)

    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self._xp_to_next_level():
            self.xp -= self._xp_to_next_level()
            self.level += 1
            self.max_hp += 8
            self.max_mana += 5
            self.hp = self.max_hp
            self.mana = self.max_mana

    def _xp_to_next_level(self) -> int:
        return settings.KILLS_PER_LEVEL

    def register_kill(self) -> None:
        self.kills += 1
        new_level = self.kills // settings.KILLS_PER_LEVEL + 1
        self.xp = self.kills % settings.KILLS_PER_LEVEL
        if new_level > self.level:
            levels_gained = new_level - self.level
            self.level = new_level
            self.max_hp += 8 * levels_gained
            self.max_mana += 5 * levels_gained
            self.hp = self.max_hp
            self.mana = self.max_mana

    def try_use_potion(self, item_id: str) -> bool:
        slot_index = self.inventory.find_first(item_id)
        if slot_index is None:
            return False
        if item_id == "health_potion":
            item = get_item(item_id)
            if item:
                self.restore_hp(item.hp_restore)
        elif item_id == "mana_potion":
            item = get_item(item_id)
            if item:
                self.restore_mana(item.mana_restore)
        return self.inventory.remove_item(item_id, 1)

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        bob = 3 * math.sin(self.bob_time * 5)
        draw_pos = self.rect.topleft - camera + pygame.Vector2(0, -bob)
        surface.blit(self.image, draw_pos)

    def to_dict(self) -> dict:
        return {
            "pos": [self.pos.x, self.pos.y],
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "ammo": self.ammo,
            "max_ammo": self.max_ammo,
            "kills": self.kills,
            "inventory": self.inventory.to_dict(),
            "equipment": self.equipment.to_dict(),
        }

    def from_dict(self, data: dict) -> None:
        pos = data.get("pos", [self.pos.x, self.pos.y])
        self.pos = vec2((pos[0], pos[1]))
        self.rect.center = (self.pos.x, self.pos.y)
        self.hp = float(data.get("hp", self.max_hp))
        self.max_hp = int(data.get("max_hp", self.max_hp))
        self.mana = float(data.get("mana", self.max_mana))
        self.max_mana = int(data.get("max_mana", self.max_mana))
        self.level = int(data.get("level", self.level))
        self.xp = int(data.get("xp", self.xp))
        self.gold = int(data.get("gold", self.gold))
        self.max_ammo = int(data.get("max_ammo", self.max_ammo))
        self.ammo = int(data.get("ammo", self.max_ammo))
        self.kills = int(data.get("kills", self.kills))
        self.inventory.from_dict(data.get("inventory", []))
        self.equipment.from_dict(data.get("equipment", {}))
