# Battle of Empires (BoE)

A hybrid strategy game combining elements from Eador and Battle Brothers, featuring both strategic and tactical gameplay layers.

## Project Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setting up the Virtual Environment

A virtual environment is recommended to manage dependencies for this project without interfering with other Python projects on your system.

1. Open a command prompt or terminal in the project directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

After setting up the virtual environment and installing dependencies:

1. Make sure your virtual environment is activated.
2. Run the game:
   ```bash
   python main.py
   ```

### Controls

- ESC: Quit the game
- M: Switch to Menu state (when in Strategic or Tactical state)
- S: Switch to Strategic state (when in Menu or Tactical state)
- T: Switch to Tactical state (when in Menu or Strategic state)

## Project Structure

- `main.py`: Main entry point for the game
- `config/`: Game settings and constants
  - `settings.py`: Configurable game parameters
  - `constants.py`: Immutable values used throughout the game
- `game/`: Game logic modules
 - `core/`: Core systems including state management
  - `strategic/`: Strategic layer components
 - `tactical/`: Tactical layer components
- `assets/`: Game assets (images, sounds, fonts)
- `data/`: Game data (maps, units, saves)
- `tests/`: Unit tests
- `memory-bank/`: Documentation and design documents

## Dependencies

- pygame: 2D game development library
- pytmx: For handling tile maps
- numpy: For efficient map generation and calculations
- Pillow: For image processing and asset management

## Development

This project follows the implementation plan outlined in `memory-bank/implementation-plan.md`. The architecture is described in `memory-bank/architecture.md`.

## Contributing

Please read through the game design document in `memory-bank/game-design-document.md` to understand the vision for the game before making significant changes.
