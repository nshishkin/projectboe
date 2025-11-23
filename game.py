"""
Main game state machine.
Manages transitions between menu, strategic, and tactical states.
"""

import pygame

from config.constants import BG_COLOR, TEXT_COLOR
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

        # Create strategic state (Phase 2)
        self.strategic_state = StrategicState(self.screen, self)

        # Phase 3: Tactical state (created when combat starts)
        self.tactical_state = None

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
                self.tactical_state.render()
    
    def _render_menu(self):
        """Render menu state (placeholder for Phase 1)."""
        font = pygame.font.Font(None, 36)
        text = font.render("MENU STATE - Press SPACE to start", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, text_rect)

    def change_state(self, new_state: str):
        """
        Change to new game state.

        Args:
            new_state: State name ('menu', 'strategic', 'tactical')
        """
        print(f"State transition: {self.current_state} -> {new_state}")
        self.current_state = new_state

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
            if event.key == pygame.K_SPACE:
                if self.current_state == 'menu':
                    self.change_state('strategic')
            elif event.key == pygame.K_ESCAPE:
                # ESC from tactical returns to strategic
                if self.current_state == 'tactical':
                    self.change_state('strategic')
                # ESC from strategic returns to menu
                elif self.current_state == 'strategic':
                    self.change_state('menu')

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_state == 'strategic':
                self.strategic_state.handle_click(event.pos)
            elif self.current_state == 'tactical':
                if self.tactical_state:
                    self.tactical_state.handle_click(event.pos)