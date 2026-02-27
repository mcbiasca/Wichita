from __future__ import annotations

import os
from typing import Dict, Tuple

import pygame

import settings


class AssetManager:
    def __init__(self, tile_size: int) -> None:
        self.tile_size = tile_size
        self.cache: Dict[Tuple[str, Tuple[int, int] | None], pygame.Surface] = {}

    def load_image(self, rel_path: str, size: tuple[int, int] | None = None) -> pygame.Surface:
        key = (rel_path, size)
        if key in self.cache:
            return self.cache[key]

        full_path = os.path.join(settings.ASSET_ROOT, rel_path)
        surface: pygame.Surface
        if os.path.exists(full_path):
            surface = pygame.image.load(full_path).convert_alpha()
        else:
            surface = self._fallback_for(rel_path, size or (self.tile_size, self.tile_size))

        if size is not None and surface.get_size() != size:
            surface = pygame.transform.smoothscale(surface, size)

        self.cache[key] = surface
        return surface

    def load_tile(self, rel_path: str) -> pygame.Surface:
        return self.load_image(rel_path, (self.tile_size, self.tile_size))

    def load_icon(self, rel_path: str, size: int) -> pygame.Surface:
        return self.load_image(rel_path, (size, size))

    def _fallback_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((80, 80, 90, 220))
        pygame.draw.rect(surface, (25, 25, 30, 255), surface.get_rect(), 3)
        return surface

    def _fallback_for(self, rel_path: str, size: tuple[int, int]) -> pygame.Surface:
        if rel_path == settings.FLOOR_TILE:
            return self._fallback_floor_surface(size)
        if rel_path == settings.WALL_TILE:
            return self._fallback_wall_surface(size)
        if rel_path == settings.PLAYER_SPRITE:
            return self._fallback_player_surface(size)
        if rel_path == settings.ENEMY_SPRITE:
            return self._fallback_enemy_surface(size)
        if rel_path == settings.PROJECTILE_SPRITE:
            return self._fallback_projectile_surface(size)
        if rel_path == settings.UI_ICON_GIFT:
            return self._fallback_gift_surface(size)
        if rel_path == settings.ITEM_ICON_APPLE:
            return self._fallback_apple_surface(size)
        if rel_path == settings.PROP_CRATE:
            return self._fallback_crate_surface(size)
        if rel_path == settings.PROP_BARREL:
            return self._fallback_barrel_surface(size)
        if rel_path == settings.PROP_ROCK:
            return self._fallback_rock_surface(size)
        if rel_path == settings.PROP_BUSH:
            return self._fallback_bush_surface(size)
        if rel_path == settings.PROP_FLOWER:
            return self._fallback_flower_surface(size)
        if rel_path == settings.PROP_MUSHROOM:
            return self._fallback_mushroom_surface(size)
        return self._fallback_surface(size)

    def _fallback_wall_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Stone dungeon walls with brick pattern
        brick_color = (100, 95, 90, 255)
        mortar_color = (60, 55, 50, 255)
        shadow_color = (70, 65, 60, 255)
        
        surface.fill(brick_color)
        
        # Brick pattern
        brick_h = max(6, size[1] // 3)
        brick_w = max(12, size[0] // 2)
        
        for y in range(0, size[1], brick_h):
            offset = (brick_w // 2) if (y // brick_h) % 2 == 1 else 0
            for x in range(-offset, size[0], brick_w):
                pygame.draw.rect(surface, mortar_color, (x, y, brick_w, brick_h), 1)
                pygame.draw.line(surface, shadow_color, (x + 2, y + 2), (x + brick_w - 2, y + 2), 1)
        
        # Stone texture
        pygame.draw.rect(surface, shadow_color, surface.get_rect(), 2)
        return surface

    def _fallback_floor_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Lush grass floor
        grass_base = (60, 140, 70, 255)
        grass_dark = (45, 110, 55, 255)
        grass_light = (75, 160, 85, 255)
        
        surface.fill(grass_base)
        
        # Grass blade texture
        import random
        random.seed(hash(size))
        for _ in range(8):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            color = grass_dark if random.random() < 0.5 else grass_light
            pygame.draw.line(surface, color, (x, y), (x, max(0, y - 3)), 1)
        
        # Grid lines for tileable look
        for x in range(0, size[0], max(1, size[0] // 4)):
            pygame.draw.line(surface, grass_dark, (x, 0), (x, size[1]), 1)
        for y in range(0, size[1], max(1, size[1] // 4)):
            pygame.draw.line(surface, grass_dark, (0, y), (size[0], y), 1)
        
        return surface

    def _fallback_player_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Wizard/mage character
        robe_color = (90, 70, 180, 255)
        skin = (230, 200, 170, 255)
        hat_color = (70, 50, 130, 255)
        staff_color = (140, 100, 60, 255)
        
        # Wizard hat
        hat_y = max(2, size[1] // 12)
        hat_w = max(8, size[0] // 3)
        hat_pts = [(size[0] // 2 - hat_w // 2, hat_y + hat_w), (size[0] // 2, hat_y - hat_w // 2), (size[0] // 2 + hat_w // 2, hat_y + hat_w)]
        pygame.draw.polygon(surface, hat_color, hat_pts)
        pygame.draw.circle(surface, (255, 220, 100, 255), hat_pts[1], max(2, hat_w // 8))
        
        # Head/face
        head_y = hat_y + hat_w + max(2, size[0] // 8)
        head_size = max(5, size[0] // 6)
        pygame.draw.circle(surface, skin, (size[0] // 2, head_y), head_size)
        
        # Eyes
        pygame.draw.circle(surface, (30, 30, 40, 255), (size[0] // 2 - head_size // 3, head_y - head_size // 4), max(1, head_size // 5))
        pygame.draw.circle(surface, (30, 30, 40, 255), (size[0] // 2 + head_size // 3, head_y - head_size // 4), max(1, head_size // 5))
        
        # Beard
        beard_pts = [(size[0] // 2 - head_size // 2, head_y + head_size // 3), (size[0] // 2, head_y + head_size + 2), (size[0] // 2 + head_size // 2, head_y + head_size // 3)]
        pygame.draw.polygon(surface, (200, 200, 210, 255), beard_pts)
        
        # Robe body
        robe_y = head_y + head_size
        robe_h = max(10, size[1] // 2)
        robe_w = max(12, size[0] * 2 // 3)
        pygame.draw.ellipse(surface, robe_color, (size[0] // 2 - robe_w // 2, robe_y, robe_w, robe_h))
        
        # Staff in hand
        staff_x = size[0] - max(8, size[0] // 8)
        pygame.draw.line(surface, staff_color, (staff_x, robe_y + 4), (staff_x, size[1] - 4), max(2, size[0] // 16))
        pygame.draw.circle(surface, (100, 150, 255, 255), (staff_x, robe_y + 4), max(3, size[0] // 12))
        
        return surface

    def _fallback_enemy_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Dungeon goblin/orc enemy
        skin = (90, 140, 80, 255)
        dark_skin = (60, 100, 50, 255)
        cloth = (150, 80, 60, 255)
        dark = (20, 20, 20, 255)
        
        # Head - slightly irregular for goblin look
        head_y = max(size[1] // 5, 6)
        head_size = max(4, size[0] // 5)
        pygame.draw.circle(surface, skin, (size[0] // 2, head_y), head_size)
        
        # Ears/horns
        pygame.draw.circle(surface, dark_skin, (size[0] // 2 - head_size - 2, head_y - 2), max(2, head_size // 3))
        pygame.draw.circle(surface, dark_skin, (size[0] // 2 + head_size + 2, head_y - 2), max(2, head_size // 3))
        
        # Angry eyes
        pygame.draw.circle(surface, dark, (size[0] // 2 - head_size // 3, head_y - head_size // 3), max(1, head_size // 5))
        pygame.draw.circle(surface, dark, (size[0] // 2 + head_size // 3, head_y - head_size // 3), max(1, head_size // 5))
        
        # Body - wider, menacing
        chest_y = head_y + head_size
        chest_h = max(10, size[1] // 2)
        chest_w = size[0] * 2 // 3
        pygame.draw.rect(surface, cloth, (size[0] //2 - chest_w // 2, chest_y, chest_w, chest_h))
        pygame.draw.rect(surface, dark_skin, (size[0] // 2 - chest_w // 2, chest_y, chest_w, chest_h // 2))
        
        # Claws/arms
        arm_h = max(6, size[1] // 3)
        pygame.draw.line(surface, dark_skin, (size[0] // 2 - chest_w // 2, chest_y + 4), (max(2, size[0] // 8), chest_y + arm_h), max(2, size[0] // 12))
        pygame.draw.line(surface, dark_skin, (size[0] // 2 + chest_w // 2, chest_y + 4), (size[0] - max(2, size[0] // 8), chest_y + arm_h), max(2, size[0] // 12))
        
        # Legs
        leg_y = chest_y + chest_h
        leg_h = max(4, size[1] // 5)
        pygame.draw.rect(surface, dark_skin, (size[0] // 2 - size[0] // 8, leg_y, max(2, size[0] // 10), leg_h))
        pygame.draw.rect(surface, dark_skin, (size[0] // 2 + size[0] // 8 - max(2, size[0] // 10), leg_y, max(2, size[0] // 10), leg_h))
        
        return surface

    def _fallback_projectile_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center = (size[0] // 2, size[1] // 2)
        radius = max(4, min(size[0], size[1]) // 6)
        pygame.draw.circle(surface, (90, 170, 255, 230), center, radius)
        pygame.draw.circle(surface, (30, 80, 170, 255), center, radius, 2)
        return surface

    def _fallback_gift_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        box_color = (200, 60, 80, 255)
        ribbon = (240, 220, 100, 255)
        pygame.draw.rect(surface, box_color, (2, 6, size[0] - 4, size[1] - 8))
        pygame.draw.rect(surface, ribbon, (size[0] // 2 - 3, 6, 6, size[1] - 8))
        pygame.draw.rect(surface, ribbon, (2, size[1] // 2, size[0] - 4, 6))
        pygame.draw.rect(surface, (40, 15, 20, 255), (2, 6, size[0] - 4, size[1] - 8), 2)
        pygame.draw.circle(surface, ribbon, (size[0] // 2 - 6, 4), 4)
        pygame.draw.circle(surface, ribbon, (size[0] // 2 + 6, 4), 4)
        return surface

    def _fallback_apple_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        
        apple_color = (220, 50, 50, 255)
        stem_color = (100, 80, 30, 255)
        leaf_color = (80, 150, 60, 255)
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        apple_radius = max(size[0] // 3, max(size[1] // 3, 8))
        
        # Draw apple body
        pygame.draw.circle(surface, apple_color, (center_x, center_y), apple_radius)
        
        # Draw stem
        stem_start = (center_x, center_y - apple_radius - 2)
        stem_end = (center_x, center_y - apple_radius - apple_radius // 2 - 2)
        pygame.draw.line(surface, stem_color, stem_start, stem_end, max(2, apple_radius // 4))
        
        # Draw leaf
        leaf_x = center_x + apple_radius // 2
        leaf_pts = [(leaf_x, center_y - apple_radius - 4), (leaf_x + apple_radius // 3, center_y - apple_radius - apple_radius // 3), (leaf_x + apple_radius // 4, center_y - apple_radius - apple_radius // 2)]
        pygame.draw.polygon(surface, leaf_color, leaf_pts)
        
        return surface

    def _fallback_crate_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        wood_color = (160, 110, 70, 255)
        dark_wood = (100, 70, 40, 255)
        pygame.draw.rect(surface, wood_color, (2, 2, size[0] - 4, size[1] - 4))
        pygame.draw.line(surface, dark_wood, (2, size[1] // 3), (size[0] - 2, size[1] // 3), 2)
        pygame.draw.line(surface, dark_wood, (2, size[1] * 2 // 3), (size[0] - 2, size[1] * 2 // 3), 2)
        pygame.draw.line(surface, dark_wood, (size[0] // 3, 2), (size[0] // 3, size[1] - 2), 2)
        pygame.draw.line(surface, dark_wood, (size[0] * 2 // 3, 2), (size[0] * 2 // 3, size[1] - 2), 2)
        pygame.draw.rect(surface, dark_wood, (2, 2, size[0] - 4, size[1] - 4), 2)
        return surface

    def _fallback_barrel_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        barrel_color = (140, 100, 60, 255)
        band_color = (80, 80, 85, 255)
        center = (size[0] // 2, size[1] // 2)
        radius = min(size[0], size[1]) // 2 - 2
        pygame.draw.circle(surface, barrel_color, center, radius)
        pygame.draw.circle(surface, band_color, center, radius, 2)
        pygame.draw.line(surface, band_color, (center[0], center[1] - radius // 2), (center[0], center[1] + radius // 2), 2)
        pygame.draw.arc(surface, band_color, (center[0] - radius, center[1] - radius // 3, radius * 2, radius // 2), 0, 3.14159, 2)
        return surface

    def _fallback_rock_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        rock_color = (110, 105, 100, 255)
        shadow_color = (70, 65, 60, 255)
        rock_pts = [(size[0] // 2, 2), (size[0] - 4, size[1] // 3), (size[0] - 2, size[1] - 4), (size[0] // 3, size[1] - 2), (2, size[1] // 2)]
        pygame.draw.polygon(surface, rock_color, rock_pts)
        pygame.draw.polygon(surface, shadow_color, rock_pts, 2)
        return surface

    def _fallback_bush_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        bush_color = (60, 120, 50, 255)
        dark_bush = (40, 90, 35, 255)
        center = (size[0] // 2, size[1] // 2)
        radius = min(size[0], size[1]) // 3
        pygame.draw.circle(surface, bush_color, (center[0] - radius, center[1]), radius)
        pygame.draw.circle(surface, bush_color, center, radius)
        pygame.draw.circle(surface, bush_color, (center[0] + radius, center[1]), radius)
        pygame.draw.circle(surface, dark_bush, (center[0], center[1] - radius // 2), radius // 2)
        return surface

    def _fallback_flower_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        petal_colors = [(220, 80, 120, 255), (250, 200, 80, 255), (200, 100, 220, 255)]
        import random
        random.seed(hash(size))
        petal_color = random.choice(petal_colors)
        center_color = (255, 220, 100, 255)
        stem_color = (80, 140, 60, 255)
        center = (size[0] // 2, size[1] // 2)
        petal_radius = min(size[0], size[1]) // 4
        for angle in [0, 1.57, 3.14, 4.71]:
            import math
            x = int(center[0] + math.cos(angle) * petal_radius)
            y = int(center[1] + math.sin(angle) * petal_radius)
            pygame.draw.circle(surface, petal_color, (x, y), petal_radius)
        pygame.draw.circle(surface, center_color, center, petal_radius // 2)
        pygame.draw.line(surface, stem_color, (center[0], center[1]), (center[0], size[1] - 2), 2)
        return surface

    def _fallback_mushroom_surface(self, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        cap_color = (200, 60, 60, 255)
        spot_color = (255, 255, 240, 255)
        stem_color = (240, 230, 210, 255)
        cap_y = size[1] // 3
        cap_w = size[0] - 4
        cap_h = size[1] // 2
        pygame.draw.ellipse(surface, cap_color, (2, cap_y, cap_w, cap_h))
        pygame.draw.circle(surface, spot_color, (size[0] // 3, cap_y + cap_h // 3), max(2, size[0] // 8))
        pygame.draw.circle(surface, spot_color, (size[0] * 2 // 3, cap_y + cap_h // 2), max(2, size[0] // 10))
        stem_rect = pygame.Rect(size[0] // 2 - size[0] // 6, cap_y + cap_h // 2, size[0] // 3, size[1] - cap_y - cap_h // 2 - 2)
        pygame.draw.rect(surface, stem_color, stem_rect)
        pygame.draw.rect(surface, (180, 170, 160, 255), stem_rect, 1)
        return surface
