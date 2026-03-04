"""Unit tests for the Wichita RPG game."""

import sys
import os
import random
import unittest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.items import (
    Consumable, Weapon, Armor, Inventory,
    HEALTH_POTION, MANA_POTION, ELIXIR,
    RUSTY_SWORD, IRON_SWORD, LEATHER_ARMOR,
)
from src.character import Player, Enemy, create_enemy, EXP_TO_LEVEL, CLASS_BASE_STATS
from src.combat import run_combat, CombatResult, display_combat_status
from src.world import WORLD_MAP, TOWN, WHISPERING_FOREST, DARK_CAVES


# ---------------------------------------------------------------------------
# Items tests
# ---------------------------------------------------------------------------

class TestItems(unittest.TestCase):

    def test_health_potion_restores_hp(self):
        player = Player("Test", "Warrior")
        player.hp = 10
        potion = HEALTH_POTION()
        msg = potion.use(player)
        self.assertGreater(player.hp, 10)
        self.assertIn("recovers", msg)

    def test_health_potion_does_not_exceed_max_hp(self):
        player = Player("Test", "Warrior")
        player.hp = player.max_hp - 5
        potion = HEALTH_POTION()
        potion.use(player)
        self.assertEqual(player.hp, player.max_hp)

    def test_mana_potion_restores_mp(self):
        player = Player("Test", "Mage")
        player.mp = 0
        potion = MANA_POTION()
        msg = potion.use(player)
        self.assertGreater(player.mp, 0)

    def test_elixir_restores_both(self):
        player = Player("Test", "Mage")
        player.hp = 1
        player.mp = 0
        elixir = ELIXIR()
        msg = elixir.use(player)
        self.assertGreater(player.hp, 1)
        self.assertGreater(player.mp, 0)

    def test_weapon_attack_bonus(self):
        sword = IRON_SWORD()
        self.assertGreater(sword.attack_bonus, 0)

    def test_armor_defense_bonus(self):
        armor = LEATHER_ARMOR()
        self.assertGreater(armor.defense_bonus, 0)

    def test_inventory_equip_weapon(self):
        inv = Inventory()
        sword = IRON_SWORD()
        inv.add_item(sword)
        msg = inv.equip_weapon(sword)
        self.assertEqual(inv.weapon, sword)
        self.assertNotIn(sword, inv.items)
        self.assertIn("+", msg)

    def test_inventory_equip_armor(self):
        inv = Inventory()
        armor = LEATHER_ARMOR()
        inv.add_item(armor)
        inv.equip_armor(armor)
        self.assertEqual(inv.armor, armor)

    def test_inventory_equip_swaps_old_weapon(self):
        old_sword = Weapon("Old Sword", "A worn blade.", 0, attack_bonus=3)
        inv = Inventory(weapon=old_sword)
        new_sword = IRON_SWORD()
        inv.add_item(new_sword)
        inv.equip_weapon(new_sword)
        self.assertEqual(inv.weapon, new_sword)
        self.assertIn(old_sword, inv.items)

    def test_inventory_gold(self):
        inv = Inventory(gold=100)
        self.assertEqual(inv.gold, 100)
        inv.gold += 50
        self.assertEqual(inv.gold, 150)

    def test_attack_defense_bonus_properties(self):
        inv = Inventory()
        self.assertEqual(inv.attack_bonus, 0)
        self.assertEqual(inv.defense_bonus, 0)
        sword = IRON_SWORD()
        inv.add_item(sword)
        inv.equip_weapon(sword)
        self.assertGreater(inv.attack_bonus, 0)


# ---------------------------------------------------------------------------
# Character tests
# ---------------------------------------------------------------------------

