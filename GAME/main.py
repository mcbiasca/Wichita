from __future__ import annotations

import random

import pygame

import settings
from assets import AssetManager
from audio import AudioManager
from combat import Projectile, perform_melee
from enemy import Enemy
from items import Pickup, get_item
from player import Player
from ui import UI
from utils import load_json, save_json, vec2
from world import World


def compute_window_size() -> tuple[int, int]:
    info = pygame.display.Info()
    width = min(settings.DESIRED_WIDTH, info.current_w - settings.WINDOW_MARGIN_W)
    height = min(settings.DESIRED_HEIGHT, info.current_h - settings.WINDOW_MARGIN_H)
    return max(800, width), max(600, height)


def random_world_position(world: World, walls: list[pygame.Rect]) -> pygame.Vector2:
    margin = settings.TILE_SIZE
    for _ in range(200):
        x = random.randint(margin, world.width - margin)
        y = random.randint(margin, world.height - margin)
        rect = pygame.Rect(x - 16, y - 16, 32, 32)
        if not any(rect.colliderect(wall) for wall in walls):
            return pygame.Vector2(x, y)
    return pygame.Vector2(world.width / 2, world.height / 2)


def spawn_enemy_random(enemies: pygame.sprite.Group, world: World, asset_manager: AssetManager) -> None:
    pos = random_world_position(world, world.walls)
    enemies.add(Enemy((pos.x, pos.y), asset_manager))


class DeathSplash:
    def __init__(self, pos: pygame.Vector2, lifetime: float = 0.6) -> None:
        self.pos = pos
        self.life_timer = lifetime
        self.max_life = lifetime

    def update(self, dt: float) -> bool:
        self.life_timer -= dt
        return self.life_timer > 0

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        alpha_ratio = self.life_timer / self.max_life
        draw_pos = self.pos - camera
        cx, cy = int(draw_pos.x), int(draw_pos.y)
        
        apple_color = (220, 50, 50, int(230 * alpha_ratio))
        stem_color = (100, 80, 30, int(200 * alpha_ratio))
        leaf_color = (80, 150, 60, int(200 * alpha_ratio))
        
        pygame.draw.circle(surface, apple_color, (cx, cy), 12)
        pygame.draw.line(surface, stem_color, (cx, cy - 12), (cx, cy - 18), 2)
        leaf_pts = [(cx + 8, cy - 12), (cx + 12, cy - 8), (cx + 8, cy - 14)]
        pygame.draw.polygon(surface, leaf_color, leaf_pts)


class BloodSplash:
    def __init__(self, pos: pygame.Vector2, lifetime: float = 0.5) -> None:
        self.pos = pos
        self.life_timer = lifetime
        self.max_life = lifetime
        self.particles = []
        for _ in range(8):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(80, 150)
            vx = speed * __import__("math").cos(angle)
            vy = speed * __import__("math").sin(angle)
            self.particles.append({"x": pos.x, "y": pos.y, "vx": vx, "vy": vy})

    def update(self, dt: float) -> bool:
        self.life_timer -= dt
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
        return self.life_timer > 0

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2) -> None:
        alpha_ratio = max(0, self.life_timer / self.max_life)
        color = (200, 30, 30, int(180 * alpha_ratio))
        for p in self.particles:
            draw_x = int(p["x"] - camera.x)
            draw_y = int(p["y"] - camera.y)
            pygame.draw.circle(surface, color, (draw_x, draw_y), 3)


def main() -> None:
    pygame.init()
    pygame.font.init()

    size = compute_window_size()
    flags = pygame.SCALED | pygame.RESIZABLE
    screen = pygame.display.set_mode(size, flags)
    pygame.display.set_caption("Kenney ARPG Prototype")

    asset_manager = AssetManager(settings.TILE_SIZE)
    
    running = True
    while running:
        running = game_loop(screen, asset_manager, size, flags)

    pygame.quit()


