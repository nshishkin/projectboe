# AI-Assisted Coding Workflow Guide(this guide is for user who interacts with AI,not for AI itself)

## Understanding the AI Coding Environment

### Tool-Based System
The AI operates through a tool-based system where specific actions are performed through dedicated tools:
- `read_file`: View existing code content
- `write_to_file`: Create new files or completely rewrite existing ones
- `apply_diff`: Make surgical changes to existing code
- `search_files`: Find code patterns across the project
- `execute_command`: Run system commands like installing packages or running scripts
- `list_files`: See directory contents
- `insert_content`: Add new content at specific line numbers
- `search_and_replace`: Find and replace text patterns

### Modes Explained
- **Code Mode**: For writing, modifying, and refactoring code
- **Architect Mode**: For planning, design, and system architecture
- **Ask Mode**: For explanations, documentation, and general questions
- **Debug Mode**: For troubleshooting and issue diagnosis

## Best Practices for AI-Assisted Coding

### 1. Project Structure
- Organize your code in a logical directory structure
- Keep related files together (e.g., all game components in a `game/` directory)
- Use descriptive file names that clearly indicate their purpose
- Maintain a clean separation between different game layers (strategic, tactical, meta)

### 2. Prompt Strategies
- **Specific Requests**: Instead of "make a game," say "create a Pygame window with a 10x10 grid for tactical combat"
- **Contextual Prompts**: Reference existing files or code when making changes
- **Step-by-Step**: Break complex features into smaller, manageable tasks
- **Include Constraints**: Mention performance, compatibility, or design requirements

### 3. File Organization for BoE
```
projectboe/
├── main.py                 # Main game entry point
├── config/
│   ├── settings.py         # Game settings and constants
│   └── constants.py        # Global constants
├── game/
│   ├── __init__.py
│   ├── tactical/
│   │   ├── __init__.py
│   │   ├── grid.py         # Grid system for tactical combat
│   │   ├── unit.py         # Unit class and behaviors
│   │   └── combat.py       # Combat mechanics
│   ├── strategic/
│   │   ├── __init__.py
│   │   ├── map.py          # Strategic map with provinces
│   │   ├── province.py     # Province/node class
│   │   └── hero.py         # Hero movement and management
│   └── core/
│       ├── __init__.py
│       ├── game.py         # Main game class
│       ├── renderer.py     # Rendering system
│       └── state.py        # Game state management
├── assets/
│   ├── images/             # Sprites and textures
│   ├── sounds/             # Audio files
│   └── fonts/              # Font files
├── data/
│   ├── maps/               # Map data files
│   └── units/              # Unit definitions
└── tests/                  # Unit tests
```

### 4. Working with Code Changes
- **Small Iterative Changes**: Make small changes and test frequently
- **Use apply_diff for Modifications**: When modifying existing code, use `apply_diff` to make targeted changes
- **Use write_to_file for New Files**: When creating entirely new files, use `write_to_file`
- **Review Before Applying**: Always review suggested changes before confirming

### 5. Common Pygame Patterns for BoE
When working with Pygame for your strategy game, expect to work with patterns like:

- **Game Loop Structure**:
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update game state
        # Render game objects
        pygame.display.flip()
        clock.tick(FPS)
```

- **Grid-Based Systems**: For tactical combat and strategic maps
- **State Management**: Switching between strategic and tactical layers
- **Sprite Management**: Handling game units and visual elements

### 6. Error Handling and Debugging
- The AI will help identify and fix syntax errors
- For logical errors, provide specific examples of what's not working
- Include error messages when asking for help with bugs
- Test code segments before implementing them fully

### 7. Communication Tips
- Be specific about what you want to achieve
- Share relevant code when asking for modifications
- Mention when you're stuck on a particular approach
- Ask for explanations of concepts you don't understand
- Request examples when learning new patterns

### 8. Version Control Considerations
- The AI doesn't directly interact with Git, so you'll need to manage version control separately
- Make backups of important code before major changes
- Consider implementing version control as your project grows

This workflow will help you maximize the effectiveness of AI-assisted coding while building your BoE game with Pygame.