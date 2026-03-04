#!/usr/bin/env python3
"""
  ██╗    ██╗██╗ ██████╗██╗  ██╗██╗████████╗ █████╗
  ██║    ██║██║██╔════╝██║  ██║██║╚══██╔══╝██╔══██╗
  ██║ █╗ ██║██║██║     ███████║██║   ██║   ███████║
  ██║███╗██║██║██║     ██╔══██║██║   ██║   ██╔══██║
  ╚███╔███╔╝██║╚██████╗██║  ██║██║   ██║   ██║  ██║
   ╚══╝╚══╝ ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝

         An RPG Adventure of the 80's
         ==============================
"""

import sys
import random
from typing import List, Optional

from src.character import Player, EXP_TO_LEVEL
from src.items import Consumable, Weapon, Armor, SHOP_ITEMS
from src.combat import run_combat, CombatResult
from src.world import WORLD_MAP, TOWN, Location


# ---------------------------------------------------------------------------
# Simple text UI
# ---------------------------------------------------------------------------

class TextUI:
    def print(self, text: str = ""):
        print(text)

    def input(self, prompt: str = "") -> str:
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye, adventurer!")
            sys.exit(0)

    def choose(self, prompt: str, options: List[str]) -> str:
        """Present a numbered menu and return the chosen option text."""
        self.print(f"\n{prompt}")
        for i, opt in enumerate(options, 1):
            self.print(f"  {i}. {opt}")
        while True:
            raw = self.input("> ")
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            # Allow typing the option directly (case-insensitive)
            matches = [o for o in options if o.lower().startswith(raw.lower())]
            if len(matches) == 1:
                return matches[0]
            self.print("Invalid choice. Please enter a number.")

    def separator(self, char: str = "=", width: int = 50):
        self.print(char * width)

    def pause(self):
        self.input("\nPress ENTER to continue...")


# ---------------------------------------------------------------------------
# Helper display functions
# ---------------------------------------------------------------------------

def show_stats(player: Player, ui: TextUI):
    ui.separator()
    ui.print(f"  {player.name} the {player.char_class}  [Level {player.level}]")
    ui.separator("-")
    ui.print(f"  HP  : {player.hp}/{player.max_hp}")
    ui.print(f"  MP  : {player.mp}/{player.max_mp}")
    ui.print(f"  ATK : {player.total_attack}  (base {player.attack} + {player.inventory.attack_bonus})")
    ui.print(f"  DEF : {player.total_defense}  (base {player.defense} + {player.inventory.defense_bonus})")
    ui.print(f"  SPD : {player.speed}")
    ui.print(f"  EXP : {player.exp}")
    next_level = EXP_TO_LEVEL[player.level] if player.level < len(EXP_TO_LEVEL) else "MAX"
    ui.print(f"  Next: {next_level}")
    ui.print(f"  Gold: {player.inventory.gold}")
    ui.separator("-")
    weapon_name = player.inventory.weapon.name if player.inventory.weapon else "None"
    armor_name = player.inventory.armor.name if player.inventory.armor else "None"
    ui.print(f"  Weapon: {weapon_name}")
    ui.print(f"  Armor : {armor_name}")
    ui.separator()


def show_inventory(player: Player, ui: TextUI):
    items = player.inventory.list_items()
    ui.separator()
    ui.print("  INVENTORY")
    ui.separator("-")
    if not items:
        ui.print("  (empty)")
    else:
        for item in items:
            ui.print(f"  - {item.name}: {item.description}")
    ui.separator()


