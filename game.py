"""
Main game state machine.
Manages transitions between menu, strategic, and tactical states.
"""

import pygame

from config.constants import (
    BG_COLOR, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR,
    BUTTON_TEXT_COLOR, BUTTON_HEIGHT, BUTTON_BORDER_WIDTH
)
from strategic.strategic_state import StrategicState
from tactical.tactical_state import TacticalState

class Game:
    """
    Game state machine that controls game flow.
    'menu' -> 'strategic' -> 'tactical' -> back to 'strategic'
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize game with starting state.
        Args:
            screen: Pygame display surface to render to
        """
        self.screen = screen
        self.current_state = 'menu'
        self.running = True

        # Strategic state (created when scenario is selected)
        self.strategic_state = None

        # Phase 3: Tactical state (created when combat starts)
        self.tactical_state = None

        # Menu buttons (4 scenario selection buttons)
        button_width = 400
        button_spacing = 20
        start_y = 200
        center_x = self.screen.get_width() // 2

        self.menu_buttons = {
            'player_win': pygame.Rect(center_x - button_width // 2, start_y, button_width, BUTTON_HEIGHT),
            'player_loss': pygame.Rect(center_x - button_width // 2, start_y + (BUTTON_HEIGHT + button_spacing) * 1, button_width, BUTTON_HEIGHT),
            'movement': pygame.Rect(center_x - button_width // 2, start_y + (BUTTON_HEIGHT + button_spacing) * 2, button_width, BUTTON_HEIGHT),
            'default': pygame.Rect(center_x - button_width // 2, start_y + (BUTTON_HEIGHT + button_spacing) * 3, button_width, BUTTON_HEIGHT)
        }

        print(f"Game initialized in state: {self.current_state}")
    
    def update(self):
        """Update current game state logic."""
        if self.current_state == 'menu':
            pass
        elif self.current_state == 'strategic':
            self.strategic_state.update()
        elif self.current_state == 'tactical':
            if self.tactical_state:
                self.tactical_state.update()
    
    def render(self):
        """Render current game state."""
        # Clear screen
        self.screen.fill(BG_COLOR)

        if self.current_state == 'menu':
            self._render_menu()
        elif self.current_state == 'strategic':
            self.strategic_state.render()
        elif self.current_state == 'tactical':
            if self.tactical_state:
                self.tactical_state.renderer.render()
    
    def _render_menu(self):
        """Render menu state with scenario selection buttons."""
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("Battle of Empires", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 28)
        subtitle_text = subtitle_font.render("Select Scenario:", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width()//2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Button labels
        button_labels = {
            'player_win': 'Player Win Scenario',
            'player_loss': 'Player Loss Scenario',
            'movement': 'Movement Test Scenario',
            'default': 'Default Scenario'
        }

        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_font = pygame.font.Font(None, 32)

        # Draw buttons
        for button_key, button_rect in self.menu_buttons.items():
            # Check if mouse is hovering over button
            is_hovering = button_rect.collidepoint(mouse_pos)
            button_color = BUTTON_HOVER_COLOR if is_hovering else BUTTON_COLOR

            # Draw button background
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, BUTTON_TEXT_COLOR, button_rect, BUTTON_BORDER_WIDTH)

            # Draw button text
            text = button_font.render(button_labels[button_key], True, BUTTON_TEXT_COLOR)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

    def change_state(self, new_state: str):
        """
        Change to new game state.

        Args:
            new_state: State name ('menu', 'strategic', 'tactical')
        """
        print(f"State transition: {self.current_state} -> {new_state}")
        self.current_state = new_state

    def start_scenario(self, scenario_name: str):
        """
        Start game with selected scenario preset.

        Args:
            scenario_name: Scenario preset name ('player_win', 'player_loss', 'movement', 'default')
        """
        # Map scenario names to preset keys
        scenario_map = {
            'player_win': 'debug_player_win',
            'player_loss': 'debug_player_loss',
            'movement': 'debug_movement',
            'default': 'default'
        }

        preset_key = scenario_map.get(scenario_name, 'default')
        print(f"Starting scenario: {scenario_name} (preset: {preset_key})")

        # Create strategic state with selected preset
        self.strategic_state = StrategicState(self.screen, self, preset_key)
        self.change_state('strategic')

    def start_combat(self, player_army: list[str], enemy_army: list[str], terrain: str):
        """
        Start tactical combat.

        Called by strategic_state when combat is triggered.

        Args:
            player_army: List of unit types for player
            enemy_army: List of unit types for enemy
            terrain: Terrain type from province
        """
        self.tactical_state = TacticalState(self.screen, self, player_army, enemy_army, terrain)
        self.change_state('tactical')
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events based on current state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC from tactical: skip animation if playing, otherwise return to strategic
                if self.current_state == 'tactical':
                    if self.tactical_state and self.tactical_state.animation_queue.is_playing():
                        self.tactical_state.animation_queue.skip_current()
                        print("Animation skipped (ESC)")
                    else:
                        self.change_state('strategic')
                # ESC from strategic returns to menu
                elif self.current_state == 'strategic':
                    self.change_state('menu')

            # Pass key events to strategic state for save/load handling
            if self.current_state == 'strategic' and self.strategic_state:
                self.strategic_state.handle_key(event.key)

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_state == 'menu':
                # Check menu button clicks
                mouse_pos = event.pos
                for button_key, button_rect in self.menu_buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        self.start_scenario(button_key)
                        break
            elif self.current_state == 'strategic':
                if self.strategic_state:
                    self.strategic_state.handle_click(event.pos)
            elif self.current_state == 'tactical':
                if self.tactical_state:
                    self.tactical_state.input.handle_click(event.pos)
        # Handle mouse wheel
        elif event.type == pygame.MOUSEWHEEL:
            if self.current_state == 'tactical':
                if self.tactical_state:
                    self.tactical_state.input.handle_mousewheel(event)