"""
Strategic state manager for the strategic map layer.
Handles map rendering, hero movement, and strategic gameplay.
"""
import pygame
import math

from strategic.map_generator import generate_map, get_province_at
from strategic.hero import Hero
from strategic.province import Province
from strategic.input_handler import pixel_to_hex, hex_to_pixel
from strategic.movement import get_reachable_cells
from config.data_definitions import TERRAIN_TYPES
from config.player_data import HERO_PRESETS
from config.enemy import ENEMY_PRESETS
from config.constants import (
    STRATEGIC_HEX_SIZE, MAP_ROWS, MAP_COLS,
    BG_COLOR, WHITE, BLACK, DARK_GRAY, SCREEN_HEIGHT,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH, UNIT_TYPES
)
from strategic import save_system
from shared.sprite_loader import get_sprite_loader

class StrategicState:
    def __init__(self, screen, game, scenario_preset: str = 'default'):
        """
        Initialize strategic state with map and hero.

        Args:
            screen: Pygame display surface to render to
            game: Reference to Game instance (for triggering combat)
            scenario_preset: Scenario preset key ('debug_player_win', 'debug_player_loss', 'debug_movement', 'default')
        """
        self.screen = screen
        self.game = game
        self.scenario_preset = scenario_preset
        self.map_grid = generate_map(MAP_ROWS, MAP_COLS)
        self.hero = Hero(0, 0)  # Start at top-left for now

        # Load hero's army from scenario preset
        self.hero.army = HERO_PRESETS.get(scenario_preset, HERO_PRESETS['default'])
        print(f"Loaded hero army preset '{scenario_preset}': {self.hero.army}")

        # Turn counter
        self.current_turn = 1

        # Movement tracking
        self.reachable_cells: dict[tuple[int, int], int] = {}  # Valid movement targets and distances
        self._calculate_reachable_cells()  # Calculate initial reachable cells

        # Debug mode for showing hex coordinates
        self.show_hex_coords = False

        # Load sprite loader
        self.sprite_loader = get_sprite_loader()

        # UI Buttons (positioned at bottom of screen)
        button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - 10
        self.end_turn_button = pygame.Rect(50, button_y, 150, BUTTON_HEIGHT)
        self.start_combat_button = pygame.Rect(220, button_y, 180, BUTTON_HEIGHT)
        self.show_coords_button = pygame.Rect(420, button_y, 200, BUTTON_HEIGHT)

        print(f"Strategic state initialized with {MAP_ROWS}x{MAP_COLS} map")
        # Debug: print all province centers
        # for row in self.map_grid:
        #     for province in row:
        #         center_x, center_y = hex_to_pixel(province.x, province.y)
        #         print(f"Province x{province.x},y{province.y},center is {center_x},{center_y}")
        
    def update(self):
        """Update strategic layer logic."""
        # Phase 2: Minimal logic
        # Phase 4+: Check for encounters, AI movement, etc.
        pass
        
    def _get_hex_corners(self, center_x: float, center_y: float) -> list[tuple[float, float]]:
        """
        Calculate 6 corner points of a hexagon.
        
        Args:
            center_x: X coordinate of hex center
            center_y: Y coordinate of hex center
        
        Returns:
            List of (x, y) tuples for the 6 corners
        """
        corners = []
        for i in range(6):
            angle = math.pi / 3 * i  # 60 degrees between each corner
            x = center_x + STRATEGIC_HEX_SIZE * math.cos(angle)
            y = center_y + STRATEGIC_HEX_SIZE * math.sin(angle)
            corners.append((x, y))
        return corners

    def _draw_province(self, province):
        """
        Draw a single province hexagon.

        Args:
            province: Province object to draw
        """
        # Get hex center position in pixels
        center_x, center_y = hex_to_pixel(province.x, province.y)
        # Get hexagon corner points
        corners = self._get_hex_corners(center_x, center_y)

        # Try to load terrain sprite
        hex_diameter = int(STRATEGIC_HEX_SIZE * 2)
        terrain_sprite = self.sprite_loader.load_terrain_sprite(
            province.terrain_type,
            'strategic',
            size=(hex_diameter, hex_diameter),
            rotate=30  # Convert corner-top hexes to flat-top
        )

        if terrain_sprite:
            # Draw sprite centered on hex
            sprite_rect = terrain_sprite.get_rect(center=(int(center_x), int(center_y)))
            self.screen.blit(terrain_sprite, sprite_rect)
        else:
            # Fallback: Draw filled hexagon with terrain color
            terrain_color = TERRAIN_TYPES[province.terrain_type]['color']
            pygame.draw.polygon(self.screen, terrain_color, corners)
        
        # Draw hexagon border (black outline)
        pygame.draw.polygon(self.screen, BLACK, corners, 2)

    def _draw_hero(self):
        """Draw hero marker on current province."""
        # Get hero position in pixels
        center_x, center_y = hex_to_pixel(self.hero.x, self.hero.y)

        # Draw hero as white circle with black border
        pygame.draw.circle(self.screen, WHITE, (int(center_x), int(center_y)), 15)
        pygame.draw.circle(self.screen, BLACK, (int(center_x), int(center_y)), 15, 2)

    def _draw_reachable_cells(self):
        """Draw green highlights on cells hero can move to."""
        for (x, y), distance in self.reachable_cells.items():
            center_x, center_y = hex_to_pixel(x, y)
            corners = self._get_hex_corners(center_x, center_y)

            # Draw semi-transparent green overlay
            alpha = 100 if distance == 1 else 60
            green_color = (0, 255, 0)

            # Create surface for transparency
            overlay = pygame.Surface((STRATEGIC_HEX_SIZE * 3, STRATEGIC_HEX_SIZE * 3), pygame.SRCALPHA)
            overlay_corners = [(cx - center_x + STRATEGIC_HEX_SIZE * 1.5,
                               cy - center_y + STRATEGIC_HEX_SIZE * 1.5)
                              for cx, cy in corners]
            pygame.draw.polygon(overlay, (*green_color, alpha), overlay_corners)

            # Blit to screen
            self.screen.blit(overlay, (int(center_x - STRATEGIC_HEX_SIZE * 1.5),
                                      int(center_y - STRATEGIC_HEX_SIZE * 1.5)))

    def _draw_hero_info_panel(self):
        """Draw hero information panel below the map, aligned with buttons."""
        # Panel dimensions
        panel_width = 220
        panel_height = 200

        # Position: right of the buttons, at bottom of screen
        panel_x = 640
        panel_y = SCREEN_HEIGHT - panel_height - 10

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 2)  # Border

        # Font for text (smaller for compact panel)
        title_font = pygame.font.Font(None, 28)
        text_font = pygame.font.Font(None, 20)

        y_offset = panel_y + 8

        # Hero title
        title_text = title_font.render("Hero", True, WHITE)
        self.screen.blit(title_text, (panel_x + 8, y_offset))
        y_offset += 30

        # Movement points
        movement_text = text_font.render(
            f"Movement: {self.hero.current_movement}/{self.hero.movement_points}",
            True, WHITE
        )
        self.screen.blit(movement_text, (panel_x + 8, y_offset))
        y_offset += 28

        # Army section
        army_title = text_font.render("Army:", True, WHITE)
        self.screen.blit(army_title, (panel_x + 8, y_offset))
        y_offset += 25

        # Count units by type
        unit_counts = {}
        for unit_type in self.hero.army:
            unit_counts[unit_type] = unit_counts.get(unit_type, 0) + 1

        # Draw unit list (compact)
        for unit_type, count in unit_counts.items():
            if unit_type in UNIT_TYPES:
                unit_name = UNIT_TYPES[unit_type]['name']
                unit_color = UNIT_TYPES[unit_type]['color']

                # Draw colored circle for unit type (smaller)
                circle_x = panel_x + 15
                circle_y = y_offset + 8
                pygame.draw.circle(self.screen, unit_color, (circle_x, circle_y), 6)
                pygame.draw.circle(self.screen, WHITE, (circle_x, circle_y), 6, 1)

                # Draw unit name and count
                unit_text = text_font.render(f"{unit_name} x{count}", True, WHITE)
                self.screen.blit(unit_text, (panel_x + 30, y_offset))
                y_offset += 25

    def render(self):
        """Render the strategic map, hero, and UI."""
        # Draw all provinces
        for row in self.map_grid:
            for province in row:
                self._draw_province(province)

        # Draw reachable cells (before hero so they're underneath)
        if self.reachable_cells:
            self._draw_reachable_cells()

        # Draw hero on top
        self._draw_hero()

        # Draw hex coordinates if enabled
        if self.show_hex_coords:
            self._draw_hex_coords()

        # Draw UI (buttons and turn counter)
        self._draw_ui()

        # Draw hero info panel
        self._draw_hero_info_panel()

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handle mouse click on the strategic map or UI buttons.

        Args:
            mouse_pos: Tuple of (x, y) mouse position in pixels
        """
        # Check button clicks first
        if self._handle_button_click(mouse_pos):
            return  # Button was clicked, don't process map click

        # Convert pixel position to hex grid coordinates
        grid_coords = pixel_to_hex(mouse_pos[0], mouse_pos[1])
        if grid_coords:
            grid_x, grid_y = grid_coords

            # Check if click is within reachable cells
            if (grid_x, grid_y) in self.reachable_cells:
                distance = self.reachable_cells[(grid_x, grid_y)]
                province = get_province_at(self.map_grid, grid_x, grid_y)

                # Move hero and consume movement points
                self.hero.move_to(grid_x, grid_y)
                self.hero.current_movement -= distance
                print(f"Moved to {province.terrain_type} at ({grid_x}, {grid_y}), {self.hero.current_movement} movement left")

                # Recalculate reachable cells
                self._calculate_reachable_cells()
            else:
                print(f"Cannot move to ({grid_x}, {grid_y}) - out of range")

    def _calculate_reachable_cells(self):
        """Calculate cells reachable by hero based on current movement points."""
        if self.hero.current_movement > 0:
            self.reachable_cells = get_reachable_cells(
                self.hero.x,
                self.hero.y,
                self.hero.current_movement,
                self.map_grid
            )
            print(f"Hero can reach {len(self.reachable_cells)} cells")
        else:
            self.reachable_cells.clear()
            print("Hero has no movement points left")

    def _trigger_test_combat(self, province):
        """
        Trigger test combat (Phase 3 only).

        Phase 4+: Replace with proper encounter system.

        Args:
            province: Province where combat happens
        """
        # Autosave before entering combat
        self.save_state('autosave_combat')
        print("[Autosave] Before combat")

        # Use predefined armies from data files
        player_army = HERO_ARMY
        enemy_army = TEST_ENEMY_ARMY

        # Start combat
        self.game.start_combat(player_army, enemy_army, province.terrain_type)

    def _draw_ui(self):
        """Draw UI elements (buttons and turn counter)."""
        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()

        # Draw turn counter at top
        font = pygame.font.Font(None, 36)
        turn_text = font.render(f"Turn: {self.current_turn}", True, WHITE)
        self.screen.blit(turn_text, (50, 10))

        # Draw buttons with hover effect
        self._draw_button(self.end_turn_button, "End Turn", mouse_pos)
        self._draw_button(self.start_combat_button, "Start Combat", mouse_pos)

        # Show coords button text changes based on state
        coords_text = "Hide hex coords" if self.show_hex_coords else "Show hex coords"
        self._draw_button(self.show_coords_button, coords_text, mouse_pos)

    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: tuple[int, int]):
        """Draw button with hover effect."""
        # Hover detection
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        # Draw button background and border
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BUTTON_TEXT_COLOR, rect, BUTTON_BORDER_WIDTH)

        # Draw text centered
        font = pygame.font.Font(None, 28)
        text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def _handle_button_click(self, mouse_pos: tuple[int, int]) -> bool:
        """Handle button clicks. Returns True if a button was clicked."""
        if self.end_turn_button.collidepoint(mouse_pos):
            self._end_turn()
            return True
        elif self.start_combat_button.collidepoint(mouse_pos):
            self._start_test_combat()
            return True
        elif self.show_coords_button.collidepoint(mouse_pos):
            self._toggle_hex_coords()
            return True
        return False

    def _end_turn(self):
        """End current turn and advance to next."""
        self.current_turn += 1

        # Autosave at start of new turn
        self.save_state('autosave_turn')
        print("[Autosave] Turn start")

        # Restore hero movement points
        self.hero.restore_movement()

        # Recalculate reachable cells
        self._calculate_reachable_cells()

        print(f"=== Turn {self.current_turn} started ===")

    def _start_test_combat(self):
        """Start test combat (manual trigger) using current scenario preset."""
        player_army = self.hero.army
        enemy_army = ENEMY_PRESETS.get(self.scenario_preset, ENEMY_PRESETS['default'])
        terrain = 'plains'
        print(f"Starting test combat with preset '{self.scenario_preset}'")
        print(f"  Player army: {player_army}")
        print(f"  Enemy army: {enemy_army}")
        self.game.start_combat(player_army, enemy_army, terrain)

    def _toggle_hex_coords(self):
        """Toggle display of hex coordinates on/off."""
        self.show_hex_coords = not self.show_hex_coords
        status = "ON" if self.show_hex_coords else "OFF"
        print(f"Hex coordinates display: {status}")

    def _draw_hex_coords(self):
        """Draw coordinates on each hex."""
        font = pygame.font.Font(None, 18)  # Small font for coordinates

        for row in self.map_grid:
            for province in row:
                # Get hex center position
                center_x, center_y = hex_to_pixel(province.x, province.y)

                # Create coordinate text "x,y"
                coord_text = f"{province.x},{province.y}"
                text_surf = font.render(coord_text, True, WHITE)
                text_rect = text_surf.get_rect(center=(int(center_x), int(center_y)))

                # Draw black background for better visibility
                background_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(self.screen, BLACK, background_rect)

                # Draw coordinate text
                self.screen.blit(text_surf, text_rect)

    def save_state(self, slot: str = 'quicksave', slot_number: int = None) -> bool:
        """
        Save current strategic state to file.

        Args:
            slot: Save slot type ('autosave_combat', 'autosave_turn', 'quicksave', 'manual')
            slot_number: Slot number for manual saves

        Returns:
            True if save successful
        """
        state_dict = {
            'version': '1.0',
            'turn': self.current_turn,
            'hero': self.hero.to_dict(),
            'map': [[province.to_dict() for province in row] for row in self.map_grid]
        }

        success = save_system.save_game(state_dict, slot, slot_number)
        if success:
            slot_name = f"{slot}{slot_number if slot_number else ''}"
            print(f"Game saved to slot: {slot_name}")
        return success

    def load_state(self, slot: str = 'quicksave', slot_number: int = None) -> bool:
        """
        Load strategic state from file.

        Args:
            slot: Save slot type
            slot_number: Slot number for manual saves

        Returns:
            True if load successful
        """
        state_dict = save_system.load_game(slot, slot_number)
        if not state_dict:
            print("Failed to load game - save file not found or corrupted")
            return False

        try:
            # Restore turn counter
            self.current_turn = state_dict.get('turn', 1)

            # Restore hero
            self.hero = Hero.from_dict(state_dict['hero'])

            # Restore map
            map_data = state_dict['map']
            self.map_grid = [[Province.from_dict(prov_data) for prov_data in row] for row in map_data]

            # Recalculate reachable cells
            self._calculate_reachable_cells()

            slot_name = f"{slot}{slot_number if slot_number else ''}"
            print(f"Game loaded from slot: {slot_name}")
            print(f"Turn: {self.current_turn}, Hero at ({self.hero.x}, {self.hero.y})")
            return True

        except Exception as e:
            print(f"Error loading game state: {e}")
            return False

    def handle_key(self, key: int):
        """
        Handle keyboard input.

        Hotkeys:
            F5 - Quicksave (save2.json)
            F6 - Load autosave before combat (save0.json)
            F7 - Load autosave turn start (save1.json)
            F9 - Load quicksave (save2.json)

        Args:
            key: Pygame key constant
        """
        if key == pygame.K_F5:
            # Quicksave
            self.save_state('quicksave')
            print("Quicksave created (F5)")

        elif key == pygame.K_F6:
            # Load autosave before combat
            if save_system.save_exists('autosave_combat'):
                self.load_state('autosave_combat')
                print("Loaded autosave before combat (F6)")
            else:
                print("No autosave before combat found (F6)")

        elif key == pygame.K_F7:
            # Load autosave turn start
            if save_system.save_exists('autosave_turn'):
                self.load_state('autosave_turn')
                print("Loaded autosave turn start (F7)")
            else:
                print("No autosave turn start found (F7)")

        elif key == pygame.K_F9:
            # Quickload
            if save_system.save_exists('quicksave'):
                self.load_state('quicksave')
                print("Quickload loaded (F9)")
            else:
                print("No quicksave found (F9)")