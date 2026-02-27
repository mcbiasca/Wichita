from __future__ import annotations

import random

import pygame

import settings
from utils import vec2


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], asset_manager) -> None:
        super().__init__()
        self.asset_manager = asset_manager
        self.image = asset_manager.load_tile(settings.ENEMY_SPRITE)
        self.rect = self.image.get_rect(center=pos)
        self.pos = vec2(pos)
        self.velocity = pygame.Vector2(0, 0)

        self.max_hp = settings.ENEMY_MAX_HP
        self.hp = float(self.max_hp)
        self.damage = settings.ENEMY_DAMAGE
        self.speed = settings.ENEMY_SPEED
        self.attack_range = settings.ENEMY_ATTACK_RANGE
        self.attack_cooldown = settings.ENEMY_ATTACK_COOLDOWN
        self.attack_timer = random.uniform(0.1, 0.6)

        self.xp_reward = 20
        self.gold_drop = random.randint(6, 16)

    def update(self, dt: float, player, walls: list[pygame.Rect]) -> None:
        direction = player.pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed

        self._move_and_collide(self.velocity.x * dt, 0, walls)
        self._move_and_collide(0, self.velocity.y * dt, walls)

        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)

        if self.pos.distance_to(player.pos) <= self.attack_range and self.attack_timer <= 0:
            player.apply_damage(self.damage)
            self.attack_timer = self.attack_cooldown

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

    def apply_damage(self, amount: float) -> None:
        self.hp -= amount

    def is_dead(self) -> bool:
        return self.hp <= 0

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        surface.blit(self.image, self.rect.topleft - camera)
