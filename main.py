"""
Entry point for BoE (Brothers of Eador).
Initializes Pygame and runs the main game loop.
"""
import pygame

from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT,FPS

def main():
    """Initializes and run the game."""
    print("Starting BoE...")

    #Initialize Pygame
    pygame.init()

    #Create display window
    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption("BoE- Brothers of Eador")

    # Create clock for FPS control
    clock=pygame.time.clock()

    #Create game instance
    game = Game(screen)

    # Main game loop
    running = True
    while running:
        # Handle events:
        for event in pygame.event.get():
            if event.type==pygame.Quit:
                running=false
            else:
                # Pass other events to game state
                game.handle_event(event)
        
        # Update game state
        game.update()

        # Render
        game.render()

        # Update display and control frame rate
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    print("Shutting down..")
    pygame.quit()

if _name_== "_main_":
    main()