class TestCharacter(unittest.TestCase):

    def test_warrior_creation(self):
        player = Player("Hero", "Warrior")
        self.assertEqual(player.char_class, "Warrior")
        self.assertEqual(player.level, 1)
        stats = CLASS_BASE_STATS["Warrior"]
        self.assertEqual(player.max_hp, stats["max_hp"])

    def test_mage_creation(self):
        player = Player("Wizard", "Mage")
        self.assertEqual(player.char_class, "Mage")
        self.assertGreater(len(player.spells), 0)

    def test_rogue_creation(self):
        player = Player("Shadow", "Rogue")
        self.assertEqual(player.char_class, "Rogue")
        self.assertGreater(len(player.spells), 0)

    def test_player_total_attack_includes_weapon(self):
        player = Player("Hero", "Warrior")
        base = player.attack
        sword = IRON_SWORD()
        player.inventory.add_item(sword)
        player.inventory.equip_weapon(sword)
        self.assertEqual(player.total_attack, base + sword.attack_bonus)

    def test_player_take_damage(self):
        player = Player("Hero", "Warrior")
        initial_hp = player.hp
        player.take_damage(20)
        self.assertLess(player.hp, initial_hp)

    def test_player_hp_not_negative(self):
        player = Player("Hero", "Warrior")
        player.take_damage(10000)
        self.assertEqual(player.hp, 0)
        self.assertFalse(player.is_alive)

    def test_player_is_alive(self):
        player = Player("Hero", "Warrior")
        self.assertTrue(player.is_alive)
        player.hp = 0
        self.assertFalse(player.is_alive)

    def test_gain_exp_and_level_up(self):
        player = Player("Hero", "Warrior")
        old_max_hp = player.max_hp
        msgs = player.gain_exp(EXP_TO_LEVEL[1])
        self.assertEqual(player.level, 2)
        self.assertGreater(player.max_hp, old_max_hp)
        self.assertTrue(any("LEVEL UP" in m for m in msgs))

    def test_gain_exp_no_level_up(self):
        player = Player("Hero", "Warrior")
        msgs = player.gain_exp(10)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.exp, 10)

    def test_create_enemy_goblin(self):
        enemy = create_enemy("Goblin")
        self.assertEqual(enemy.name, "Goblin")
        self.assertGreater(enemy.max_hp, 0)
        self.assertTrue(enemy.is_alive)

    def test_create_enemy_dragon(self):
        enemy = create_enemy("Dragon")
        self.assertEqual(enemy.name, "Dragon")
        self.assertGreater(enemy.max_hp, 50)

    def test_create_enemy_invalid(self):
        with self.assertRaises(ValueError):
            create_enemy("NotAnEnemy")

    def test_enemy_basic_attack_reduces_player_hp(self):
        player = Player("Hero", "Warrior")
        enemy = create_enemy("Goblin")
        initial_hp = player.hp
        enemy.basic_attack(player)
        self.assertLess(player.hp, initial_hp)

    def test_player_basic_attack_reduces_enemy_hp(self):
        player = Player("Hero", "Warrior")
        enemy = create_enemy("Goblin")
        initial_hp = enemy.hp
        player.basic_attack(enemy)
        self.assertLess(enemy.hp, initial_hp)

    def test_starting_gold(self):
        player = Player("Hero", "Warrior")
        self.assertGreater(player.inventory.gold, 0)


# ---------------------------------------------------------------------------
# Spell tests
# ---------------------------------------------------------------------------

class TestSpells(unittest.TestCase):

    def test_fireball_damages_enemy(self):
        player = Player("Wizard", "Mage")
        enemy = create_enemy("Goblin")
        fireball = next(s for s in player.spells if s.name == "Fireball")
        initial_hp = enemy.hp
        initial_mp = player.mp
        msg = fireball.apply(player, enemy)
        self.assertLess(enemy.hp, initial_hp)
        self.assertLess(player.mp, initial_mp)

    def test_spell_insufficient_mp(self):
        player = Player("Wizard", "Mage")
        enemy = create_enemy("Goblin")
        fireball = next(s for s in player.spells if s.name == "Fireball")
        player.mp = 0
        initial_hp = enemy.hp
        msg = fireball.apply(player, enemy)
        self.assertEqual(enemy.hp, initial_hp)
        self.assertIn("Not enough MP", msg)

    def test_heal_spell_restores_hp(self):
        player = Player("Wizard", "Mage")
        heal = next(s for s in player.spells if s.name == "Heal")
        player.hp = player.max_hp // 2
        initial_hp = player.hp
        heal.apply(player, player)
        self.assertGreater(player.hp, initial_hp)


