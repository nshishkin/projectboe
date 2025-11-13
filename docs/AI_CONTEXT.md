# BoE - AI Coding Guidelines

## Project Overview
Turn-based strategy game combining strategic map exploration with tactical combat.
Tech stack: Python 3.11+, Pygame
Target: Single-player, vertical slice prototype
You (model) acting as experienced programmer.  User is planniing development of turn-based game.  Game design document will be added below. Your task is to help user to preplan architecture of game. When developing architecture take notice what user is not experienced programmer, try to give simplest and more robust solution possible. Plan to keep code split in sizeble modules, not more than 300 lines. Techstack is Python and Pygame. If you need more information to plan architecture, you can ask 5-10 questions. When restarting session from scratch, read files in doc folder.

## Architecture Rules

### Module Organization
- Keep files under 300 lines
- One class per file (except small helper classes)
- Follow the structure in docs/architecture_plan.md
- Strategic layer in `strategic/`, tactical in `tactical/`, shared in `shared/`

### File Locations
- Core files (main.py, game.py, constants.py, data_definitions.py) in root
- Layer-specific files in respective folders
- Documentation in `docs/`
- Save files will go in root (save.json)

## Code Style

### Python Conventions
- Use Python 3.11+ features
- Type hints for function parameters and return values
- Docstrings for all classes and public methods (Google style)
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants

### Imports
- Group imports: standard library, third-party (pygame), local modules
- Use absolute imports from project root
- Avoid circular imports

Example:
```python
import json
from typing import Optional, Dict, List

import pygame

from constants import SCREEN_WIDTH
from strategic.province import Province
```

### Error Handling
- Use explicit error handling, don't silently fail
- Validate inputs at boundaries (user input, file loading)
- Raise exceptions for programmer errors
- Log warnings for recoverable issues

### Comments
- Explain WHY, not WHAT
- Document complex algorithms
- Mark TODOs with: # TODO: description
