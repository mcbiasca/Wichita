from __future__ import annotations

import math

import pygame

import settings


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, direction: pygame.Vector2, asset_manager, damage: int) -> None:
        super().__init__()
        self.image = asset_manager.load_tile(settings.PROJECTILE_SPRITE)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.velocity = direction * settings.PROJECTILE_SPEED
        self.damage = damage
        self.life_timer = settings.PROJECTILE_LIFETIME

    def update(self, dt: float, walls: list[pygame.Rect], enemies: pygame.sprite.Group) -> None:
        self.pos += self.velocity * dt
        self.rect.center = (self.pos.x, self.pos.y)

        self.life_timer -= dt
        if self.life_timer <= 0:
            self.kill()
            return

        for wall in walls:
            if self.rect.colliderect(wall):
                self.kill()
                return

        hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in hits:
            enemy.apply_damage(self.damage)
            self.kill()
            return

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        surface.blit(self.image, self.rect.topleft - camera)


def perform_melee(player, enemies: pygame.sprite.Group) -> int:
    radius = settings.PLAYER_ATTACK_RANGE
    hits = 0
    for enemy in enemies:
        to_enemy = enemy.pos - player.pos
        if to_enemy.length() <= radius:
            if to_enemy.length() == 0:
                facing_dot = 1
            else:
                facing_dot = player.facing.dot(to_enemy.normalize())
            if facing_dot >= math.cos(math.radians(90)):
                enemy.apply_damage(player.get_damage())
                hits += 1
    return hits
