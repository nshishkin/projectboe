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
9. **tactical_state.py** - Manages turn-based combat, victory conditions, animation queue, combat log
10. **tactical_renderer.py** - Handles all tactical rendering (battlefield, units, UI, combat log)
11. **tactical_input.py** - Processes tactical input (mouse clicks, wheel scrolling, button interactions)
12. **battlefield.py** - 10x16 tactical grid, terrain generation, unit placement
13. **combat_unit.py** - Combat unit with HP, position, stats, display coordinates, attack/defend logic
14. **combat_ai.py** - Priority-based enemy AI for target selection and movement
15. **animation.py** - Animation system (MoveAnimation, AttackAnimation, AnimationQueue)
16. **hex_geometry.py** - Hex coordinate conversions (pixel ↔ grid) and distance calculations

### Shared Systems
17. **sprite_loader.py** - Centralized sprite loading with caching (terrain, units, strategic objects)
18. **renderer.py** - Pygame rendering for strategic map (battlefield now uses tactical_renderer.py)
19. **input_handler.py** - Mouse/keyboard input for strategic map (hex coordinate conversion)
20. **save_system.py** - JSON save/load for strategic state only
21. **utils.py** - Helper functions (distance, pathfinding, general utilities)

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
  → tactical_input.handle_click(mouse_pos) processes click
    → Converts pixel to hex coordinates via hex_geometry.pixel_to_hex()
    → If clicking enemy: tactical_state._execute_attack()
      → Creates AttackAnimation and adds to animation_queue
      → Deducts action points, calculates damage
    → If clicking empty hex: tactical_state._move_unit()
      → Uses BFS pathfinding to get path
      → Creates chain of MoveAnimation for each step
      → Deducts action points based on distance

Enemy turn:
  → For each enemy unit:
    → combat_ai.choose_action(unit, battlefield, targets) returns AI decision
    → tactical_state executes action with animations
    → Logs action to combat log

Animation playback:
  → tactical_state.update(dt) processes animation queue
  → animation_queue.update(dt) interpolates display positions
  → Units have separate display_x/y from grid x/y for smooth movement
  → Click during animation skips current animation

After each turn:
  → tactical_state.check_victory()
    → If victory/defeat: show victory window, return to strategic with results
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

## Animation System Architecture

The tactical combat layer uses a sequential animation queue system for smooth visual feedback.

### Animation Components

**Base Animation Class**
- Abstract base with `update(dt)` and `is_finished()` methods
- Delta time based for frame-rate independence
- Returns True when animation completes

**MoveAnimation**
- Interpolates unit from start (display_x, display_y) to target pixel position
- Speed configurable (default: 3 hexes/sec)
- Supports explicit start positions for animation chaining
- Calculates duration based on pixel distance and hex size

**AttackAnimation**
- Shifts unit toward target by TACTICAL_ATTACK_OFFSET pixels (25px)
- Two-phase: move toward target, then return to original position
- Fixed duration (default: 0.25s total)
- Uses `attack_phase` to track forward/backward movement

**AnimationQueue**
- Sequential playback of animations (FIFO queue)
- Only one animation plays at a time
- Supports skipping current animation on user click
- Updates current animation with delta time each frame

### Display Coordinate System

Units maintain two sets of coordinates:
- **Grid coordinates (x, y)**: Logical position on battlefield, updated immediately
- **Display coordinates (display_x, display_y)**: Visual position, interpolated by animations

This separation allows:
- Instant game logic updates (pathfinding, range checks)
- Smooth visual transitions without blocking gameplay
- Multi-step movement with chained animations

### Multi-Hex Movement

When a unit moves multiple hexes:
1. BFS pathfinding calculates complete path
2. For each hex in path, create MoveAnimation with explicit start position
3. Chain animations in queue (second starts where first ends)
4. Update logical position immediately, display position animates

Example:
```python
prev_x, prev_y = unit.display_x, unit.display_y
for step_x, step_y in path:
    target_pixel_x, target_pixel_y = hex_to_pixel(step_x, step_y)
    anim = MoveAnimation(unit, target_pixel_x, target_pixel_y, speed, prev_x, prev_y)
    animation_queue.add(anim)
    prev_x, prev_y = target_pixel_x, target_pixel_y
```

### Hex Coordinate System

Both strategic and tactical layers now use **even-q vertical layout** (flat-top hexagons):
- Even columns (x % 2 == 0) offset downward by hex_height/2
- Horizontal spacing: `hex_width * 3/4` (75% of hex width)
- Includes battlefield offsets (BATTLEFIELD_OFFSET_X/Y = 50, 50)

**hex_geometry.py** provides:
- `hex_to_pixel(grid_x, grid_y)`: Grid → pixel center coordinates
- `pixel_to_hex(mouse_x, mouse_y)`: Mouse → grid coordinates (nearest neighbor)
- `calculate_hex_distance(x1, y1, x2, y2)`: Hex distance via cube coordinates
- `get_hex_corners(center_x, center_y)`: 6 corner points for rendering

