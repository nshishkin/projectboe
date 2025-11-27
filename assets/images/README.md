# Game Sprites

## Folder Structure

```
images/
├── terrain/
│   ├── strategic/     # Hex tiles for strategic map (40px radius)
│   │   ├── plains.png
│   │   ├── forest.png
│   │   ├── swamp.png
│   │   └── hills.png
│   └── tactical/      # Hex tiles for tactical battlefield (30px radius)
│       ├── grass.png
│       ├── forest_ground.png
│       ├── dirt.png
│       └── stone.png
└── units/             # Unit sprites for tactical combat
    ├── infantry.png
    ├── cavalry.png
    └── ranged.png
```

## Sprite Requirements

### Terrain Tiles (Hexagonal)

**Strategic Map:**
- Size: ~80x80 pixels (fits 40px radius hex)
- Format: PNG with transparency
- Style: Top-down or isometric view

**Tactical Battlefield:**
- Size: ~60x60 pixels (fits 30px radius hex)
- Format: PNG with transparency
- Style: Should match strategic map style

### Unit Sprites

**Tactical Units:**
- Size: 48x48 to 64x64 pixels recommended
- Format: PNG with transparent background
- Style: Top-down or isometric view
- Should be centered and fit within hex

## How to Add Sprites

1. Place sprite files in appropriate folders
2. Use exact names matching terrain/unit types in game
3. The game will automatically load sprites using `sprite_loader.py`
4. If sprite not found, game falls back to colored circles/hexes

## Naming Convention

File names must match game definitions:
- Terrain: `plains.png`, `forest.png`, `swamp.png`, `hills.png`
- Units: `infantry.png`, `cavalry.png`, `ranged.png`
- Names are case-sensitive and lowercase
