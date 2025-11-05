#!/usr/bin/env python3
"""
Enhanced Snake Game with best practices implementation.

Features:
- Explicit growth mechanism
- Pause/Quit functionality
- Difficulty progression
- High score persistence
- Comprehensive logging
- Error handling
- Terminal size validation
"""

import curses
import random
import logging
import json
import os
from collections import deque
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Game dimensions
WINDOW_HEIGHT = 20
WINDOW_WIDTH = 40
MIN_TERMINAL_HEIGHT = 22
MIN_TERMINAL_WIDTH = 42

# Initial game settings
INITIAL_SNAKE_POSITION = (5, 5)
INITIAL_SNAKE_LENGTH = 3
INITIAL_TIMEOUT = 150  # milliseconds
MIN_TIMEOUT = 50  # fastest speed

# Speed progression
SPEED_INCREASE_PER_FOOD = 5  # ms decrease per food eaten
DIFFICULTY_THRESHOLD = 5  # foods before speed increases

# Visual characters
SNAKE_HEAD_CHAR = '@'
SNAKE_BODY_CHAR = '#'
FOOD_CHAR = '*'

# File paths
HIGH_SCORE_FILE = Path.home() / '.snake_game_highscore.json'
LOG_FILE = Path.home() / '.snake_game_log.txt'

# Food spawning
MAX_SPAWN_ATTEMPTS = 1000
MIN_FOOD_DISTANCE_FROM_HEAD = 3  # minimum Manhattan distance

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging():
    """Configure comprehensive logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w'),
            logging.StreamHandler()
        ]
    )
    logging.info("=" * 60)
    logging.info("Snake Game Started")
    logging.info(f"Log file: {LOG_FILE}")
    logging.info(f"High score file: {HIGH_SCORE_FILE}")
    logging.info("=" * 60)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def load_high_score():
    """Load high score from file."""
    try:
        if HIGH_SCORE_FILE.exists():
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                logging.info(f"Loaded high score: {data['score']} from {data['date']}")
                return data['score']
    except Exception as e:
        logging.error(f"Error loading high score: {e}")
    return 0

def save_high_score(score):
    """Save high score to file."""
    try:
        data = {
            'score': score,
            'date': datetime.now().isoformat()
        }
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved new high score: {score}")
    except Exception as e:
        logging.error(f"Error saving high score: {e}")

# ============================================================================
# SNAKE CLASS
# ============================================================================

class Snake:
    """
    Represents the snake with explicit growth mechanism.
    
    The snake maintains its body as a deque and tracks positions in a set
    for O(1) collision detection.
    """
    
    # Direction opposites for preventing 180-degree turns
    OPPOSITE_DIRECTIONS = {
        curses.KEY_UP: curses.KEY_DOWN,
        curses.KEY_DOWN: curses.KEY_UP,
        curses.KEY_LEFT: curses.KEY_RIGHT,
        curses.KEY_RIGHT: curses.KEY_LEFT
    }
    
    def __init__(self, window, initial_pos=INITIAL_SNAKE_POSITION):
        """
        Initialize the Snake.
        
        Args:
            window: The curses window for drawing
            initial_pos: Starting position (y, x) tuple
        """
        self.window = window
        self.direction = curses.KEY_RIGHT
        
        # Initialize body as deque for efficient append/pop operations
        y, x = initial_pos
        self.body = deque([
            (y, x),
            (y, x - 1),
            (y, x - 2)
        ])
        
        # Maintain set of body positions for O(1) collision checks
        self.body_set = set(self.body)
        
        # Track if snake should grow on next move
        self.grow_pending = False
        
        logging.debug(f"Snake initialized at {initial_pos}, length: {len(self.body)}")
    
    @property
    def head(self):
        """Get the snake's head position."""
        return self.body[0]
    
    def change_direction(self, direction):
        """
        Change snake's direction, preventing 180-degree turns.
        
        Args:
            direction: New direction key
        """
        if direction not in self.OPPOSITE_DIRECTIONS:
            return
        
        # Prevent reversing directly into body
        if self.direction != self.OPPOSITE_DIRECTIONS[direction]:
            old_direction = self.direction
            self.direction = direction
            logging.debug(f"Direction changed: {old_direction} -> {direction}")
    
    def move(self):
        """
        Move the snake one step in current direction.
        
        Returns:
            tuple: New head position (y, x)
        """
        y, x = self.head
        
        # Calculate new head position
        if self.direction == curses.KEY_UP:
            y -= 1
        elif self.direction == curses.KEY_DOWN:
            y += 1
        elif self.direction == curses.KEY_LEFT:
            x -= 1
        elif self.direction == curses.KEY_RIGHT:
            x += 1
        
        new_head = (y, x)
        
        # Add new head
        self.body.appendleft(new_head)
        self.body_set.add(new_head)
        
        # Remove tail unless growing
        if self.grow_pending:
            self.grow_pending = False
            logging.debug(f"Snake grew to length {len(self.body)}")
        else:
            tail = self.body.pop()
            self.body_set.remove(tail)
        
        return new_head
    
    def grow(self):
        """Schedule snake to grow on next move."""
        self.grow_pending = True
        logging.debug("Growth scheduled for next move")
    
    def is_self_collision(self, pos=None):
        """
        Check if position collides with snake body (excluding head).
        
        Args:
            pos: Position to check, defaults to head position
            
        Returns:
            bool: True if collision detected
        """
        if pos is None:
            pos = self.head
        
        # Check if position is in body (excluding the head itself)
        return pos in list(self.body)[1:]
    
    def draw(self):
        """Draw the snake on the window."""
        # Draw head with distinctive character
        y, x = self.head
        try:
            self.window.addch(y, x, SNAKE_HEAD_CHAR)
        except curses.error:
            logging.error(f"Failed to draw head at ({y}, {x})")
        
        # Draw body
        for y, x in list(self.body)[1:]:
            try:
                self.window.addch(y, x, SNAKE_BODY_CHAR)
            except curses.error:
                logging.error(f"Failed to draw body segment at ({y}, {x})")

