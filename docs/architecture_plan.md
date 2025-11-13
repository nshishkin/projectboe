# BoE - Game Architecture Plan

## High-Level Architecture

The game follows a **layered state machine** architecture with clear separation between:
- **Game States** (Menu → Strategic → Tactical → Results)
- **Data Layer** (definitions, game state)
- **Logic Layer** (game rules, AI)
- **Presentation Layer** (rendering, input)

```
┌─────────────────────────────────────────┐
│         main.py (Entry Point)           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      game.py (Game State Machine)       │
│  Manages state transitions & main loop  │
└──┬───────────────────────────────────┬──┘
   │                                   │
   │  ┌────────────────────────────┐   │
   ├──► Strategic Layer            │   │
   │  │ - map_generator.py         │   │
   │  │ - province.py              │   │
   │  │ - hero.py                  │   │
   │  │ - strategic_state.py       │   │
   │  └────────────────────────────┘   │
   │                                   │
   │  ┌────────────────────────────┐   │
   └──► Tactical Layer              │   │
      │ - battlefield.py           │   │
      │ - combat_unit.py           │   │
      │ - combat_ai.py             │   │
      │ - tactical_state.py        │   │
      └────────────────────────────┘   │
                                       │
      ┌────────────────────────────┐   │
      │ Shared Systems             │◄──┘
      │ - constants.py             │
      │ - data_definitions.py      │
      │ - renderer.py              │
      │ - input_handler.py         │
      │ - save_system.py           │
      │ - utils.py                 │
      └────────────────────────────┘
```

---

## Module List

### Core Files
1. **main.py** - Entry point, initializes Pygame and runs game loop
2. **game.py** - State machine that controls transitions between menu/strategic/tactical states
3. **constants.py** - Screen dimensions, colors, grid sizes, default stats
4. **data_definitions.py** - Content definitions (terrain types, unit types, races, equipment)

### Strategic Layer
5. **strategic_state.py** - Manages strategic game state, hero movement, triggers combat
6. **map_generator.py** - Generates 8x8 province grid with terrain and races
7. **province.py** - Single province with terrain, race, encounters, exploration status
8. **hero.py** - Hero position, army composition, inventory, movement

### Tactical Layer
9. **tactical_state.py** - Manages turn-based combat, victory conditions, retreat/auto-resolve
10. **battlefield.py** - 10x16 tactical grid, terrain generation, unit placement
11. **combat_unit.py** - Combat unit with HP, position, stats, attack/defend logic
12. **combat_ai.py** - Basic enemy AI for target selection and movement

### Shared Systems
13. **renderer.py** - Pygame rendering (strategic map, battlefield, UI, colored squares/circles)
14. **input_handler.py** - Mouse/keyboard input processing, coordinate conversion
15. **save_system.py** - JSON save/load for strategic state only
16. **utils.py** - Helper functions (distance, pathfinding, general utilities)

---

## Data Flow

### Starting New Game
```
main.py
  → game.py creates StrategicState
    → MapGenerator.generate() creates provinces
    → Hero created at starting position
    → renderer.draw_strategic_map() displays map
```

### Hero Movement on Strategic Map
```
Player clicks province
  → input_handler returns {'action': 'move', 'target': (x,y)}
  → strategic_state.move_hero(x, y)
    → hero.move_to(x, y) validates and updates position
    → province.explore() reveals province
    → province.get_encounter() may return enemy army
      → If enemy exists: strategic_state.start_combat()
```

### Transitioning to Tactical Combat
```
strategic_state.start_combat(province)
  → Prepares combat data:
    - player_army = hero.get_army_data()
    - enemy_army = province.get_encounter()
    - terrain = province.terrain_type
  → game.change_state('tactical')
    → Creates TacticalState(player_army, enemy_army, terrain)
      → battlefield.generate_terrain()
      → battlefield.place_units()
      → Initialize turn order by initiative
```

### Tactical Combat Turn
```
Player's turn:
  → input_handler.get_tactical_input() returns action
  → tactical_state.execute_turn(selected_unit, action)

Enemy turn:
  → For each enemy unit:
    → combat_ai.get_action(unit) returns AI decision
    → tactical_state.execute_turn(unit, action)

After each turn:
  → tactical_state.check_victory()
    → If victory/defeat: return to strategic with results
```

### Returning to Strategic Layer
```
Combat ends (victory/defeat/retreat)
  → tactical_state returns result dict:
    {
      'outcome': 'victory'/'defeat'/'retreat',
      'surviving_units': [...],
      'experience_gained': 100,
      'losses': 2
    }
  → game.change_state('strategic')
  → strategic_state applies results:
    → hero.army updated with survivors
    → province conquered (if victory)
```

### Save/Load
```
Save:
  → strategic_state.save_state() returns dict
  → save_system.save_game(state_dict)
  → Writes JSON to disk

Load:
  → save_system.load_game() returns dict
  → strategic_state.load_state(dict)
    → Recreates map, hero, provinces from data
```

---

## Key Design Principles

1. **State Machine Pattern** - Clean separation between game modes (menu/strategic/tactical)
2. **Data-Driven Design** - All content in data_definitions.py for easy balancing
3. **Grid-Based** - Both strategic (8x8) and tactical (10x16) use simple grid systems
4. **Minimal Dependencies** - Only Pygame required, pure Python data structures
5. **Strategic-Only Saves** - Simpler implementation, combat can restart if interrupted
6. **Module Size** - Each file <300 lines for maintainability

---

## Project Structure
```
boe/
├── main.py
├── game.py
├── constants.py
├── data_definitions.py
├── strategic/
│   ├── strategic_state.py
│   ├── map_generator.py
│   ├── province.py
│   └── hero.py
├── tactical/
│   ├── tactical_state.py
│   ├── battlefield.py
│   ├── combat_unit.py
│   └── combat_ai.py
└── shared/
    ├── renderer.py
    ├── input_handler.py
    ├── save_system.py
    └── utils.py
```
