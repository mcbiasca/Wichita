"""Turn-based combat system for the Wichita RPG."""

import random
from typing import List, Tuple

from src.character import Player, Enemy
from src.items import Consumable


class CombatResult:
    VICTORY = "victory"
    DEFEAT = "defeat"
    RAN = "ran"


def _separator(char: str = "-", width: int = 50) -> str:
    return char * width


def _status_bar(label: str, current: int, maximum: int, width: int = 20) -> str:
    filled = int(width * current / maximum) if maximum > 0 else 0
    bar = "[" + "#" * filled + "." * (width - filled) + "]"
    return f"{label:<6} {bar} {current}/{maximum}"


def display_combat_status(player: Player, enemy: Enemy) -> str:
    lines = [
        _separator(),
        _status_bar(player.name[:6], player.hp, player.max_hp),
        _status_bar("MP", player.mp, player.max_mp),
        _separator("~"),
        _status_bar(enemy.name[:6], enemy.hp, enemy.max_hp),
        _separator(),
    ]
    return "\n".join(lines)


def run_combat(player: Player, enemy: Enemy, ui) -> Tuple[str, List[str]]:
    """
    Run a full combat encounter.

    Args:
        player: The player character.
        enemy: The enemy to fight.
        ui: UI helper with print() and choose() methods.

    Returns:
        A tuple of (CombatResult, log_messages).
    """
    log: List[str] = []

    ui.print(f"\n*** A wild {enemy.name} appears! ***")

    while player.is_alive and enemy.is_alive:
        ui.print(display_combat_status(player, enemy))

        # Build action menu
        actions = ["Attack"]
        if player.spells:
            actions.append("Magic")
        consumables = [i for i in player.inventory.list_items() if isinstance(i, Consumable)]
        if consumables:
            actions.append("Items")
        actions.append("Run")

        choice = ui.choose("Your action:", actions)

        player_msg = ""
        if choice == "Attack":
            player_msg = player.basic_attack(enemy)

        elif choice == "Magic":
            spell_names = [f"{s.name} (MP:{s.mp_cost})" for s in player.spells]
            spell_names.append("Cancel")
            sc = ui.choose("Choose spell:", spell_names)
            if sc == "Cancel":
                continue
            spell_idx = spell_names.index(sc)
            spell = player.spells[spell_idx]
            player_msg = spell.apply(player, enemy)

        elif choice == "Items":
            item_names = [i.name for i in consumables]
            item_names.append("Cancel")
            ic = ui.choose("Use which item?", item_names)
            if ic == "Cancel":
                continue
            item_idx = item_names.index(ic)
            item = consumables[item_idx]
            player_msg = item.use(player)
            player.inventory.remove_item(item)

        elif choice == "Run":
            if random.random() < 0.5 + (player.speed - enemy.speed) * 0.05:
                ui.print("You successfully escaped!")
                log.append("Ran from battle.")
                return CombatResult.RAN, log
            else:
                player_msg = "Couldn't escape!"

        if player_msg:
            ui.print(player_msg)
            log.append(player_msg)

        if not enemy.is_alive:
            break

        # Enemy turn
        enemy_msg = enemy.choose_action(player)
        ui.print(enemy_msg)
        log.append(enemy_msg)

    if player.is_alive:
        ui.print(f"\nVictory! {enemy.name} has been defeated!")
        rewards = player.gain_exp(enemy.exp_reward)
        player.inventory.gold += enemy.gold_reward
        ui.print(f"Received {enemy.gold_reward} gold!")
        for msg in rewards:
            ui.print(msg)
        log.extend(rewards)
        return CombatResult.VICTORY, log
    else:
        ui.print("\nYou have been defeated...")
        return CombatResult.DEFEAT, log