# ============================================================================
# FOOD CLASS
# ============================================================================

class Food:
    """
    Represents food with smart spawning logic.
    
    Spawns food avoiding the snake and maintaining minimum distance from head.
    """
    
    def __init__(self, window, snake):
        """
        Initialize Food.
        
        Args:
            window: The curses window for drawing
            snake: The Snake object to avoid
        """
        self.window = window
        self.position = self.spawn(snake)
    
    def spawn(self, snake):
        """
        Spawn food at a valid random location.
        
        Ensures food doesn't spawn on snake and maintains minimum distance
        from head when possible.
        
        Args:
            snake: The Snake object
            
        Returns:
            tuple: Food position (y, x)
            
        Raises:
            RuntimeError: If no valid position found after max attempts
        """
        height, width = self.window.getmaxyx()
        attempts = 0
        best_position = None
        best_distance = 0
        
        logging.debug(f"Spawning food, snake length: {len(snake.body)}")
        
        while attempts < MAX_SPAWN_ATTEMPTS:
            y = random.randint(1, height - 2)
            x = random.randint(1, width - 2)
            pos = (y, x)
            
            # Must not be on snake
            if pos in snake.body_set:
                attempts += 1
                continue
            
            # Calculate distance from head
            distance = manhattan_distance(pos, snake.head)
            
            # If far enough, use it immediately
            if distance >= MIN_FOOD_DISTANCE_FROM_HEAD:
                logging.debug(f"Food spawned at {pos}, distance from head: {distance}")
                return pos
            
            # Otherwise track best option
            if distance > best_distance:
                best_position = pos
                best_distance = distance
            
            attempts += 1
        
        # If we exhausted attempts, use best position found
        if best_position:
            logging.warning(f"Food spawned at suboptimal position {best_position}, "
                          f"distance: {best_distance}")
            return best_position
        
        # This should be extremely rare - game board nearly full
        error_msg = "Cannot find valid position for food - board may be full"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    
    def draw(self):
        """Draw the food on the window."""
        try:
            self.window.addch(self.position[0], self.position[1], FOOD_CHAR)
        except curses.error:
            logging.error(f"Failed to draw food at {self.position}")

