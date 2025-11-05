# Snake Game

A classic Snake game implementation in Python using the `curses` library for terminal-based gameplay. Works on macOS and Linux (including WSL2).

## Features

- 🎮 Two implementations: simple and enhanced
- 🏆 High score persistence
- ⚡ Progressive difficulty (speed increases as you eat)
- ⏸️ Pause/resume functionality
- 📊 Comprehensive logging for debugging
- 🎯 Smart food spawning algorithm

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd test-opencode-snake

# Activate virtual environment (optional)
source .venv/bin/activate

# Install dependencies (currently none required)
pip install -r requirements.txt

# Run the enhanced version
python snake-game_claude45ui.py

# Or run the simple version
python snake-game_kilo-code.py
```

## Game Controls

- **Arrow Keys**: Move the snake (Up, Down, Left, Right)
- **P** or **Space**: Pause/Resume game
- **Q** or **ESC**: Quit game
- **R**: Restart after game over

## Implementations

### Enhanced Version (`snake-game_claude45ui.py`)

The production-ready implementation with advanced features:

- **Explicit growth mechanism**: Uses a `grow_pending` flag for predictable behavior
- **Difficulty progression**: Speed increases every 5 foods eaten (150ms → 50ms minimum)
- **High score tracking**: Persists to `~/.snake_game_highscore.json`
- **Debug logging**: Comprehensive logs saved to `~/.snake_game_log.txt`
- **Terminal validation**: Requires minimum 42x22 terminal size
- **Smart food spawning**: Maintains 3-tile Manhattan distance from head when possible
- **Error handling**: Graceful recovery from edge cases

### Simple Version (`snake-game_kilo-code.py`)

A straightforward implementation demonstrating core game mechanics without the bells and whistles. Great for learning or as a starting point for modifications.

## Architecture

The game follows a component-based architecture with three main classes:

### `Snake` Class
- Body represented as a `deque` of (y, x) coordinates for efficient O(1) operations
- Parallel set for O(1) collision detection
- Prevents 180° direction reversals
- Explicit growth mechanism (enhanced version)

### `Food` Class
- Random spawning that avoids snake body
- Smart positioning to maintain distance from head (enhanced version)
- Fallback logic for crowded boards

### `Game` Class
- Main game loop: Input → Update → Render → Collision Check
- Speed control via `window.timeout()`
- State management for pause, score, and difficulty
- Game over and restart handling

## Configuration

Key constants in `snake-game_claude45ui.py`:

```python
WINDOW_HEIGHT = 20          # Game window height
WINDOW_WIDTH = 40           # Game window width
INITIAL_TIMEOUT = 150       # Starting speed (ms)
MIN_TIMEOUT = 50            # Maximum speed (ms)
SPEED_INCREASE_PER_FOOD = 5 # Speed increment (ms decrease)
DIFFICULTY_THRESHOLD = 5    # Foods before speed increase
```

Visual characters:
- `@` - Snake head
- `#` - Snake body
- `*` - Food

## Development

### Code Style
- Type hints for all function signatures
- Google-style docstrings
- `snake_case` for variables/functions, `PascalCase` for classes
- isort-compatible import ordering

### Testing
```bash
# Run all tests (when implemented)
pytest

# Run specific test
pytest tests/test_file.py::test_function
```

### Linting & Formatting
```bash
# Check code quality
ruff check .

# Format code
ruff format .
```

## Files

- `snake-game_claude45ui.py` - Enhanced implementation with all features
- `snake-game_kilo-code.py` - Simple implementation
- `DESIGN.md` - Detailed design documentation
- `AGENTS.md` - AI coding agent instructions
- `CLAUDE.md` - Claude Code context and guidance
- `requirements.txt` - Python dependencies (currently empty)

## Technical Details

### Coordinate System
- Uses curses (y, x) convention: y=vertical, x=horizontal
- Origin (0,0) at top-left
- Playable area: 1 to (dimension-2) due to borders

### Collision Detection
- **Wall collision**: Head at/beyond borders (0 or max-1)
- **Self collision**: Head position in body[1:] (excludes head)

### Movement Mechanics
1. Calculate new head position based on direction
2. Add new head to front of deque
3. Remove tail (unless growing)

## License

See repository license file.

## Contributing

Contributions welcome! Please follow the code style guidelines in AGENTS.md.