def game_loop(screen: pygame.Surface, asset_manager: AssetManager, size: tuple[int, int], flags: int) -> bool:
    world = World(asset_manager)
    player = Player((world.width / 2, world.height / 2), asset_manager)
    audio = AudioManager()

    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    death_splashes: list[DeathSplash] = []
    blood_splashes: list[BloodSplash] = []

    ui = UI(asset_manager)

    clock = pygame.time.Clock()
    game_running = True
    fullscreen = False
    
    # Start background music
    audio.play_music(loops=-1)
    for _ in range(settings.ENEMY_SPAWN_WAVE_SIZE):
        spawn_enemy_random(enemies, world, asset_manager)

    for _ in range(settings.AMMO_GIFT_COUNT):
        pos = random_world_position(world, world.walls)
        pickups.add(Pickup((pos.x, pos.y), asset_manager, ammo=settings.AMMO_GIFT_AMOUNT, icon_size=40))

    while game_running:
        dt = clock.tick(settings.FPS) / 1000.0
        mouse_screen = pygame.mouse.get_pos()
        screen_w, screen_h = screen.get_size()
        camera = pygame.Vector2(player.pos.x - screen_w / 2, player.pos.y - screen_h / 2)
        camera.x = max(0, min(camera.x, world.width - screen_w))
        camera.y = max(0, min(camera.y, world.height - screen_h))
        mouse_world = vec2(mouse_screen) + camera

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                return False
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                size = event.size
                screen = pygame.display.set_mode(size, flags)
            elif event.type == pygame.KEYDOWN:
                if ui.is_game_over:
                    return True
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
                    else:
                        screen = pygame.display.set_mode(size, flags)
                elif event.key == pygame.K_i:
                    ui.toggle_inventory()
                    audio.play_sound('menu')
                elif event.key == pygame.K_F5:
                    save_json(settings.SAVE_FILE, player.to_dict())
                elif event.key == pygame.K_F9:
                    data = load_json(settings.SAVE_FILE)
                    if data:
                        player.from_dict(data)
                elif event.key == pygame.K_1:
                    player.try_use_potion("health_potion")
                elif event.key == pygame.K_2:
                    player.try_use_potion("mana_potion")
                elif event.key == pygame.K_SPACE:
                    if player.spell_cooldown <= 0 and player.ammo > 0:
                        direction = -player.velocity
                        if direction.length() == 0:
                            direction = player.facing
                        if direction.length() > 0:
                            projectile = Projectile(
                                player.pos,
                                direction.normalize(),
                                asset_manager,
                                settings.AMMO_BULLET_DAMAGE,
                            )
                            projectiles.add(projectile)
                            player.ammo -= 1
                            player.spell_cooldown = settings.PLAYER_SPELL_COOLDOWN
                            audio.play_sound('shoot')
                elif event.key == pygame.K_b:
                    if player.spell_cooldown <= 0 and player.spend_mana(settings.PLAYER_SPELL_COST):
                        direction = (mouse_world - player.pos)
                        if direction.length() > 0:
                            projectile = Projectile(player.pos, direction.normalize(), asset_manager, settings.PROJECTILE_DAMAGE)
                            projectiles.add(projectile)
                            player.spell_cooldown = settings.PLAYER_SPELL_COOLDOWN
                            audio.play_sound('shoot')
                elif event.key == pygame.K_n:
                    if player.melee_cooldown <= 0 and player.melee_windup_timer <= 0:
                        player.melee_windup_timer = settings.PLAYER_MELEE_WINDUP
                        player.melee_pending = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if ui.show_inventory:
                        ui.handle_inventory_click(player, event.pos)

        if not ui.is_game_over:
            audio.update_music()
            keys = pygame.key.get_pressed()
            input_dir = pygame.Vector2(
                (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
                (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP]),
            )

            player.update(dt, input_dir, world.walls, mouse_world)

            if player.melee_pending and player.melee_windup_timer <= 0:
                hits = perform_melee(player, enemies)
                if hits > 0:
                    audio.play_sound('hit')
                player.melee_pending = False
                player.melee_cooldown = settings.PLAYER_MELEE_COOLDOWN

            enemies.update(dt, player, world.walls)
            projectiles.update(dt, world.walls, enemies)
            pickups.update(dt)
            
            death_splashes = [s for s in death_splashes if s.update(dt)]
            blood_splashes = [s for s in blood_splashes if s.update(dt)]

            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    blood_splashes.append(BloodSplash(player.pos))
                    audio.play_sound('scream')

            for enemy in list(enemies):
                if enemy.is_dead():
                    enemy.kill()
                    audio.play_sound('death')
                    death_splashes.append(DeathSplash(enemy.pos))
                    old_level = player.level
                    player.register_kill()
                    if player.level > old_level:
                        ui.show_level_up(player.level)
                        audio.play_sound('levelup')
                    spawn_enemy_random(enemies, world, asset_manager)
                    
                    apple_item = get_item("apple")
                    if apple_item:
                        pickups.add(Pickup(enemy.pos, asset_manager, item=apple_item, icon_size=64))

            for pickup in list(pickups):
                if pickup.rect.colliderect(player.rect):
                    if pickup.ammo > 0:
                        player.ammo = player.max_ammo
                        new_pos = random_world_position(world, world.walls)
                        pickup.set_position((new_pos.x, new_pos.y))
                        audio.play_sound('pickup')
                    elif pickup.gold > 0:
                        player.gold += pickup.gold
                        pickup.kill()
                        audio.play_sound('pickup')
                    elif pickup.item is not None:
                        if pickup.item.item_id == "apple":
                            player.restore_hp(pickup.item.hp_restore)
                            pickup.kill()
                            audio.play_sound('pickup')
                        elif pickup.item.item_id == "health_potion":
                            player.restore_hp(pickup.item.hp_restore)
                            pickup.kill()
                            audio.play_sound('pickup')
                        elif pickup.item.item_id == "mana_potion":
                            player.restore_mana(pickup.item.mana_restore)
                            pickup.kill()
                            audio.play_sound('pickup')
                        else:
                            remaining = player.inventory.add_item(pickup.item)
                            if remaining == 0:
                                pickup.kill()
                                audio.play_sound('pickup')

            if player.hp <= 0:
                ui.show_game_over()
                audio.play_game_over()

        screen.fill(settings.COLORS.bg)
        world.draw(screen, camera)

        for pickup in pickups:
            screen.blit(pickup.image, pickup.rect.topleft - camera)
        for projectile in projectiles:
            projectile.draw(screen, camera)
        for splash in death_splashes:
            splash.draw(screen, camera)
        for blood in blood_splashes:
            blood.draw(screen, camera)
        for enemy in enemies:
            enemy.draw(screen, camera)
        player.draw(screen, camera)

        ui.draw_hud(screen, player)
        ui.draw_minimap(screen, world, player, enemies)
        ui.draw_level_up_notification(screen, dt)
        ui.draw_game_over(screen)
        ui.draw_inventory(screen, player, mouse_screen)

        pygame.display.flip()

    return True


if __name__ == "__main__":
    main()
