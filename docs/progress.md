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
  Phase 5: Polish and Save System (Week 5)

  Goal: Playable vertical slice

  1. Implement save_system.py - JSON save/load
  2. Add save/load to strategic_state.py
  3. Implement encounter system - Generate encounters on map, trigger combat on movement
  4. Implement utils.py - Pathfinding helpers (if needed)
  5. Improve map generation (constraints, connectivity)
  6. Add UI for retreat and auto-resolve options
  7. Update hero.py army composition persistence
  8. Polish rendering (better colors, unit info display)
  9. Test: Can play multiple sessions with save/load

  Files: save_system.py, utils.py, map_generator.py, province.py, strategic_state.py, polish across existing files

  ---
  Phase 6: Content and Balance (Week 6)

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