Implementation Phases

  Phase 1: Foundation (Week 1)

  Goal: Get basic Pygame window and state machine working

  1. Create project structure (folders for modules)
  2. Implement main.py - Basic Pygame initialization
  3. Implement constants.py - All constant definitions
  4. Implement game.py - Basic state machine (just menu → strategic)
  5. Implement renderer.py - Draw colored rectangles and text
  6. Test: Window opens, can switch between placeholder states

  Files: main.py, game.py, constants.py, renderer.py

  ---
  Phase 2: Strategic Layer Basics (Week 2)

  Goal: Navigate hero on a generated map

  1. Implement data_definitions.py - Terrain types
  2. Implement province.py - Basic province class
  3. Implement map_generator.py - Simple 8x8 grid generation
  4. Implement hero.py - Hero with position
  5. Implement strategic_state.py - Map display and hero movement
  6. Implement input_handler.py - Click to move hero
  7. Test: Click provinces to move hero, terrain colors show

  Files: data_definitions.py, province.py, map_generator.py, hero.py, strategic_state.py, input_handler.py

  ---
  Phase 3: Tactical Layer Basics (Week 3)

  Goal: Basic combat working with placeholder units

  1. Implement combat_unit.py - Unit with HP and attack
  2. Implement battlefield.py - 10x16 grid with unit placement
  3. Implement tactical_state.py - Turn-based combat loop
  4. Add basic UI for selecting units and actions
  5. Implement simple attack mechanics (click unit → click target)
  6. Test: Can attack enemy units until one side is eliminated

  Files: combat_unit.py, battlefield.py, tactical_state.py

  ---
  Phase 4: AI and Combat Flow (Week 4) ✅ COMPLETED

  Goal: AI opponents and complete combat cycle

  1. ✅ Implement combat_ai.py - Basic enemy AI with priority-based targeting
  2. ✅ Add initiative system to tactical_state.py (was already implemented)
  3. ✅ Implement victory/defeat detection with auto-display window
  4. ✅ Add transition back to strategic layer after combat
  5. ✅ Implement new UI system (ALT+hover, ranged attacks, visual feedback)
  6. ✅ Add ranged attack support (4 hex range for ranged units)

  Files: combat_ai.py, tactical_state.py, combat_unit.py, constants.py

  Additional features implemented:
  - Priority-based AI (targets wounded, prioritizes ranged units, path-finding)
  - Auto-selection of active player unit
  - Visual indicators (green for movement, red for attackable enemies)
  - ALT+hover/click for viewing enemy stats
  - Automatic melee/ranged attack selection based on distance
  - Victory/defeat window with auto-display

  ---
  Phase 5: Animation System and Refactoring (Week 5) ✅ COMPLETED

  Goal: Add visual polish and improve code organization

  1. ✅ Implement animation.py - Animation system with MoveAnimation, AttackAnimation, AnimationQueue
  2. ✅ Add display coordinates to combat_unit.py for smooth interpolation
  3. ✅ Integrate animation queue into tactical_state.py with delta time
  4. ✅ Implement animation skipping (click during animation)
  5. ✅ Refactor tactical layer: separate rendering, input, and geometry modules
  6. ✅ Add combat logging system with scrollable message history
  7. ✅ Unify hex coordinate systems (even-q vertical layout for both strategic and tactical)
  8. ✅ Add hex_geometry.py - Centralized hex coordinate utilities
  9. ✅ Fix animation synchronization bugs (movement+attack, movement+movement)
  10. ✅ Implement sprite loading system with caching
  11. ✅ Add terrain and unit sprites for both strategic and tactical layers

  Files: animation.py, combat_unit.py, tactical_state.py, tactical_renderer.py, tactical_input.py, hex_geometry.py, sprite_loader.py, constants.py

  **Animation System:**
  - Configurable animation speeds (3 hexes/sec for movement, 0.25s for attacks)
  - Sequential animation queue with proper chaining for multi-hex movement
  - Dual coordinate system: logical (unit.x/y) for game logic, display (display_x/y) for visuals
  - Animation start positions calculated from logical coordinates via hex_to_pixel()
  - Prevents "teleportation" artifacts when chaining multiple actions

  **Refactoring & UI:**
  - TacticalRenderer class for separation of rendering logic (~400 lines)
  - TacticalInput class for input handling and button management
  - Combat log with automatic word wrapping and mouse wheel scrolling
  - Unit display names (e.g., "Party0 (Infantry)")
  - Debug controls (instant finish, hex coordinate display toggle)
  - Turn end logging with hex coordinates

  **Sprite System:**
  - SpriteLoader singleton with automatic caching
  - Support for terrain tiles (strategic 80x80, tactical 60x60)
  - Support for unit sprites (tactical 48-64px, strategic hero 60x60)
  - Automatic horizontal flip for enemy units
  - Fallback to colored shapes if sprites not found
  - Assets organized in assets/images/terrain and assets/images/units

  **Critical Bug Fixes:**
  - Fixed animation "teleportation" when enemy units start moving
  - Fixed turn order corruption when units die mid-combat
  - Fixed infinite recursion on player defeat
  - Fixed victory/defeat animation timing
  - Fixed coordinate system (corrected to even-q from odd-q)

  ---
  Phase 6: Save System and Encounters (Week 6) 🔄 IN PROGRESS

  Goal: Playable vertical slice with persistence

  **Current Status:**
  - Animation system fully polished and bug-free ✅
  - Sprite loading system implemented ✅
  - Tactical combat visually complete ✅
  - Ready to implement save system and encounters

  **Remaining Tasks:**
  1. ⏳ Implement save_system.py - JSON save/load
  2. ⏳ Add save/load to strategic_state.py
  3. ⏳ Implement encounter system - Generate encounters on map, trigger combat on movement
  4. ⏳ Implement utils.py - Pathfinding helpers (if needed)
  5. ⏳ Improve map generation (constraints, connectivity)
  6. ⏳ Add UI for retreat and auto-resolve options
  7. ⏳ Update hero.py army composition persistence
  8. ⏳ Test: Can play multiple sessions with save/load

  Files: save_system.py, utils.py, map_generator.py, province.py, strategic_state.py

  **Notes:**
  - Tactical layer is feature-complete and stable
  - All critical animation bugs resolved
  - Focus now shifts to strategic layer integration and persistence

  ---
  Phase 7: Content and Balance (Week 7)

  Goal: Expand content using data definitions

  1. Add more terrain types to data_definitions.py
  2. Add multiple unit types with different stats
  3. Add basic race/enemy variety
  4. Balance combat (adjust stats, damage formulas)
  5. Add experience/rewards system
  6. Test: Multiple playthroughs feel varied and balanced

  Files: Updates to data_definitions.py and related systems

  ---
  Key Design Decisions

  1. State Machine Pattern

  - Clean separation between game modes
  - Easy to add new states later (menu, game over, etc.)
  - Each state is self-contained with update/render/input methods

  2. Data-Driven Design

  - All content in data_definitions.py
  - Easy to balance without touching code
  - Can expand to JSON files later if needed

  3. Grid-Based Everything

  - Both strategic and tactical use grids
  - Simplifies rendering (just draw squares)
  - Easy collision and pathfinding

  4. Minimal Dependencies

  - Only Pygame required
  - No complex libraries or frameworks
  - Pure Python data structures

  5. Save Only Strategic Layer

  - Simpler save/load implementation
  - If combat is interrupted, can restart it
  - Strategic state captures everything important