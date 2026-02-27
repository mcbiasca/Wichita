from __future__ import annotations

from typing import Optional

import pygame

import settings


class UI:
    def __init__(self, asset_manager) -> None:
        self.asset_manager = asset_manager
        self.font_small = pygame.font.SysFont("georgia", 18)
        self.font_medium = pygame.font.SysFont("georgia", 22, bold=True)
        self.font_large = pygame.font.SysFont("georgia", 28, bold=True)
        self.font_huge = pygame.font.SysFont("georgia", 48, bold=True)
        self.show_inventory = False
        self.inv_slot_rects: list[pygame.Rect] = []
        self.equip_slot_rects: dict[str, pygame.Rect] = {}
        self.level_up_timer = 0.0
        self.level_up_level = 0
        self.is_game_over = False
        self.game_over_timer = 0.0

    def draw_hud(self, surface: pygame.Surface, player) -> None:
        screen_w, screen_h = surface.get_size()
        panel_h = 90
        panel_rect = pygame.Rect(0, screen_h - panel_h, screen_w, panel_h)
        pygame.draw.rect(surface, settings.COLORS.hud_bg, panel_rect)
        pygame.draw.rect(surface, settings.COLORS.hud_border, panel_rect, 2)

        hp_ratio = player.hp / player.max_hp if player.max_hp else 0
        mana_ratio = player.mana / player.max_mana if player.max_mana else 0
        xp_ratio = player.xp / player._xp_to_next_level() if player._xp_to_next_level() else 0

        bar_w = 280
        bar_h = 18
        hp_rect = pygame.Rect(20, panel_rect.y + 14, bar_w, bar_h)
        mana_rect = pygame.Rect(20, panel_rect.y + 40, bar_w, bar_h)
        xp_rect = pygame.Rect(20, panel_rect.y + 66, bar_w, 10)

        self._draw_bar(surface, hp_rect, hp_ratio, settings.COLORS.hp)
        self._draw_bar(surface, mana_rect, mana_ratio, settings.COLORS.mana)
        self._draw_bar(surface, xp_rect, xp_ratio, settings.COLORS.xp)

        level_text = self.font_medium.render(f"Lv {player.level}", True, settings.COLORS.text)
        surface.blit(level_text, (bar_w + 40, panel_rect.y + 12))

        gold_text = self.font_medium.render(f"Gold: {player.gold}", True, settings.COLORS.gold)
        surface.blit(gold_text, (bar_w + 40, panel_rect.y + 44))

        ammo_text = self.font_small.render(f"Ammo: {player.ammo}", True, settings.COLORS.text)
        surface.blit(ammo_text, (bar_w + 40, panel_rect.y + 68))

    def draw_minimap(self, surface: pygame.Surface, world, player, enemies) -> None:
        screen_w, _ = surface.get_size()
        map_size = settings.MINIMAP_SIZE
        map_rect = pygame.Rect(
            screen_w - map_size - settings.MINIMAP_MARGIN,
            settings.MINIMAP_MARGIN,
            map_size,
            map_size,
        )
        pygame.draw.rect(surface, settings.COLORS.minimap_bg, map_rect)
        pygame.draw.rect(surface, settings.COLORS.minimap_border, map_rect, 2)

        scale_x = map_rect.width / world.width
        scale_y = map_rect.height / world.height

        def _to_map(pos: pygame.Vector2) -> tuple[int, int]:
            return (
                int(map_rect.x + pos.x * scale_x),
                int(map_rect.y + pos.y * scale_y),
            )

        player_pos = _to_map(player.pos)
        pygame.draw.circle(surface, settings.COLORS.minimap_player, player_pos, 4)

        for enemy in enemies:
            enemy_pos = _to_map(enemy.pos)
            pygame.draw.circle(surface, settings.COLORS.minimap_enemy, enemy_pos, 3)

    def _draw_bar(self, surface: pygame.Surface, rect: pygame.Rect, ratio: float, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, settings.COLORS.shadow, rect)
        inner = rect.copy()
        inner.width = max(0, int(rect.width * max(0.0, min(ratio, 1.0))))
        pygame.draw.rect(surface, color, inner)
        pygame.draw.rect(surface, settings.COLORS.hud_border, rect, 1)

    def toggle_inventory(self) -> None:
        self.show_inventory = not self.show_inventory

    def draw_inventory(self, surface: pygame.Surface, player, mouse_pos: tuple[int, int]) -> None:
        if not self.show_inventory:
            return

        screen_w, screen_h = surface.get_size()
        panel_w = 420
        panel_h = 360
        panel_rect = pygame.Rect((screen_w - panel_w) // 2, (screen_h - panel_h) // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (15, 15, 22), panel_rect)
        pygame.draw.rect(surface, settings.COLORS.hud_border, panel_rect, 2)

        title = self.font_large.render("Inventory", True, settings.COLORS.text)
        surface.blit(title, (panel_rect.x + 18, panel_rect.y + 12))

        self.inv_slot_rects = []
        start_x = panel_rect.x + 20
        start_y = panel_rect.y + 60
        for row in range(settings.INV_ROWS):
            for col in range(settings.INV_COLS):
                slot_rect = pygame.Rect(
                    start_x + col * (settings.INV_SLOT_SIZE + 8),
                    start_y + row * (settings.INV_SLOT_SIZE + 8),
                    settings.INV_SLOT_SIZE,
                    settings.INV_SLOT_SIZE,
                )
                pygame.draw.rect(surface, (30, 30, 40), slot_rect)
                pygame.draw.rect(surface, settings.COLORS.hud_border, slot_rect, 1)
                self.inv_slot_rects.append(slot_rect)

        for index, slot in enumerate(player.inventory.slots):
            if slot is None:
                continue
            slot_rect = self.inv_slot_rects[index]
            icon = self.asset_manager.load_icon(slot.item.icon_path, settings.INV_SLOT_SIZE)
            surface.blit(icon, slot_rect.topleft)
            if slot.item.stackable and slot.count > 1:
                count_text = self.font_small.render(str(slot.count), True, settings.COLORS.text)
                surface.blit(count_text, (slot_rect.right - 16, slot_rect.bottom - 18))

        equip_x = panel_rect.right - 150
        equip_y = panel_rect.y + 70
        self.equip_slot_rects = {
            "weapon": pygame.Rect(equip_x, equip_y, settings.INV_SLOT_SIZE, settings.INV_SLOT_SIZE),
            "armor": pygame.Rect(equip_x, equip_y + settings.INV_SLOT_SIZE + 20, settings.INV_SLOT_SIZE, settings.INV_SLOT_SIZE),
        }
        for label, rect in self.equip_slot_rects.items():
            pygame.draw.rect(surface, (30, 30, 40), rect)
            pygame.draw.rect(surface, settings.COLORS.hud_border, rect, 1)
            text = self.font_small.render(label.title(), True, settings.COLORS.text)
            surface.blit(text, (rect.x, rect.y - 18))

        if player.equipment.weapon:
            icon = self.asset_manager.load_icon(player.equipment.weapon.icon_path, settings.INV_SLOT_SIZE)
            surface.blit(icon, self.equip_slot_rects["weapon"].topleft)
        if player.equipment.armor:
            icon = self.asset_manager.load_icon(player.equipment.armor.icon_path, settings.INV_SLOT_SIZE)
            surface.blit(icon, self.equip_slot_rects["armor"].topleft)

        tooltip = self._get_tooltip(player, mouse_pos)
        if tooltip:
            self._draw_tooltip(surface, tooltip, mouse_pos)

    def _get_tooltip(self, player, mouse_pos: tuple[int, int]) -> Optional[str]:
        for index, rect in enumerate(self.inv_slot_rects):
            if rect.collidepoint(mouse_pos):
                slot = player.inventory.slots[index]
                if slot:
                    return slot.item.name
        for key, rect in self.equip_slot_rects.items():
            if rect.collidepoint(mouse_pos):
                item = player.equipment.weapon if key == "weapon" else player.equipment.armor
                if item:
                    return item.name
        return None

    def _draw_tooltip(self, surface: pygame.Surface, text: str, mouse_pos: tuple[int, int]) -> None:
        padding = 8
        label = self.font_small.render(text, True, settings.COLORS.text)
        rect = label.get_rect()
        rect.topleft = (mouse_pos[0] + 12, mouse_pos[1] + 12)
        bg = pygame.Rect(rect.x - padding, rect.y - padding, rect.width + padding * 2, rect.height + padding * 2)
        pygame.draw.rect(surface, (10, 10, 14), bg)
        pygame.draw.rect(surface, settings.COLORS.hud_border, bg, 1)
        surface.blit(label, rect.topleft)

    def handle_inventory_click(self, player, mouse_pos: tuple[int, int]) -> None:
        if not self.show_inventory:
            return

        for index, rect in enumerate(self.inv_slot_rects):
            if rect.collidepoint(mouse_pos):
                slot = player.inventory.slots[index]
                if not slot:
                    return
                if slot.item.kind == "weapon":
                    self._equip_item(player, slot.item, index, "weapon")
                elif slot.item.kind == "armor":
                    self._equip_item(player, slot.item, index, "armor")
                return

        for key, rect in self.equip_slot_rects.items():
            if rect.collidepoint(mouse_pos):
                self._unequip_item(player, key)
                return

    def _equip_item(self, player, item, slot_index: int, slot_name: str) -> None:
        if slot_name == "weapon":
            if player.equipment.weapon:
                player.inventory.add_item(player.equipment.weapon)
            player.equipment.weapon = item
        elif slot_name == "armor":
            if player.equipment.armor:
                player.inventory.add_item(player.equipment.armor)
            player.equipment.armor = item
        player.inventory.slots[slot_index] = None

    def _unequip_item(self, player, slot_name: str) -> None:
        if slot_name == "weapon" and player.equipment.weapon:
            if player.inventory.add_item(player.equipment.weapon) == 0:
                player.equipment.weapon = None
        if slot_name == "armor" and player.equipment.armor:
            if player.inventory.add_item(player.equipment.armor) == 0:
                player.equipment.armor = None

    def show_level_up(self, level: int) -> None:
        self.level_up_timer = 2.5
        self.level_up_level = level

    def draw_level_up_notification(self, surface: pygame.Surface, dt: float) -> None:
        if self.level_up_timer > 0:
            self.level_up_timer -= dt
            alpha_ratio = min(1.0, self.level_up_timer / 2.5)
            text = self.font_huge.render(f"LEVEL {self.level_up_level}!", True, settings.COLORS.gold)
            screen_w, screen_h = surface.get_size()
            text_rect = text.get_rect(center=(screen_w // 2, screen_h // 2 - 80))
            surface.blit(text, text_rect)

    def show_game_over(self) -> None:
        self.is_game_over = True
        self.game_over_timer = 0.0

    def draw_game_over(self, surface: pygame.Surface) -> None:
        if not self.is_game_over:
            return
        screen_w, screen_h = surface.get_size()
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        game_over_text = self.font_huge.render("GAME OVER", True, (220, 80, 80))
        restart_text = self.font_medium.render("Press any key to restart", True, settings.COLORS.text)
        credit_text = self.font_medium.render("AI generated by Maria Biasca", True, settings.COLORS.text)
        
        game_over_rect = game_over_text.get_rect(center=(screen_w // 2, screen_h // 2 - 40))
        restart_rect = restart_text.get_rect(center=(screen_w // 2, screen_h // 2 + 40))
        credit_rect = credit_text.get_rect(center=(screen_w // 2, screen_h - 30))
        
        surface.blit(game_over_text, game_over_rect)
        surface.blit(restart_text, restart_rect)
        surface.blit(credit_text, credit_rect)