def use_item_menu(player: Player, ui: TextUI):
    consumables = [i for i in player.inventory.list_items() if isinstance(i, Consumable)]
    equippables = [i for i in player.inventory.list_items()
                   if isinstance(i, (Weapon, Armor))]
    if not consumables and not equippables:
        ui.print("You have nothing to use or equip.")
        return

    all_items = consumables + equippables
    item_options = [i.name for i in all_items] + ["Cancel"]
    choice = ui.choose("Use/Equip which item?", item_options)
    if choice == "Cancel":
        return

    idx = item_options.index(choice)
    item = all_items[idx]

    if isinstance(item, Consumable):
        msg = item.use(player)
        player.inventory.remove_item(item)
        ui.print(msg)
    elif isinstance(item, Weapon):
        msg = player.inventory.equip_weapon(item)
        ui.print(msg)
    elif isinstance(item, Armor):
        msg = player.inventory.equip_armor(item)
        ui.print(msg)


# ---------------------------------------------------------------------------
# Town actions
# ---------------------------------------------------------------------------

def visit_inn(player: Player, ui: TextUI):
    cost = 15
    ui.print(f"\nInnkeeper: 'A good night's rest costs {cost} gold, friend.'")
    if player.inventory.gold < cost:
        ui.print("You don't have enough gold.")
        return
    choice = ui.choose("Rest at the inn?", ["Yes", "No"])
    if choice == "Yes":
        player.inventory.gold -= cost
        player.hp = player.max_hp
        player.mp = player.max_mp
        ui.print("You rest and feel completely refreshed!")
    else:
        ui.print("You decide not to rest.")


def visit_shop(player: Player, ui: TextUI):
    ui.print(f"\nShopkeeper: 'Welcome! You have {player.inventory.gold} gold.'")
    while True:
        items = [i() for i in SHOP_ITEMS]
        options = [f"{i.name} - {i.price}g" for i in items] + ["Leave"]
        choice = ui.choose("What would you like to buy?", options)
        if choice == "Leave":
            break
        idx = options.index(choice)
        item = items[idx]
        if player.inventory.gold < item.price:
            ui.print("You don't have enough gold!")
        else:
            player.inventory.gold -= item.price
            msg = player.inventory.add_item(item)
            ui.print(msg)
            ui.print(f"Remaining gold: {player.inventory.gold}")


def visit_town(player: Player, ui: TextUI):
    ui.separator()
    ui.print(f"  {TOWN.name}")
    ui.separator("-")
    ui.print(TOWN.description)
    ui.separator()

    while True:
        action = ui.choose("What would you like to do?",
                           ["Visit Inn (rest)", "Visit Shop", "View Stats",
                            "View Inventory", "Use Item", "Leave Town"])
        if action == "Visit Inn (rest)":
            visit_inn(player, ui)
        elif action == "Visit Shop":
            visit_shop(player, ui)
        elif action == "View Stats":
            show_stats(player, ui)
        elif action == "View Inventory":
            show_inventory(player, ui)
        elif action == "Use Item":
            use_item_menu(player, ui)
        elif action == "Leave Town":
            break


# ---------------------------------------------------------------------------
# Exploration
# ---------------------------------------------------------------------------

def explore_location(player: Player, location: Location, ui: TextUI) -> bool:
    """
    Explore a location. Returns True if player is still alive.
    """
    ui.separator()
    ui.print(f"  {location.name}")
    ui.separator("-")
    ui.print(location.description)
    ui.separator()

    steps = 0
    while True:
        action = ui.choose("What do you do?",
                           ["Explore deeper", "Rest (use item)", "Return"])
        if action == "Return":
            return True

        elif action == "Rest (use item)":
            use_item_menu(player, ui)
            continue

        # Explore deeper
        steps += 1
        # Encounter chance scales from 60% up to 90% as the player explores deeper
        BASE_ENCOUNTER_CHANCE = 0.6
        STEP_INCREASE = 0.05
        MAX_INCREASE = 0.3
        encounter_chance = BASE_ENCOUNTER_CHANCE + min(steps * STEP_INCREASE, MAX_INCREASE)
        if random.random() < encounter_chance and location.enemy_pool:
            enemy = location.get_encounter()
            result, _ = run_combat(player, enemy, ui)
            if result == CombatResult.DEFEAT:
                return False
        else:
            loot_roll = random.random()
            if loot_roll < 0.25:
                gold = random.randint(5, 20) * player.level
                player.inventory.gold += gold
                ui.print(f"\nYou find {gold} gold on the ground!")
            elif loot_roll < 0.35:
                from src.items import HEALTH_POTION, MANA_POTION
                potion = HEALTH_POTION() if random.random() < 0.7 else MANA_POTION()
                msg = player.inventory.add_item(potion)
                ui.print(f"\nYou search the area and find something!")
                ui.print(msg)
            else:
                ui.print("\nYou explore further but find nothing of interest.")

        show_stats(player, ui)


