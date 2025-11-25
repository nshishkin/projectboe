# Game Hotkeys

## Save/Load System (Strategic Map)

| Key | Action | File | Description |
|-----|--------|------|-------------|
| **F5** | Quicksave | `saves/save2.json` | Manual save |
| **F6** | Load autosave (combat) | `saves/save0.json` | Load state before combat |
| **F7** | Load autosave (turn) | `saves/save1.json` | Load state at turn start |
| **F9** | Quickload | `saves/save2.json` | Load quicksave |

## Autosaves

Autosaves are created automatically:
- **save0.json** - Created before entering combat
- **save1.json** - Created at the start of each new turn

## Other Controls

### Strategic Map
- **Space** - Start game (from menu)
- **ESC** - Return to menu
- **Mouse Click** - Move hero to province
- **End Turn button** - Advance to next turn
- **Start Combat button** - Trigger test combat

### Tactical Combat
- **ESC** - Skip current animation / Return to strategic map
- **Mouse Click** - Select unit / Move / Attack
- **ALT + Hover** - View enemy stats (hold ALT)
- **ALT + Click** - Lock enemy stats display
- **Mouse Wheel** - Scroll combat log
- **End Turn button** - End current unit's turn

## Tips

1. **Before risky combat**: Press F5 to create a quicksave
2. **Want to retry combat**: Press F6 to load pre-combat state
3. **Made a mistake on turn**: Press F7 to reload turn start
4. **Quick reload**: Press F9 to load your last quicksave
