# BoE (Brothers of Eador) - Game Design Document

## Core Concept

BoE is a hybrid strategy game that combines elements from Eador and Battle Brothers, featuring both strategic and tactical gameplay layers. The game blends low-fantasy combat with RPG progression elements, focusing on unit positioning, equipment management, and tactical decision-making. The game will be single-player only.

## Gameplay Layers

### Strategic Layer
The strategic layer takes place on a randomly generated map consisting of provinces (nodes) that differ primarily by terrain type and inhabitant races. The default map size is 8x8 provinces, with options for different world sizes and terrain preferences in the future. The main terrain types include:


- Plains: Open areas that provide moderate movement speed and balanced combat bonuses
- Woods: Dense areas that provide defensive bonuses but may limit movement for certain unit types
- Hills: Elevated areas that offer tactical advantages for ranged units but may slow down cavalry
- Swamps: Difficult terrain that slows movement and may reduce unit effectiveness

Each province is inhabited by different races that may be friendly, neutral, or hostile to the player. Players control heroes who move across this strategic map, exploring provinces, recruiting units, managing resources, and engaging in various activities. The strategic layer focuses on:

- Hero movement and pathfinding
- Province exploration and control
- Resource management
- Unit recruitment and army composition
- Diplomacy with different races
- Quest completion

When combat is initiated through encounters with hostile forces or by attacking enemy positions, the game transitions to the tactical layer.
### Tactical Layer

The tactical layer involves direct combat between the player's squad of units and AI opponents on detailed battlefields. Key features include:

- Low-fantasy setting with limited magic elements
- Focus on unit positioning and tactical placement
- Equipment management and unit types
- Armor and weapon considerations
- RPG progression system for player units

Combat mechanics emphasize tactical positioning, with different unit types having advantages and disadvantages against others. The battlefield uses a configurable grid system (default 10x20) where terrain affects movement and combat effectiveness, with elevation, cover, and flanking playing important roles.

Unit types include:
- Infantry: Versatile ground units with balanced stats
- Cavalry: Fast-moving units with high mobility and charge bonuses
- Ranged: Units that can attack from distance
- Siege: Specialized units for attacking fortifications
- Support: Units that provide buffs, healing, or other utility

Default unit stats for prototyping:
- Hitpoints: 50
- Melee attack: 50
- Ranged attack: 40
- Melee defence: 0
- Ranged defence: 0
- Stamina: 90
- Initiative: 100
- Morale: 40

Equipment management includes weapons, armor, shields, and accessories that affect unit stats and abilities. Players can customize their units' gear based on tactical needs and available resources.

RPG progression allows units to gain experience and level up, unlocking new abilities, improving stats, or gaining special traits. This creates a sense of attachment to veteran units and strategic decisions about which units to develop.
After completing tactical combat, the game returns to the strategic layer with rewards, experience gains, and any consequences from the battle. The game supports save/load functionality for both strategic and tactical layers.


## Future Meta Layer

A third meta layer is planned for future development that will track player progression as they successfully complete strategic maps, adding a persistent progression system across multiple game sessions. This layer will include:

- Persistent character and unit progression between campaigns
- Unlockable content based on achievements and completion
- Customizable starting conditions for new campaigns
- Player statistics and performance tracking
- Achievements and milestones system
- Potential for shared or competitive elements between players

The meta layer will serve to enhance replayability by providing long-term goals and customization options that carry forward from one strategic map completion to the next.


## Core Mechanics

- Randomly generated strategic maps
- Hero movement and exploration
- Tactical combat with positioning focus
- Unit equipment and armor systems
- RPG progression for units
- Terrain-based strategic decisions

## Additional Considerations

The game will emphasize replayability through randomly generated maps and meaningful choices in unit progression and equipment management. The combination of strategic planning and tactical execution creates a satisfying gameplay loop where strategic decisions directly impact tactical capabilities and vice versa.