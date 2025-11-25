"""
Save/load system for strategic layer state.

Handles JSON serialization and file operations for game saves.
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


# Save slots configuration
SAVES_FOLDER = "saves"
SAVE_SLOTS = {
    'autosave_combat': 'save0.json',    # Before entering combat
    'autosave_turn': 'save1.json',      # At start of new turn
    'quicksave': 'save2.json',          # F5 quicksave
    'manual': 'save{}.json'             # save3.json, save4.json, etc.
}


def ensure_saves_folder():
    """Create saves folder if it doesn't exist."""
    Path(SAVES_FOLDER).mkdir(exist_ok=True)


def save_game(state_dict: Dict[str, Any], slot: str = 'quicksave', slot_number: Optional[int] = None) -> bool:
    """
    Save game state to JSON file.

    Args:
        state_dict: Dictionary containing game state
        slot: Save slot type ('autosave_combat', 'autosave_turn', 'quicksave', 'manual')
        slot_number: Slot number for manual saves (3, 4, 5, etc.)

    Returns:
        True if save successful, False otherwise
    """
    ensure_saves_folder()

    # Determine filename
    if slot == 'manual' and slot_number is not None:
        filename = SAVE_SLOTS['manual'].format(slot_number)
    else:
        filename = SAVE_SLOTS.get(slot, 'save2.json')

    filepath = os.path.join(SAVES_FOLDER, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, indent=2, ensure_ascii=False)
        print(f"Game saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving game to {filepath}: {e}")
        return False


def load_game(slot: str = 'quicksave', slot_number: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Load game state from JSON file.

    Args:
        slot: Save slot type ('autosave_combat', 'autosave_turn', 'quicksave', 'manual')
        slot_number: Slot number for manual saves (3, 4, 5, etc.)

    Returns:
        Dictionary containing game state, or None if load failed
    """
    # Determine filename
    if slot == 'manual' and slot_number is not None:
        filename = SAVE_SLOTS['manual'].format(slot_number)
    else:
        filename = SAVE_SLOTS.get(slot, 'save2.json')

    filepath = os.path.join(SAVES_FOLDER, filename)

    if not os.path.exists(filepath):
        print(f"Save file not found: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            state_dict = json.load(f)
        print(f"Game loaded from {filepath}")
        return state_dict
    except Exception as e:
        print(f"Error loading game from {filepath}: {e}")
        return None


def save_exists(slot: str = 'quicksave', slot_number: Optional[int] = None) -> bool:
    """
    Check if a save file exists.

    Args:
        slot: Save slot type
        slot_number: Slot number for manual saves

    Returns:
        True if save file exists, False otherwise
    """
    if slot == 'manual' and slot_number is not None:
        filename = SAVE_SLOTS['manual'].format(slot_number)
    else:
        filename = SAVE_SLOTS.get(slot, 'save2.json')

    filepath = os.path.join(SAVES_FOLDER, filename)
    return os.path.exists(filepath)


def list_saves() -> list[dict[str, Any]]:
    """
    List all available save files with metadata.

    Returns:
        List of save file info dicts with 'filename', 'slot', 'modified' keys
    """
    ensure_saves_folder()
    saves = []

    for filename in os.listdir(SAVES_FOLDER):
        if filename.endswith('.json') and filename.startswith('save'):
            filepath = os.path.join(SAVES_FOLDER, filename)
            try:
                modified = os.path.getmtime(filepath)
                saves.append({
                    'filename': filename,
                    'filepath': filepath,
                    'modified': modified
                })
            except Exception as e:
                print(f"Error reading save file {filename}: {e}")

    # Sort by modification time (newest first)
    saves.sort(key=lambda x: x['modified'], reverse=True)
    return saves
