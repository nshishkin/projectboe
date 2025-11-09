"""
Game state management for Brothers of Eador.
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
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create menu buttons."""
        # Create preset buttons for strategic map
        presets = [
            ("Wood", "forest"),
            ("Hills", "mountainous"),  # Using mountainous preset for hills
            ("Plains", "plains"),
            ("Swamps", "wetlands")
        ]
        
        for i, (display_name, preset_name) in enumerate(presets):
            button = {
                'text': display_name,
                'preset': preset_name,
                'rect': pygame.Rect(300, 300 + i * 60, 200, 50),
                'color': (70, 130, 180),  # Steel blue
                'hover_color': (10, 149, 237)  # Cornflower blue
            }
            self.buttons.append(button)
        
        # Add tactical button
        tactical_button = {
            'text': "Tactical Map",
            'preset': None,
            'rect': pygame.Rect(300, 300 + len(presets) * 60, 200, 50),
            'color': (50, 205, 50),  # Lime green
            'hover_color': (34, 139, 34)  # Forest green
        }
        self.buttons.append(tactical_button)
    
    def enter(self):
        print("Entering Menu State")
    
    def render(self, screen):
        # Fill screen with a menu background color
        screen.fill((50, 50, 100))  # Dark blue background
        
        # Draw menu text
        font = pygame.font.SysFont(None, 48)
        title = font.render("Brothers of Eador", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, screen.get_height()//6))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.SysFont(None, 32)
        
        for button in self.buttons:
            color = button['hover_color'] if button['rect'].collidepoint(mouse_pos) else button['color']
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, (255, 255, 255), button['rect'], 2)  # White border
            
            text = font_small.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
        
        # Draw instructions
        instructions_font = pygame.font.SysFont(None, 24)
        instructions = instructions_font.render("Click on a preset to go to Strategic Map, or Tactical Map button", True, (20, 200, 200))
        screen.blit(instructions, (screen.get_width()//2 - instructions.get_width()//2, screen.get_height() - 50))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button['rect'].collidepoint(mouse_pos):
                    if button['preset']:  # Strategic map with preset
                        # Set the preset for the strategic map
                        strategic_state = self.state_manager.states.get('strategic')
                        if strategic_state:
                            # Store the selected preset to be used when creating the map
                            strategic_state.selected_preset = button['preset']
                            # Recreate the strategic map with the selected preset
                            from game.strategic.strategic_map import StrategicMap
                            from config.settings import STRATEGIC_MAP_WIDTH, STRATEGIC_MAP_HEIGHT
                            strategic_state.strategic_map = StrategicMap(
                                width=STRATEGIC_MAP_WIDTH,
                                height=STRATEGIC_MAP_HEIGHT,
                                preset_name=button['preset']
                            )
                        self.state_manager.set_state('strategic')
                    else:  # Tactical map
                        self.state_manager.set_state('tactical')
                    return True
        
        # Don't handle ESC in the menu so the main loop can quit the game
        return False


class StrategicState(GameState):
    """Strategic map state for the game."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        # Import here to avoid circular dependencies
        from game.strategic.strategic_map import StrategicMap
        # Use dimensions from config settings
        from config.settings import STRATEGIC_MAP_WIDTH, STRATEGIC_MAP_HEIGHT
        self.strategic_map = StrategicMap(width=STRATEGIC_MAP_WIDTH, height=STRATEGIC_MAP_HEIGHT, preset_name="balanced")
        self.selected_preset = "balanced"  # Default preset
   
    def enter(self):
        print("Entering Strategic State")
        # If a preset was selected, recreate the map with that preset
        if hasattr(self, 'selected_preset') and self.selected_preset:
            from game.strategic.strategic_map import StrategicMap
            from config.settings import STRATEGIC_MAP_WIDTH, STRATEGIC_MAP_HEIGHT
            self.strategic_map = StrategicMap(
                width=STRATEGIC_MAP_WIDTH,
                height=STRATEGIC_MAP_HEIGHT,
                preset_name=self.selected_preset
            )
            # Reset the selected preset after using it
            self.selected_preset = None
    
    def render(self, screen):
        # Clear the screen with a background color before drawing strategic elements
        screen.fill((100, 150, 100))  # Green background for strategic view
        # Render the strategic map
        self.strategic_map.render(screen)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left mouse button
            # Handle click on strategic map hex
            clicked_hex = self.strategic_map.handle_click(event.pos)
            if clicked_hex:
                # Get the terrain type of the clicked hex
                strategic_terrain = clicked_hex.terrain_type
                
                # Update the tactical state with the strategic terrain information
                tactical_state = self.state_manager.states.get('tactical')
                if tactical_state:
                    # Recreate the tactical map with the strategic terrain influence
                    from game.tactical.map import TacticalMap
                    from config.settings import TACTICAL_GRID_WIDTH, TACTICAL_GRID_HEIGHT
                    tactical_state.tactical_map = TacticalMap(
                        width=TACTICAL_GRID_WIDTH,
                        height=TACTICAL_GRID_HEIGHT,
                        strategic_terrain=clicked_hex.terrain_type
                    )
                
                # Transition to tactical state
                self.state_manager.set_state('tactical')
                return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Press 'M' to go back to menu
                self.state_manager.set_state('menu')
                return True
            elif event.key == pygame.K_t:  # Press 'T' to go to tactical view
                # For the 'T' key, use default terrain
                self.state_manager.set_state('tactical')
                return True
        return False


class TacticalState(GameState):
    """Tactical combat state for the game."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        # Import here to avoid circular dependencies
        from game.tactical.map import TacticalMap
        # Use dimensions from config settings
        from config.settings import TACTICAL_GRID_WIDTH, TACTICAL_GRID_HEIGHT
        self.tactical_map = TacticalMap(width=TACTICAL_GRID_WIDTH, height=TACTICAL_GRID_HEIGHT,
                                      strategic_terrain="plain")
    
    def enter(self):
        print("Entering Tactical State")
    
    def render(self, screen):
        # Clear the screen with a background color before drawing tactical elements
        screen.fill((150, 150, 150))  # Gray background for tactical view
        # Render the tactical map
        self.tactical_map.render(screen)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Press 'M' to go back to menu
                self.state_manager.set_state('menu')
                return True
            elif event.key == pygame.K_s:  # Press 'S' to go to strategic view
                self.state_manager.set_state('strategic')
                return True
        return False