# Snake Game Design

This document outlines the design for a classic snake game that runs in a standard terminal.

## High-Level Design

The game will be implemented in Python using the `curses` library for terminal screen handling, which works well on macOS and Linux environments like WSL2.

The core of the game will be a central game loop that orchestrates the following actions on each tick:
1.  **Process Input**: Check for and handle user input to change the snake's direction.
2.  **Update State**: Move the snake, check for collisions (with walls or itself), and handle food consumption.
3.  **Render Output**: Redraw the entire game screen in the terminal with the updated game state.

A constant game speed will be maintained by introducing a small delay at the end of each loop iteration. The speed will increase as the snake eats more food.

## Component-Based Architecture

To promote modularity and separation of concerns, the game will be built around three main components:

-   **`Game`**: The central class that manages the game's state, orchestrates the game loop, and handles user input. It will be responsible for initializing the screen, spawning the snake and food, and detecting collisions.
-   **`Snake`**: A class representing the snake. It will manage its own state, including its body segments, direction, and growth.
-   **`Food`**: A class for the food items that the snake consumes. It will be responsible for placing itself at a random location on the screen.

## Data Structures

-   The snake's body will be represented by a `deque` of coordinate tuples `(y, x)`, which will allow for efficient addition and removal of segments from both ends.
-   The food's position will be stored as a simple coordinate tuple.

## Implementation Plan

The implementation will be carried out in the following phases:

1.  **Setup the Game Environment**: Initialize the `curses` screen and set up the game window.
2.  **Implement the `Snake` Class**: Create the `Snake` class with methods to move, grow, and change direction.
3.  **Implement the `Food` Class**: Create the `Food` class with a method to spawn at a random location.
4.  **Implement the `Game` Class**:
    -   Set up the main game loop.
    -   Handle user input for snake movement.
    -   Implement collision detection (walls and self).
    -   Integrate the `Snake` and `Food` classes.
5.  **Add Scoring and Game Over**:
    -   Display the current score.
    -   Implement a "Game Over" screen with the final score.
    -   Add the option to restart the game.
