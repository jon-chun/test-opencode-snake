# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A classic Snake game implementation in Python using the `curses` library. The repository contains two implementations of varying complexity, both terminal-based games that run on macOS and Linux (including WSL2).

## Game Implementations

### snake-game_claude45ui.py (Recommended)
The enhanced, production-ready implementation with:
- Explicit growth mechanism using `grow_pending` flag
- Pause/resume functionality (P or Space)
- Difficulty progression (speed increases every 5 foods)
- High score persistence (~/.snake_game_highscore.json)
- Comprehensive logging (~/.snake_game_log.txt)
- Terminal size validation (requires 42x22 minimum)
- Smart food spawning with Manhattan distance checks
- Error handling and recovery

### snake-game_kilo-code.py
A simpler, more straightforward implementation demonstrating basic game mechanics without the advanced features.

## Running the Game

```bash
# Install dependencies (currently none required beyond standard library)
pip install -r requirements.txt

# Run the enhanced version
python snake-game_claude45ui.py

# Run the simple version
python snake-game_kilo-code.py
```

## Architecture

Both implementations follow a component-based architecture with three main classes:

### Snake Class
- **Body representation**: `deque` of (y, x) coordinate tuples for O(1) append/pop
- **Body set**: Parallel set for O(1) collision detection
- **Direction system**: Uses curses key constants, prevents 180° turns
- **Growth mechanism**:
  - Enhanced version: `grow_pending` flag, grows on next move
  - Simple version: Growth handled by not calling `shrink()`

### Food Class
- **Spawning logic**: Random placement avoiding snake body
- **Enhanced version**: Maintains MIN_FOOD_DISTANCE_FROM_HEAD (3 tiles) from head when possible
- **Fallback**: Tracks best position if ideal spawn location unavailable

### Game Class
- **Game loop**: Process input → Update state → Render → Check collisions
- **Timing**: `window.timeout()` controls game speed
- **Enhanced version**:
  - Speed progression: Decreases timeout by 5ms per food (every 5 foods)
  - Min timeout: 50ms (maximum speed)
  - Pause state management

## Key Design Patterns

### Collision Detection
- **Wall collision**: Check if head is at/beyond window borders (0 or max-1)
- **Self collision**: Check if head position in body[1:] (excluding head itself)

### Movement System
Direction changes processed before move to allow responsive controls. The snake moves by:
1. Calculate new head position based on current direction
2. Add new head to front of deque
3. Remove tail from deque (unless growing)

### Coordinate System
- Uses curses (y, x) convention where y is vertical, x is horizontal
- Origin (0,0) is top-left
- Game area is bordered, playable area is 1 to (max-2)

## Configuration Constants (Enhanced Version)

Located at top of snake-game_claude45ui.py:
- `WINDOW_HEIGHT/WIDTH`: Game window dimensions (20x40)
- `INITIAL_TIMEOUT`: Starting speed (150ms)
- `MIN_TIMEOUT`: Maximum speed limit (50ms)
- `SPEED_INCREASE_PER_FOOD`: Speed increment (5ms decrease)
- `DIFFICULTY_THRESHOLD`: Foods before speed increase (5)
- Visual characters: `@` (head), `#` (body), `*` (food)

## Development Notes

### Code Style
- Type hints for function signatures
- Google-style docstrings
- snake_case for variables/functions, PascalCase for classes
- Imports: standard library, third-party, first-party (isort compatible)

### Testing
No test suite currently implemented. When adding tests:
- Use `pytest` framework
- Run all tests: `pytest`
- Run specific test: `pytest tests/test_file.py::test_function`

### Linting/Formatting
- Linter: `ruff check .`
- Formatter: `ruff format .`

## Design Documentation

See DESIGN.md for detailed design philosophy including:
- Component-based architecture rationale
- Data structure choices (deque for snake body)
- Implementation phases and planning

## Virtual Environment

A `.venv` directory exists with Python 3.11. Activate with:
```bash
source .venv/bin/activate
```
