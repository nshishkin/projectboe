# BoE (Battle of Empires) Project Architecture

## Overview
This document describes the project structure for the BoE game, a hybrid strategy game combining elements from Eador and Battle Brothers with both strategic and tactical gameplay layers.

## Directory Structure
```
projectboe/
├── main.py                 # Main game entry point
├── config/
│   ├── settings.py         # Game settings and constants
│   └── constants.py        # Global constants
├── game/
│   ├── __init__.py
│   ├── tactical/
│   │   ├── __init__.py
│   │   ├── grid.py         # Grid system for tactical combat
│   │   ├── unit.py         # Unit class and behaviors
│   │   └── combat.py       # Combat mechanics
│   ├── strategic/
│   │   ├── __init__.py
│   │   ├── map.py          # Strategic map with provinces
│   │   ├── province.py     # Province/node class
│   │   └── hero.py         # Hero movement and management
│   └── core/
│       ├── __init__.py
│       ├── game.py         # Main game class
│       ├── renderer.py     # Rendering system
│       └── state.py        # Game state management
├── assets/
│   ├── images/             # Sprites and textures
│   ├── sounds/             # Audio files
│   └── fonts/              # Font files
├── data/
│   ├── maps/               # Map data files
│   ├── units/              # Unit definitions
│   └── saves/              # Save game data
├── tests/                  # Unit tests
└── memory-bank/            # Documentation and design documents
    ├── game-design-document.md    # Core game design
    ├── ai-coding-workflow-guide.md # AI-assisted coding guide
    ├── tech-stack-recommendation.md # Technology choices
    └── architecture.md     # This document
```

## Core Components

### Main Entry Point (main.py)
- Initializes Pygame
- Sets up the main game loop
- Manages game state transitions
- Handles the primary game flow

### Configuration Module
- **settings.py**: Contains configurable game parameters like screen resolution, game speed, etc.
- **constants.py**: Immutable values used throughout the game (colors, dimensions, etc.)

### Game Module
Organized into three main submodules:

#### Tactical Layer
- **grid.py**: Implements the grid system for tactical combat
- **unit.py**: Defines unit properties, behaviors, and interactions
- **combat.py**: Handles combat mechanics, damage calculation, and battle resolution

#### Strategic Layer
- **map.py**: Manages the strategic map with province nodes
- **province.py**: Defines province properties and interactions
- **hero.py**: Handles hero movement, abilities, and management

#### Core System
- **game.py**: Main game class that orchestrates all components
- **renderer.py**: Handles all rendering operations
- **state.py**: Manages game states (tactical, strategic, menu, etc.)

### Assets Module
- Organized by media type for easy management
- Contains all game assets like sprites, sounds, and fonts
### Data Module
- **maps/**: Contains map definitions and generation data
- **units/**: Unit definitions and configuration files
- **saves/**: Save game data for both strategic and tactical layers


### Tests Module
- Unit tests for all major components
- Integration tests for game systems

### Memory Bank Module
- Contains all design documents and architectural information
- Serves as the project's knowledge base

## Key Design Patterns

### State Pattern
Used for managing different game states (strategic view, tactical combat, menus).

### Observer Pattern
Used for UI updates when game state changes.

### Factory Pattern
Used for creating different types of units and provinces.

## Technology Stack
- **Primary Framework**: Pygame
- **Additional Libraries**: PyTMX, NumPy, Pillow, SQLite
- **Languages**: Python

This architecture supports the hybrid nature of the game by clearly separating the strategic and tactical layers while providing a common core for shared functionality.