# ============================================================================
# GAME CLASS
# ============================================================================

class Game:
    """
    Main game controller with state management and game loop.
    
    Handles:
    - Game loop and timing
    - Input processing
    - Collision detection
    - Score tracking
    - Difficulty progression
    - Pause/restart functionality
    """
    
    def __init__(self, stdscr):
        """
        Initialize the Game.
        
        Args:
            stdscr: The standard curses screen
            
        Raises:
            RuntimeError: If terminal is too small
        """
        self.stdscr = stdscr
        
        # Validate terminal size
        term_height, term_width = stdscr.getmaxyx()
        if term_height < MIN_TERMINAL_HEIGHT or term_width < MIN_TERMINAL_WIDTH:
            raise RuntimeError(
                f"Terminal too small. Need at least {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}, "
                f"got {term_width}x{term_height}"
            )
        
        logging.info(f"Terminal size: {term_width}x{term_height}")
        
        # Create game window
        self.window = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
        self.timeout = INITIAL_TIMEOUT
        self.window.timeout(self.timeout)
        self.window.keypad(True)
        
        # Initialize game state
        self.reset_game()
        self.high_score = load_high_score()
        
        logging.info("Game initialized successfully")
    
    def reset_game(self):
        """Reset game to initial state."""
        self.snake = Snake(self.window)
        self.food = Food(self.window, self.snake)
        self.score = 0
        self.timeout = INITIAL_TIMEOUT
        self.window.timeout(self.timeout)
        self.paused = False
        self.foods_eaten = 0
        
        logging.info("Game reset to initial state")
    
    def increase_difficulty(self):
        """Increase game speed as score increases."""
        if self.timeout > MIN_TIMEOUT:
            self.timeout = max(MIN_TIMEOUT, self.timeout - SPEED_INCREASE_PER_FOOD)
            self.window.timeout(self.timeout)
            logging.info(f"Difficulty increased: timeout now {self.timeout}ms")
    
    def draw_ui(self):
        """Draw the game UI including borders, score, and controls."""
        try:
            self.window.border(0)
            
            # Score display (limit width to prevent overflow)
            score_text = f"Score: {self.score}"
            if len(score_text) > WINDOW_WIDTH - 4:
                score_text = f"S:{self.score}"
            self.window.addstr(0, 2, score_text)
            
            # High score
            high_score_text = f"High: {self.high_score}"
            self.window.addstr(0, WINDOW_WIDTH - len(high_score_text) - 2, high_score_text)
            
            # Speed indicator
            speed_text = f"Speed: {self.timeout}ms"
            self.window.addstr(WINDOW_HEIGHT - 1, 2, speed_text)
            
            # Pause indicator
            if self.paused:
                pause_text = "PAUSED"
                self.window.addstr(WINDOW_HEIGHT // 2, 
                                 (WINDOW_WIDTH - len(pause_text)) // 2, 
                                 pause_text, 
                                 curses.A_BOLD)
        except curses.error:
            logging.error("Error drawing UI")
    
    def handle_input(self):
        """
        Process user input.
        
        Returns:
            str: Command ('quit', 'pause', or None)
        """
        key = self.window.getch()
        
        if key == -1:  # No input
            return None
        
        # Quit keys
        if key == ord('q') or key == 27:  # 'q' or ESC
            logging.info("User requested quit")
            return 'quit'
        
        # Pause key
        if key == ord('p') or key == ord(' '):
            self.paused = not self.paused
            logging.info(f"Game {'paused' if self.paused else 'resumed'}")
            return 'pause'
        
        # Direction keys
        if not self.paused:
            self.snake.change_direction(key)
        
        return None
    
    def check_collision(self):
        """
        Check for wall or self collisions.
        
        Returns:
            bool: True if collision detected
        """
        height, width = self.window.getmaxyx()
        y, x = self.snake.head
        
        # Wall collision
        if y <= 0 or y >= height - 1 or x <= 0 or x >= width - 1:
            logging.info(f"Wall collision at ({y}, {x})")
            return True
        
        # Self collision
        if self.snake.is_self_collision():
            logging.info(f"Self collision at ({y}, {x})")
            return True
        
        return False
    
    def update_game_state(self):
        """Update game state for one frame."""
        if self.paused:
            return
        
        # Move snake
        self.snake.move()
        
        # Check for food consumption
        if self.snake.head == self.food.position:
            self.score += 1
            self.foods_eaten += 1
            logging.info(f"Food eaten! Score: {self.score}")
            
            self.snake.grow()
            
            try:
                self.food = Food(self.window, self.snake)
            except RuntimeError as e:
                logging.error(f"Cannot spawn food: {e}")
                # Game essentially won - board is full
                return
            
            # Increase difficulty periodically
            if self.foods_eaten % DIFFICULTY_THRESHOLD == 0:
                self.increase_difficulty()
    
    def show_game_over(self):
        """Display game over screen and handle restart/quit."""
        self.window.clear()
        self.window.border(0)
        
        # Check for new high score
        new_high_score = False
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.score)
            new_high_score = True
        
        # Display messages
        messages = [
            "GAME OVER!",
            "",
            f"Final Score: {self.score}",
            f"High Score: {self.high_score}",
            "",
        ]
        
        if new_high_score:
            messages.append("NEW HIGH SCORE!")
            messages.append("")
        
        messages.extend([
            "Press 'R' to Restart",
            "Press 'Q' to Quit"
        ])
        
        # Center and display messages
        start_y = (WINDOW_HEIGHT - len(messages)) // 2
        for i, msg in enumerate(messages):
            x = (WINDOW_WIDTH - len(msg)) // 2
            try:
                attr = curses.A_BOLD if "GAME OVER" in msg or "NEW HIGH SCORE" in msg else 0
                self.window.addstr(start_y + i, x, msg, attr)
            except curses.error:
                pass
        
        self.window.refresh()
        self.window.nodelay(False)
        
        # Wait for restart or quit
        while True:
            key = self.window.getch()
            if key == ord('q') or key == ord('Q') or key == 27:
                logging.info("User chose to quit")
                return False
            elif key == ord('r') or key == ord('R'):
                logging.info("User chose to restart")
                return True
    
    def run(self):
        """
        Run the main game loop.
        
        Returns:
            bool: True if game should restart, False to quit
        """
        logging.info(f"Starting game loop (timeout: {self.timeout}ms)")
        
        try:
            while True:
                # Clear and redraw
                self.window.clear()
                self.draw_ui()
                self.snake.draw()
                self.food.draw()
                self.window.refresh()
                
                # Handle input
                command = self.handle_input()
                if command == 'quit':
                    return False
                
                # Update game state
                self.update_game_state()
                
                # Check for collisions
                if self.check_collision():
                    return self.show_game_over()
                    
        except Exception as e:
            logging.error(f"Error in game loop: {e}", exc_info=True)
            raise

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main(stdscr):
    """
    Main entry point for the game.
    
    Args:
        stdscr: The standard curses screen
    """
    # Configure curses
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    try:
        # Create and run game
        game = Game(stdscr)
        
        # Game loop with restart capability
        while True:
            should_restart = game.run()
            if not should_restart:
                break
            
            # Reset for new game
            game.reset_game()
            
    except RuntimeError as e:
        # Handle terminal size errors gracefully
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error: {e}")
        stdscr.addstr(1, 0, "Press any key to exit...")
        stdscr.nodelay(False)
        stdscr.getch()
        logging.error(f"Game terminated: {e}")
    
    except Exception as e:
        # Log unexpected errors
        logging.error(f"Unexpected error: {e}", exc_info=True)
        raise
    
    finally:
        logging.info("Game ended")
        logging.info("=" * 60)

def entry_point():
    """Entry point with comprehensive error handling."""
    try:
        setup_logging()
        curses.wrapper(main)
    except KeyboardInterrupt:
        logging.info("Game interrupted by user (Ctrl+C)")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error occurred. Check log file: {LOG_FILE}")
        raise

if __name__ == "__main__":
    entry_point()