# ---------------------------------------------------------------------------
# Combat tests
# ---------------------------------------------------------------------------

class ScriptedUI:
    """A test double for TextUI that provides scripted responses and records output."""

    def __init__(self, choices):
        self.choices = list(choices)
        self.output = []

    def print(self, text=""):
        self.output.append(str(text))

    def input(self, prompt=""):
        return ""

    def choose(self, prompt, options):
        if self.choices:
            return self.choices.pop(0)
        return options[0]

    def pause(self):
        pass


class TestCombat(unittest.TestCase):

    def test_victory_when_player_stronger(self):
        random.seed(42)
        player = Player("Hero", "Warrior")
        # Boost player to guarantee victory
        player.attack = 100
        player.level = 10
        enemy = create_enemy("Goblin")
        ui = ScriptedUI(["Attack"] * 10)
        result, log = run_combat(player, enemy, ui)
        self.assertEqual(result, CombatResult.VICTORY)

    def test_defeat_when_enemy_stronger(self):
        random.seed(1)
        player = Player("Hero", "Warrior")
        player.hp = 1
        enemy = create_enemy("Dragon")
        # Dragon attacks first eventually since player always attacks
        ui = ScriptedUI(["Attack"] * 10)
        result, log = run_combat(player, enemy, ui)
        self.assertEqual(result, CombatResult.DEFEAT)

    def test_combat_uses_item(self):
        random.seed(42)
        player = Player("Hero", "Warrior")
        player.attack = 100
        player.level = 5
        enemy = create_enemy("Goblin")
        # First action: Items, then use potion, then Attack to finish
        ui = ScriptedUI(["Items", "Health Potion", "Attack"] * 5)
        result, log = run_combat(player, enemy, ui)
        self.assertIn(result, [CombatResult.VICTORY, CombatResult.DEFEAT, CombatResult.RAN])

    def test_display_combat_status(self):
        player = Player("Hero", "Warrior")
        enemy = create_enemy("Goblin")
        status = display_combat_status(player, enemy)
        self.assertIn("MP", status)
        self.assertIn("Goblin", status)
        self.assertIn("Hero", status)

    def test_exp_gained_after_victory(self):
        random.seed(42)
        player = Player("Hero", "Warrior")
        player.attack = 200
        player.level = 5
        goblin = create_enemy("Goblin")
        expected_exp = goblin.exp_reward
        ui = ScriptedUI(["Attack"] * 10)
        run_combat(player, goblin, ui)
        self.assertEqual(player.exp, expected_exp)

    def test_gold_gained_after_victory(self):
        random.seed(42)
        player = Player("Hero", "Warrior")
        player.attack = 200
        player.level = 5
        goblin = create_enemy("Goblin")
        gold_reward = goblin.gold_reward
        initial_gold = player.inventory.gold
        ui = ScriptedUI(["Attack"] * 10)
        run_combat(player, goblin, ui)
        self.assertEqual(player.inventory.gold, initial_gold + gold_reward)


# ---------------------------------------------------------------------------
# World tests
# ---------------------------------------------------------------------------

class TestWorld(unittest.TestCase):

    def test_town_is_safe(self):
        self.assertTrue(TOWN.is_safe)
        self.assertEqual(TOWN.enemy_pool, [])

    def test_forest_has_enemies(self):
        self.assertGreater(len(WHISPERING_FOREST.enemy_pool), 0)
        self.assertFalse(WHISPERING_FOREST.is_safe)

    def test_caves_has_enemies(self):
        self.assertGreater(len(DARK_CAVES.enemy_pool), 0)

    def test_world_map_has_locations(self):
        self.assertGreaterEqual(len(WORLD_MAP), 4)

    def test_location_get_encounter(self):
        encounter = WHISPERING_FOREST.get_encounter()
        self.assertIsNotNone(encounter)
        self.assertTrue(encounter.is_alive)

    def test_town_no_encounter(self):
        for _ in range(20):
            encounter = TOWN.random_encounter()
            self.assertIsNone(encounter)


if __name__ == "__main__":
    unittest.main(verbosity=2)
