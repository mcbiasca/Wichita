# Wizard ARPG Game

A Diablo-style action RPG built with Python and Pygame featuring a wizard protagonist battling goblins in a grass dungeon environment.

## Features

- **Wizard Character**: Purple-robed wizard with staff and magical abilities
- **Combat System**: 
  - Spell casting (B key)
  - Melee attacks (N key)
  - Bullet projectiles (Spacebar)
- **Enemy AI**: Green goblins with pathfinding
- **Procedural Graphics**: All graphics generated programmatically
- **Sound Effects**: 
  - Procedurally generated FX (shoot, hit, pickup, levelup, death, menu)
  - Woman scream when player takes damage
  - Game over sound with audio muting
- **Background Music**: Action theme with delayed looping
- **Environment**: 
  - Grass floors with stone tiles
  - 350 dungeon walls
  - 200 decorative props (barrels, rocks, bushes, flowers, mushrooms, crates)
- **Item System**: Collectible apples for health restoration
- **Save/Load**: F5 to save, F9 to load
- **Inventory**: Press I to toggle

## Requirements

- Python 3.13+
- Pygame
- NumPy

## Installation

```bash
pip install pygame numpy
```

## Controls

- **WASD**: Movement
- **Spacebar**: Shoot bullets
- **B**: Cast spell
- **N**: Melee attack
- **I**: Toggle inventory
- **F5**: Save game
- **F9**: Load game
- **ESC**: Quit

## Running the Game

```bash
python main.py
```

## Assets

Place audio files in the `assets/` folder:
- `Action.wav` - Background music
- `woman_scream.mp3` - Player damage sound
- `game_over.mp3` - Game over sound

## License

Created with GitHub Copilot