# ---------------------------------------------------------------------------
# Character creation
# ---------------------------------------------------------------------------

def create_character(ui: TextUI) -> Player:
    ui.separator("=")
    ui.print("  CREATE YOUR CHARACTER")
    ui.separator("=")

    name = ""
    while not name:
        name = ui.input("Enter your hero's name: ")
        if not name:
            ui.print("A hero must have a name!")

    ui.print("\nChoose your class:")
    ui.print("  1. Warrior - Tough fighter, high HP and strength, low magic")
    ui.print("  2. Mage    - Frail but powerful, uses spells to devastate enemies")
    ui.print("  3. Rogue   - Quick and cunning, strikes from the shadows")

    class_choice = ui.choose("Your class:", ["Warrior", "Mage", "Rogue"])

    player = Player(name, class_choice)
    ui.separator()
    ui.print(f"  Welcome, {player.name} the {player.char_class}!")
    ui.print(f"  HP: {player.max_hp}  MP: {player.max_mp}")
    ui.print(f"  ATK: {player.total_attack}  DEF: {player.total_defense}  SPD: {player.speed}")
    if player.spells:
        spell_names = ", ".join(s.name for s in player.spells)
        ui.print(f"  Spells: {spell_names}")
    ui.separator()
    ui.pause()
    return player


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def title_screen(ui: TextUI):
    ui.print(__doc__)


def game_loop(ui: TextUI):
    title_screen(ui)
    choice = ui.choose("", ["New Game", "Quit"])
    if choice == "Quit":
        ui.print("Farewell, adventurer!")
        return

    player = create_character(ui)

    while player.is_alive:
        ui.separator("=")
        ui.print(f"  THE WORLD MAP  |  {player.name} Lv.{player.level}  HP:{player.hp}/{player.max_hp}")
        ui.separator("=")
        for loc in WORLD_MAP:
            tag = " [SAFE]" if loc.is_safe else f" [Lv.{loc.level_range[0]}-{loc.level_range[1]}]"
            ui.print(f"  - {loc.name}{tag}")
        ui.separator()

        destinations = [loc.name for loc in WORLD_MAP] + ["View Stats", "View Inventory", "Use Item", "Quit Game"]
        action = ui.choose("Where do you go?", destinations)

        if action == "Quit Game":
            ui.print("Farewell, adventurer!")
            break
        elif action == "View Stats":
            show_stats(player, ui)
        elif action == "View Inventory":
            show_inventory(player, ui)
        elif action == "Use Item":
            use_item_menu(player, ui)
        else:
            location = next(loc for loc in WORLD_MAP if loc.name == action)
            if location.is_safe:
                visit_town(player, ui)
            else:
                alive = explore_location(player, location, ui)
                if not alive:
                    ui.separator("=")
                    ui.print("  GAME OVER")
                    ui.print(f"  {player.name} has fallen in battle.")
                    ui.print(f"  Level reached: {player.level}")
                    ui.print(f"  EXP gained: {player.exp}")
                    ui.separator("=")
                    break

    if player.is_alive:
        ui.print("\nThanks for playing WICHITA!")


def main():
    ui = TextUI()
    game_loop(ui)


if __name__ == "__main__":
    main()
