UP = (-1, 0)
DOWN = (1, 0)
RIGHT = (0, 1)
LEFT = (0, -1)

COMMANDS = {"w": UP, "s": DOWN, "d": RIGHT, "a": LEFT}

import os
import random
import curses
import time


class EscException(Exception):
    pass


class GameOverException(Exception):
    pass


class Game:
    def __init__(self, height, width):
        self.score = 0
        self.height = height
        self.width = width
        self.snake = Snake()
        apple_position = self.random_apple_position()
        self.apple = Apple(apple_position)
        self.render()

    def random_apple_position(self):
        apple_position = tuple(self.snake.head)
        while apple_position in self.snake.body:
            apple_position = (
                random.randint(0, self.height - 1),
                random.randint(0, self.width - 1),
            )
        return apple_position

    def increase_snake_tail(self):
        current_tail = self.snake.body[-1]
        x, y = current_tail[0], current_tail[1]
        available_cells = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        available_cells = [
            cell
            for cell in available_cells
            if (
                (cell[0] > -1 and cell[0] < self.height)
                and (cell[1] > -1 and cell[1] < self.width)
            )
        ]
        self.snake.body.append(available_cells[0])

    def board_matrix(self):
        board = [[None for _ in range(self.width)] for _ in range(self.height)]
        return board

    @staticmethod
    def curses_render(stdscr, self):
        ## setting up curses colors
        stdscr.nodelay(True)
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        stdscr.clear()

        ## Game logic
        command = "X"
        try:
            command = stdscr.getkey()
        except:
            pass
        if command == "\x1b":
            raise EscException
        direction = None
        try:
            direction = COMMANDS[command]
            #stdscr.addstr(30, 10, "try direction %s" % str(direction))
        except KeyError:
            pass
            #stdscr.addstr(30, 10, "wrong command but all good %s" % str(command))
        if direction:
            self.snake.direction = direction
        # stdscr.addstr(35, 10, "snake direction debug %s" % str(self.snake.direction))
        # stdscr.addstr(36, 10, "snake head debug %s" % str(self.snake.head))
        try:
            self.update_game()
        except GameOverException:
            self.render_game_over()

        ## Re render header
        stdscr.addstr(0, 0, "#" * self.width, curses.color_pair(227))
        stdscr.addstr(1, 0, "### Score: %s ###" % self.score, curses.color_pair(227))
        stdscr.addstr(2, 0, "#" * self.width, curses.color_pair(227))

        ## Re render board
        header = 5
        stdscr.addstr(
            -1 + header, 0, "+" + "-" * self.width + "+", curses.color_pair(131)
        )
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) == self.snake.head:
                    stdscr.addstr(row + header, col + 1, "X", curses.color_pair(29))
                elif (row, col) in self.snake.body[1:]:
                    stdscr.addstr(row + header, col + 1, "O", curses.color_pair(47))
                elif (row, col) == self.apple.position:
                    stdscr.addstr(row + header, col + 1, "@", curses.color_pair(197))
                else:
                    stdscr.addstr(row + header, col + 1, " ")
            stdscr.addstr(row + header, 0, "|", curses.color_pair(131))
            stdscr.addstr(row + header, self.width + 1, "|", curses.color_pair(131))
        stdscr.addstr(
            self.height + header,
            0,
            "+" + "-" * self.width + "+",
            curses.color_pair(131),
        )

        ## Refresh whole thing and wait
        stdscr.refresh()
        time.sleep(0.15)

    def render(self):
        curses.wrapper(self.curses_render, self)

    def render_game_over(self):
        curses.wrapper(self.curses_render_game_over, self)

    @staticmethod
    def curses_render_game_over(stdscr, self):
        ## setting up curses colors
        stdscr.clear()
        stdscr.nodelay(False)
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        stdscr.addstr(5, 9, "Game Over", curses.color_pair(47))
        stdscr.addstr(6, 6, "Your score was %s" % self.score, curses.color_pair(47))
        stdscr.addstr(9, 9, "Press 'n' for new game", curses.color_pair(47))
        stdscr.addstr(10, 9, "Press 'e' to exit", curses.color_pair(47))
        stdscr.refresh()
        command = None
        while command not in ["e", "n"]:
            command = stdscr.getkey()
        if command == "e":
            raise EscException
        elif command == "n":
            self.score = 0
            self.snake = Snake(init_body=[(1, 1), (1, 0)], init_position=RIGHT)
            apple_position = self.random_apple_position()
            self.apple = Apple(apple_position)

    def update_game(self):
        next_step = (
            self.snake.head[0] + self.snake.direction[0],
            self.snake.head[1] + self.snake.direction[1],
        )
        if (
            next_step in self.snake.body
            or (next_step[0] < 0 or next_step[0] > self.height - 1)
            or (next_step[1] < 0 or next_step[1] > self.width - 1)
        ):
            raise GameOverException
        self.snake.take_step(next_step)

        if self.snake.head == self.apple.position:
            self.increase_snake_tail()
            self.score += 1
            new_apple_position = self.random_apple_position()
            self.apple = Apple(new_apple_position)

    def run(self):
        while True:
            try:
                self.render()
            except EscException:
                break
        print("##############################")
        print("### Snake -- See you soon! ###")
        print("##############################")


class Snake:
    def __init__(self, init_body=[(1, 1), (1, 0)], init_position=RIGHT):
        self.body = init_body
        self._direction = init_position

    def take_step(self, next_step):
        self.body.insert(0, next_step)
        self.body.pop(-1)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction

    @property
    def head(self):
        return self.body[0]


class Apple:
    def __init__(self, position):
        self.position = position


if __name__ == "__main__":
    game = Game(15, 30)
    game.run()
