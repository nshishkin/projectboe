"""
Game state management for Battle of Empires.
This module manages different game states (tactical, strategic, menu, etc.)
"""

import pygame

class StateManager:
    """Manages different game states and transitions between them."""
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.previous_state = None
    
    def add_state(self, name, state_obj):
        """Add a state to the manager."""
        self.states[name] = state_obj
    
    def set_state(self, name):
        """Switch to a different state."""
        if name in self.states:
            self.previous_state = self.current_state
            self.current_state = name
            # Call the enter method of the new state if it exists
            if hasattr(self.states[name], 'enter'):
                self.states[name].enter()
    
    def get_current_state(self):
        """Get the current state object."""
        if self.current_state and self.current_state in self.states:
            return self.states[self.current_state]
        return None
    
    def update(self, dt):
        """Update the current state."""
        current_state = self.get_current_state()
        if current_state and hasattr(current_state, 'update'):
            current_state.update(dt)
    
    def render(self, screen):
        """Render the current state."""
        current_state = self.get_current_state()
        if current_state and hasattr(current_state, 'render'):
            current_state.render(screen)
    
    def handle_event(self, event):
        """Handle events for the current state."""
        current_state = self.get_current_state()
        if current_state and hasattr(current_state, 'handle_event'):
            return current_state.handle_event(event)
        return False


class GameState:
    """Base class for game states."""
    
    def enter(self):
        """Called when entering this state."""
        pass
    
    def update(self, dt):
        """Update the state with delta time."""
        pass
    
    def render(self, screen):
        """Render the state to the screen."""
        pass
    
    def handle_event(self, event):
        """Handle pygame events."""
        return False


class MenuState(GameState):
    """Menu state for the game."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def enter(self):
        print("Entering Menu State")
    
    def render(self, screen):
        # Fill screen with a menu background color
        screen.fill((50, 50, 100))  # Dark blue background
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Press 'S' to go to strategic view
                self.state_manager.set_state('strategic')
                return True
            elif event.key == pygame.K_t:  # Press 'T' to go to tactical view
                self.state_manager.set_state('tactical')
                return True
        return False


class StrategicState(GameState):
    """Strategic map state for the game."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def enter(self):
        print("Entering Strategic State")
    
    def render(self, screen):
        # Fill screen with a strategic map background color
        screen.fill((100, 150, 100))  # Green background for strategic view
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Press 'M' to go back to menu
                self.state_manager.set_state('menu')
                return True
            elif event.key == pygame.K_t:  # Press 'T' to go to tactical view
                self.state_manager.set_state('tactical')
                return True
        return False


class TacticalState(GameState):
    """Tactical combat state for the game."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def enter(self):
        print("Entering Tactical State")
    
    def render(self, screen):
        # Fill screen with a tactical combat background color
        screen.fill((150, 100, 100))  # Red background for tactical view
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Press 'M' to go back to menu
                self.state_manager.set_state('menu')
                return True
            elif event.key == pygame.K_s:  # Press 'S' to go to strategic view
                self.state_manager.set_state('strategic')
                return True
        return False