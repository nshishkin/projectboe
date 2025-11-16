"""
Main game state machine.
Manages transitions between menu, strategic, and tactical states.
"""

import pygame

from constants import BG_COLOR, TEXT_COLOR
from strategic.strategic_state import StrategicState

class Game:
    """
    Game state machime that controls game flow.
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
        self.strategic_state = StrategicState(self.screen)
        
        # Phase 3: Will initialize TacticalState
        self.tactical_state = None

        print(f"Game initialized in state: {self.current_state}")
    
    def update(self):
        """Update current game state logic."""
        if self.current_state == 'menu':
            pass
        elif self.current_state == 'strategic':
            self.strategic_state.update()  # Call strategic update
        elif self.current_state == 'tactical':
            pass
    
    def render(self):
        """Render current game state."""
        # Clear screen
        self.screen.fill(BG_COLOR)

        if self.current_state == 'menu':
            self._render_menu()
        elif self.current_state == 'strategic':
            self.strategic_state.render()  # Call strategic render
        elif self.current_state == 'tactical':
            self._render_tactical()
    
    def _render_menu(self):
        """Render menu state (placeholder for Phase 1)."""
        font = pygame.font.Font(None, 36)
        text = font.render("MENU STATE - Press SPACE to start", True,TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen.get_width()//2,self.screen.get_height()//2))
        self.screen.blit(text, text_rect)

    def _render_strategic(self):
        """Render strategic state (placeholder for Phase 1)."""
        font = pygame.font.Font(None, 36)
        text = font.render("STRATEGIC STATE - Map goes here", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)

    def _render_tactical(self):
        """Render tactical state (placeholder for Phase 1)."""
        font = pygame.font.Font(None, 36)
        text = font.render("TACTICAL STATE - Combat goes here", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)

    def change_state(self, new_state: str):
        """Change to new game state.
        Args:
            new_state: State name('menu', 'strategic', 'tactical')
        """
        print(f"State transition: {self.current_state} -> {new_state}")
        self.current_state = new_state
    
    def handle_event(self, event: pygame.event.Event):
        # Phase 1: Simple keyboard test for state transitions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.current_state == 'menu':
                    self.change_state('strategic')
            elif event.key == pygame.K_ESCAPE:
                if self.current_state != 'menu':
                    self.change_state('menu')
        
        # Phase 2: Handle mouse clicks in strategic state
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_state == 'strategic':
                self.strategic_state.handle_click(event.pos)