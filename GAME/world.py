from __future__ import annotations

import random

import pygame

import settings
from utils import vec2


class World:
    def __init__(self, asset_manager) -> None:
        self.asset_manager = asset_manager
        self.width = settings.WORLD_WIDTH
        self.height = settings.WORLD_HEIGHT
        self.tile_size = settings.TILE_SIZE

        self.floor_tiles: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.wall_tiles: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.walls: list[pygame.Rect] = []
        self.prop_tiles: list[tuple[pygame.Surface, pygame.Rect]] = []

        self._generate()

    def _generate(self) -> None:
        floor = self.asset_manager.load_tile(settings.FLOOR_TILE)
        wall = self.asset_manager.load_tile(settings.WALL_TILE)
        for y in range(settings.WORLD_TILES_Y):
            for x in range(settings.WORLD_TILES_X):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                self.floor_tiles.append((floor, rect))

        for x in range(settings.WORLD_TILES_X):
            self._add_wall(x, 0, wall)
            self._add_wall(x, settings.WORLD_TILES_Y - 1, wall)
        for y in range(settings.WORLD_TILES_Y):
            self._add_wall(0, y, wall)
            self._add_wall(settings.WORLD_TILES_X - 1, y, wall)

        for _ in range(350):
            x = random.randint(2, settings.WORLD_TILES_X - 3)
            y = random.randint(2, settings.WORLD_TILES_Y - 3)
            if random.random() < 0.4:
                self._add_wall(x, y, wall)
        
        # Add decorative props
        prop_paths = [settings.PROP_BARREL, settings.PROP_ROCK, settings.PROP_BUSH, 
                      settings.PROP_FLOWER, settings.PROP_MUSHROOM, settings.PROP_CRATE]
        for _ in range(200):
            x = random.randint(1, settings.WORLD_TILES_X - 2)
            y = random.randint(1, settings.WORLD_TILES_Y - 2)
            prop_path = random.choice(prop_paths)
            prop_surface = self.asset_manager.load_tile(prop_path)
            rect = pygame.Rect(x * self.tile_size + random.randint(-self.tile_size // 4, self.tile_size // 4),
                               y * self.tile_size + random.randint(-self.tile_size // 4, self.tile_size // 4),
                               self.tile_size // 2, self.tile_size // 2)
            self.prop_tiles.append((prop_surface, rect))

    def _add_wall(self, x: int, y: int, wall_surface: pygame.Surface) -> None:
        rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
        self.wall_tiles.append((wall_surface, rect))
        self.walls.append(rect)

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        for tile, rect in self.floor_tiles:
            surface.blit(tile, rect.topleft - camera)
        for tile, rect in self.prop_tiles:
            surface.blit(tile, rect.topleft - camera)
        for tile, rect in self.wall_tiles:
            surface.blit(tile, rect.topleft - camera)

    def get_spawn_points(self) -> list[pygame.Vector2]:
        points: list[pygame.Vector2] = []
        margin = self.tile_size * 2
        for _ in range(12):
            points.append(vec2((random.randint(margin, self.width - margin), margin)))
            points.append(vec2((random.randint(margin, self.width - margin), self.height - margin)))
            points.append(vec2((margin, random.randint(margin, self.height - margin))))
            points.append(vec2((self.width - margin, random.randint(margin, self.height - margin))))
        return points
