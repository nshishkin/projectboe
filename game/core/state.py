"""
Game state management for Brothers of Eador.
This module manages different game states (tactical, strategic, menu, etc.)
"""

import pygame
from .hero_unit import HeroManager, HeroUnit, HeroFaction

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
        
        # Initialize hero manager
        self.hero_manager = HeroManager()
        # Add a default player hero
        from config.constants import DEFAULT_HERO_SPAWN_Q, DEFAULT_HERO_SPAWN_R
        player_hero = HeroUnit(name="Player Hero", q=DEFAULT_HERO_SPAWN_Q, r=DEFAULT_HERO_SPAWN_R, faction=HeroFaction.PLAYER)
        self.hero_manager.add_hero(player_hero)
        
        # Initialize UI elements
        self.end_turn_button = None
        self.start_combat_button = None
        self._create_ui_elements()
    
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
    
    def _draw_heroes(self, screen):
        """Draw all heroes on the strategic map."""
        for hero in self.hero_manager.heroes:
            hex_tile = self.strategic_map.get_hex_at(hero.q, hero.r)
            if hex_tile:
                # Determine hero color based on faction
                faction_colors = {
                    HeroFaction.PLAYER: (0, 0, 255),    # Blue for player
                    HeroFaction.ENEMY: (255, 0, 0),     # Red for enemy
                    HeroFaction.NEUTRAL: (255, 255, 0), # Yellow for neutral
                    HeroFaction.ALLY: (0, 255, 0)       # Green for ally
                }
                color = faction_colors.get(hero.faction, (255, 255, 255))  # White as fallback
                
                # Draw the hero as a circle in the center of the hex
                pygame.draw.circle(screen, color,
                                 (int(hex_tile.center_x), int(hex_tile.center_y)),
                                 10)  # radius 10 pixels
                
                # Draw a border for the selected hero
                if hero == self.hero_manager.selected_hero:
                    pygame.draw.circle(screen, (255, 255, 255),
                                     (int(hex_tile.center_x), int(hex_tile.center_y)),
                                     12, 2)  # white border with width 2
    
    def _can_move_to_hex(self, target_hex):
        """Check if the selected hero can move to the target hex."""
        selected_hero = self.hero_manager.selected_hero
        if not selected_hero:
            return False
            
        # Check if the target hex is passable
        if not target_hex.is_passable:
            return False
            
        # Check if hero has enough movement points
        from config.constants import TERRAIN_MOVEMENT_COST
        movement_cost = TERRAIN_MOVEMENT_COST.get(target_hex.terrain_type, 2)
        return selected_hero.movement_points >= movement_cost
    
    def _move_hero_to_hex(self, target_hex):
        """Move the selected hero to the target hex."""
        selected_hero = self.hero_manager.selected_hero
        if not selected_hero:
            return False
            
        # Check if hero can move to the hex
        if not self._can_move_to_hex(target_hex):
            return False
            
        # Get movement cost
        from config.constants import TERRAIN_MOVEMENT_COST
        movement_cost = TERRAIN_MOVEMENT_COST.get(target_hex.terrain_type, 2)
        
        # Spend movement points
        if selected_hero.spend_movement_points(movement_cost):
            # Move the hero to the new position
            selected_hero.move_to(target_hex.q, target_hex.r)
            # Update possible moves visualization
            self._update_possible_moves_display()
            return True
        return False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left mouse button
            # Check if the click is on the end turn button first
            if self.end_turn_button and self.end_turn_button['rect'].collidepoint(event.pos):
                self._handle_end_turn()
                return True
            # Check if the click is on the start combat button
            elif self.start_combat_button and self.start_combat_button['rect'].collidepoint(event.pos):
                self._handle_start_combat()
                return True
            else:
                # Handle click on strategic map hex for hero movement
                clicked_hex = self.strategic_map.handle_click(event.pos)
                if clicked_hex:
                    # Check if a hero is already at this position
                    hero_at_hex = None
                    for hero in self.hero_manager.heroes:
                        if hero.q == clicked_hex.q and hero.r == clicked_hex.r:
                            hero_at_hex = hero
                            break
                    
                    # If clicked on a hero, select it
                    if hero_at_hex:
                        self.hero_manager.select_hero(hero_at_hex)
                        # Update possible moves visualization
                        self._update_possible_moves_display()
                    else:
                        # Otherwise, try to move the selected hero to this hex
                        self._move_hero_to_hex(clicked_hex)
                    
                    return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m: # Press 'M' to go back to menu
                self.state_manager.set_state('menu')
                return True
            elif event.key == pygame.K_t: # Press 'T' to go to tactical view
                # For the 'T' key, use default terrain
                self.state_manager.set_state('tactical')
                return True
            elif event.key == pygame.K_SPACE: # Press space to reset movement points
                # Reset movement points for all heroes at the start of a turn
                for hero in self.hero_manager.heroes:
                    hero.reset_movement_points()
                # Update possible moves visualization
                self._update_possible_moves_display()
                return True
            elif event.key == pygame.K_d: # Press 'D' toggle debug mode
                self.strategic_map.toggle_debug_mode()
                return True
        return False
    
    def _update_possible_moves_display(self):
        """Update the display of possible moves for the selected hero."""
        selected_hero = self.hero_manager.selected_hero
        if selected_hero:
            from config.constants import TERRAIN_MOVEMENT_COST
            possible_moves = self.hero_manager.get_available_moves(
                selected_hero,
                self.strategic_map,
                TERRAIN_MOVEMENT_COST
            )
            self.strategic_map.set_highlighted_hexes(possible_moves)
        else:
            self.strategic_map.clear_highlighted_hexes()
    
    def _create_ui_elements(self):
        """Create UI elements for the strategic state."""
        import pygame
        # Create the end turn button
        button_width = 120
        button_height = 40
        # We'll set the position in the render method when we have access to screen dimensions
        self.end_turn_button = {
            'text': "End Turn",
            'color': (70, 130, 180),  # Steel blue
            'hover_color': (10, 149, 237),  # Cornflower blue
            'width': button_width,
            'height': button_height
        }
        
        # Create the start combat button
        self.start_combat_button = {
            'text': "Start Combat",
            'color': (50, 205, 50),  # Lime green
            'hover_color': (34, 139, 34),  # Forest green
            'width': button_width,
            'height': button_height
        }
    
    def _draw_ui_elements(self, screen):
        """Draw UI elements like buttons."""
        import pygame
        if self.end_turn_button:
            # Calculate button position in the top-right corner with margin
            button_x = screen.get_width() - self.end_turn_button['width'] - 20  # 20 pixels margin from right edge
            button_y = 20 # 20 pixels from the top edge
            
            # Create the button rectangle with the calculated position
            button_rect = pygame.Rect(button_x, button_y, self.end_turn_button['width'], self.end_turn_button['height'])
            
            # Determine button color based on hover state
            mouse_pos = pygame.mouse.get_pos()
            color = self.end_turn_button['hover_color'] if button_rect.collidepoint(mouse_pos) else self.end_turn_button['color']
            
            # Draw button rectangle
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)  # White border
            
            # Draw button text
            font = pygame.font.SysFont(None, 28)
            text = font.render(self.end_turn_button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            
            # Update the button rect for event handling
            self.end_turn_button['rect'] = button_rect
        
        if self.start_combat_button:
            # Calculate button position just below the end turn button
            button_x = screen.get_width() - self.start_combat_button['width'] - 20  # 20 pixels margin from right edge
            button_y = 70 # 70 pixels from the top edge (20 + 40 + 10 for spacing)
            
            # Create the button rectangle with the calculated position
            button_rect = pygame.Rect(button_x, button_y, self.start_combat_button['width'], self.start_combat_button['height'])
            
            # Determine button color based on hover state
            mouse_pos = pygame.mouse.get_pos()
            color = self.start_combat_button['hover_color'] if button_rect.collidepoint(mouse_pos) else self.start_combat_button['color']
            
            # Draw button rectangle
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)  # White border
            
            # Draw button text
            font = pygame.font.SysFont(None, 28)
            text = font.render(self.start_combat_button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            
            # Update the button rect for event handling
            self.start_combat_button['rect'] = button_rect
    
    def _handle_end_turn(self):
        """Handle the end turn action."""
        # Reset movement points for all player heroes
        for hero in self.hero_manager.heroes:
            if hero.faction == HeroFaction.PLAYER:
                hero.reset_movement_points()
        
        # Clear highlighted hexes
        self.strategic_map.clear_highlighted_hexes()
    
    def _handle_start_combat(self):
        """Handle the start combat action."""
        # Get the selected hero
        selected_hero = self.hero_manager.selected_hero
        if not selected_hero:
            # If no hero is selected, use the first player hero
            for hero in self.hero_manager.heroes:
                if hero.faction == HeroFaction.PLAYER:
                    selected_hero = hero
                    break
        
        if selected_hero:
            # Get the terrain type of the hex where the hero is located
            hero_hex = self.strategic_map.get_hex_at(selected_hero.q, selected_hero.r)
            if hero_hex:
                strategic_terrain = hero_hex.terrain_type
                
                # Update the tactical state with the strategic terrain information
                tactical_state = self.state_manager.states.get('tactical')
                if tactical_state:
                    # Recreate the tactical map with the strategic terrain influence
                    from game.tactical.map import TacticalMap
                    from config.settings import TACTICAL_GRID_WIDTH, TACTICAL_GRID_HEIGHT
                    tactical_state.tactical_map = TacticalMap(
                        width=TACTICAL_GRID_WIDTH,
                        height=TACTICAL_GRID_HEIGHT,
                        strategic_terrain=hero_hex.terrain_type
                    )
                
                # Transition to tactical state
                self.state_manager.set_state('tactical')
    
    def render(self, screen):
        # Clear the screen with a background color before drawing strategic elements
        screen.fill((100, 150, 100))  # Green background for strategic view
        # Render the strategic map
        self.strategic_map.render(screen)
        
        # Draw heroes on the map
        self._draw_heroes(screen)
        
        # Draw UI elements
        self._draw_ui_elements(screen)
        
        # Update possible moves display if needed
        # (This could be optimized to only update when selection changes)
        self._update_possible_moves_display()


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
            elif event.key == pygame.K_d:  # Press 'D' toggle debug mode
                self.tactical_map.toggle_debug_mode()
                return True
        return False