"""
Main game state machine.
Manages transitions between menu, strategic, and tactical states.
"""

import pygame

from constants import BG_COLOR, TEXT_COLOR

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

        # Phase 1: Just placeholder states
        # Phase 2: Will initialize StrategicState, TacticalState etc.
        self.strategic_state = None
        self.tactical_state = None

        print(f"Game initialized in state: {self.current_state}")
    
    def update(self):
        """Update current game state logic."""
        # Phase 1: Basic state handling
        if self.current_state == 'menu':
            # TODO Menu logic(Phase 1 - just autotransition)
        elif self.current_state == 'strategic':
            # TODO Strategic state update(Phase 2)
            pass
        elif self.current_state == 'tactical':
            # TODO: Tactical state update(Phase 3)
            pass
    
    def render(self):
        """Render current game state."""
        # Clear screen
        self.screen.fill(BG_COLOR)

        # Phase 1: Simple text rendering to show current state
        if self.current_state == 'menu':
            self._render_menu()
        elif self.current_state == 'strategic':
            self._render_strategic()
        elif self.current_state == 'tactical':
            self.render_tactical()
    
    def _render_menu(self):
        """Render menu state (placeholder for Phase 1)."""
        font = pygame.font.Font(None, 36)
        text = font.render("MENU STATE - Press SPACE to start", True,TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen.get_width()//2,self.screen.get_height)//2))
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
        print(f`State transition: {self.current_state} -> {new_state}`)
        self.current_state = new_state
    
    def handle_event(self, event: pygame.event.Event):
        """ Handle input events for current state.
        Args:
            event: Pygame event to process
        """
        # Phase 1: Simple keyboard test for state transitions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.current_state == 'menu':
                    self.change_state('strategic')
            elif event.key == pygame.K_ESCAPE:
                if self.current_state != 'menu':
                    self.change_state('menu')