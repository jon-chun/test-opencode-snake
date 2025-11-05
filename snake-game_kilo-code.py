"""A simple snake game implemented using the curses library."""
import curses
import random
from collections import deque

class Snake:
    """
    Represents the snake in the game.
    """
    def __init__(self, window):
        """
        Initializes the Snake object.

        Args:
            window: The curses window the snake will be drawn in.
        """
        self.window = window
        self.body = deque([(5, 5), (5, 4), (5, 3)])
        self.direction = curses.KEY_RIGHT
        self.head = self.body[0]

    def change_direction(self, direction):
        """
        Changes the snake's direction.
        """
        if direction in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            # Prevent the snake from reversing on itself
            if (direction == curses.KEY_UP and self.direction != curses.KEY_DOWN) or \
               (direction == curses.KEY_DOWN and self.direction != curses.KEY_UP) or \
               (direction == curses.KEY_LEFT and self.direction != curses.KEY_RIGHT) or \
               (direction == curses.KEY_RIGHT and self.direction != curses.KEY_LEFT):
                self.direction = direction

    def move(self):
        """
        Moves the snake one step in its current direction.
        """
        y, x = self.head
        if self.direction == curses.KEY_UP:
            y -= 1
        elif self.direction == curses.KEY_DOWN:
            y += 1
        elif self.direction == curses.KEY_LEFT:
            x -= 1
        elif self.direction == curses.KEY_RIGHT:
            x += 1
        
        self.head = (y, x)
        self.body.appendleft(self.head)

    def grow(self):
        """
        Makes the snake grow by one segment.
        Note: Growth is handled by not removing the tail segment.
        """
        pass # The tail is not popped, so the snake grows.

    def shrink(self):
        """
        Shrinks the snake by removing the tail segment.
        """
        return self.body.pop()

    def draw(self):
        """
        Draws the snake on the window.
        """
        for y, x in self.body:
            self.window.addch(y, x, '#')

class Food:
    """
    Represents the food in the game.
    """
    def __init__(self, window, snake_body):
        """
        Initializes the Food object.

        Args:
            window: The curses window the food will be drawn in.
            snake_body: A deque representing the snake's body.
        """
        self.window = window
        self.position = self.spawn(snake_body)

    def spawn(self, snake_body):
        """
        Spawns food at a random location on the screen, avoiding the snake.
        """
        height, width = self.window.getmaxyx()
        while True:
            y = random.randint(1, height - 2)
            x = random.randint(1, width - 2)
            if (y, x) not in snake_body:
                return y, x

    def draw(self):
        """
        Draws the food on the window.
        """
        self.window.addch(self.position[0], self.position[1], '*')

class Game:
    """
    Manages the game state and main loop.
    """
    def __init__(self, stdscr):
        """
        Initializes the Game object.

        Args:
            stdscr: The standard screen object from curses.
        """
        self.stdscr = stdscr
        self.window = curses.newwin(20, 40, 0, 0)
        self.window.timeout(150)
        self.snake = Snake(self.window)
        self.food = Food(self.window, self.snake.body)
        self.score = 0

    def run(self):
        """
        Runs the main game loop.
        """
        while True:
            self.window.clear()
            self.window.border(0)
            self.snake.draw()
            self.food.draw()
            self.window.addstr(0, 2, f"Score: {self.score}")

            key = self.window.getch()
            if key != -1:
                self.snake.change_direction(key)

            self.snake.move()

            if self.snake.head == self.food.position:
                self.score += 1
                self.snake.grow()
                self.food = Food(self.window, self.snake.body)
            else:
                self.snake.shrink()

            if self._is_collision():
                self.window.addstr(9, 10, "Game Over!")
                self.window.addstr(10, 6, f"Final Score: {self.score}")
                self.window.nodelay(False)
                self.window.getch()
                break

    def _is_collision(self):
        """
        Checks for collisions with the wall or the snake's own body.
        """
        height, width = self.window.getmaxyx()
        y, x = self.snake.head
        if y <= 0 or y >= height - 1 or x <= 0 or x >= width - 1:
            return True
        if self.snake.head in list(self.snake.body)[1:]:
            return True
        return False

def main(stdscr):
    """
    Main function to run the snake game.

    Args:
        stdscr: The standard screen object from curses.
    """
    curses.curs_set(0)
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)