#!/usr/bin/env python3
"""
Main entry point for Battle of Empires (BoE) game.
This file initializes Pygame and starts the main game loop.
"""

import pygame
import sys

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.core.state import StateManager, MenuState, StrategicState, TacticalState

# Initialize Pygame
pygame.init()

def main():
    """Main function to run the game."""
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battle of Empires")
    
    # Set up the clock for managing frame rate
    clock = pygame.time.Clock()
    
    # Initialize state manager
    state_manager = StateManager()
    
    # Add states to the manager
    menu_state = MenuState(state_manager)
    strategic_state = StrategicState(state_manager)
    tactical_state = TacticalState(state_manager)
    
    state_manager.add_state('menu', menu_state)
    state_manager.add_state('strategic', strategic_state)
    state_manager.add_state('tactical', tactical_state)
    
    # Set initial state
    state_manager.set_state('menu')
    
    # Main game loop
    running = True
    while running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Let the current state handle the event
            state_manager.handle_event(event)
        
        # Update the current state
        state_manager.update(dt)
        
        # Render the current state
        state_manager.render(screen)
        
        # Update the display
        pygame.display.flip()
    
    # Quit Pygame and exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()