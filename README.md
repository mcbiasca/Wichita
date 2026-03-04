# Wichita
An RPG game of the 80's

## Overview

**Wichita** is a classic text-based RPG inspired by the dungeon-crawlers and adventure games of the 1980s. Choose your hero, explore dangerous locations, fight monsters, collect treasure, and grow in power!

## Features

- **Three character classes**: Warrior, Mage, and Rogue — each with unique stats and abilities
- **Turn-based combat**: Attack, cast spells, use items, or attempt to flee
- **Spells**: Fireball, Ice Shard, Thunder, Heal (Mage), Backstab, Poison Strike (Rogue)
- **Item & inventory system**: Weapons, armor, potions, and more
- **Leveling system**: Gain EXP from battles to level up and grow stronger
- **World exploration**: Four locations — a safe town, a forest, caves, and a dragon's lair
- **Shop & inn**: Buy gear and rest to restore HP/MP

## Requirements

- Python 3.8+

## How to Play

```bash
python game.py
```

### Character Classes

| Class   | HP  | MP  | Strengths                        |
|---------|-----|-----|----------------------------------|
| Warrior | 80  | 10  | High HP, strong physical attacks |
| Mage    | 45  | 50  | Powerful spells, Heal ability    |
| Rogue   | 60  | 25  | High speed, Backstab & Poison    |

### Locations

| Location          | Level Range | Description                           |
|-------------------|-------------|---------------------------------------|
| Town of Wichita   | Safe        | Rest, shop, and prepare for adventure |
| Whispering Forest | 1–3         | Goblins, Wolves, Skeletons            |
| Dark Caves        | 3–6         | Orcs, Dark Mages, Cave Trolls         |
| Dragon's Lair     | 7+          | Black Knights and the mighty Dragon   |

## Running Tests

```bash
python -m pytest tests/ -v
```