### Animation Coordinate System

Units use a **dual coordinate system** for smooth animations:

**Logical Coordinates (unit.x, unit.y)**
- Grid position on battlefield (integer hex coordinates)
- Updated **immediately** when unit moves or attacks
- Used as **source of truth** for game logic, pathfinding, range checks

**Display Coordinates (unit.display_x, unit.display_y)**
- Visual position in pixels (float)
- Interpolated gradually by animations
- Synced with logical position when animations complete

**Key Design Principle:**
- Animations calculate start positions from **logical coordinates** via `hex_to_pixel(unit.x, unit.y)`
- This ensures animations always begin from the correct position, even when queued
- No reliance on `display_x/display_y` for animation initialization
- Prevents "teleportation" artifacts when chaining multiple moves/attacks

---

## Sprite Loading System

The game uses a centralized sprite loading system with automatic caching for performance.

### SpriteLoader Architecture

**Location:** `shared/sprite_loader.py`

**Features:**
- Singleton pattern via `get_sprite_loader()`
- Automatic caching with composite keys (path + size + rotation + color_key)
- Fallback to colored shapes if sprites not found
- Support for scaling, rotation, transparency, and horizontal flipping

### Sprite Organization

```
assets/images/
├── terrain/
│   ├── strategic/       # 40px radius hex tiles
│   │   ├── plains.png
│   │   ├── woods.png
│   │   ├── swamp.png
│   │   └── hills.png
│   └── tactical/        # 30px radius hex tiles
│       ├── plains.png
│       ├── woods.png
│       ├── swamp.png
│       └── hills.png
└── units/
    ├── strategic/       # Strategic map objects
    │   └── hero.png
    └── tactical/        # Combat unit sprites (48x48 - 64x64)
        ├── infantry.png
        ├── cavalry.png
        ├── ranged.png
        ├── archer.png
        └── spearman.png
```

### Loading Methods

**`load_terrain_sprite(terrain_type, layer, size, rotate)`**
- Loads terrain hex tiles for strategic or tactical layers
- Path: `terrain/{layer}/{terrain_type}.png`

**`load_tactical_unit_sprite(unit_type, size, flip_horizontal)`**
- Loads combat unit sprites with optional horizontal flip for enemies
- Path: `units/tactical/{unit_type}.png`
- Enemy units automatically flipped to face left

**`load_strategic_object(object_name, size, color_key)`**
- Loads hero and other strategic map objects
- Path: `units/strategic/{object_name}.png`
- Supports color key transparency

### Integration

**Tactical Renderer:**
- Loads unit sprites at `TACTICAL_HEX_SIZE * 1.5` (45px for 30px hex)
- Automatically flips enemy sprites: `flip_horizontal=not unit.is_player`
- Centered on unit's `display_x/display_y` coordinates

**Strategic State:**
- Loads hero sprite at 60x60 pixels
- Loads terrain sprites matching hex size (80x80)
- Centered on hex centers

---

## Key Design Principles

1. **State Machine Pattern** - Clean separation between game modes (menu/strategic/tactical)
2. **Data-Driven Design** - All content in data_definitions.py for easy balancing
3. **Grid-Based** - Both strategic (8x8) and tactical (10x16) use simple grid systems
4. **Minimal Dependencies** - Only Pygame required, pure Python data structures
5. **Strategic-Only Saves** - Simpler implementation, combat can restart if interrupted
6. **Module Size** - Each file <300 lines for maintainability (larger files split into renderer/input/state)
7. **Separation of Concerns** - Rendering, input, game logic, and geometry separated into dedicated modules
8. **Animation System** - Display coordinates separate from logical positions for smooth interpolation

---

## Project Structure
```
boe/
├── main.py
├── game.py
├── constants.py
├── data_definitions.py
├── config/
│   └── constants.py
├── strategic/
│   ├── strategic_state.py
│   ├── map_generator.py
│   ├── province.py
│   ├── hero.py
│   └── input_handler.py
├── tactical/
│   ├── tactical_state.py
│   ├── tactical_renderer.py      # NEW - Rendering logic
│   ├── tactical_input.py          # NEW - Input handling
│   ├── battlefield.py
│   ├── combat_unit.py
│   ├── combat_ai.py
│   ├── animation.py               # NEW - Animation system
│   └── hex_geometry.py            # NEW - Hex coordinate utilities
├── shared/
│   ├── sprite_loader.py           # Sprite loading with caching
│   ├── renderer.py                # Strategic map rendering
│   ├── save_system.py             # TODO
│   └── utils.py                   # TODO
├── assets/
│   └── images/
│       ├── terrain/               # Terrain hex tiles
│       │   ├── strategic/         # Strategic layer tiles
│       │   └── tactical/          # Tactical layer tiles
│       └── units/                 # Unit sprites
│           ├── strategic/         # Hero sprite
│           └── tactical/          # Combat unit sprites
└── docs/
    ├── architecture_plan.md
    ├── progress.md
    └── game_design.md
```