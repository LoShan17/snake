UP = (-1, 0)
DOWN = (1, 0)
RIGHT = (0, 1)
LEFT = (0, -1)

COMMANDS = {"w": UP, "s": DOWN, "d": RIGHT, "a": LEFT}

import os
import random
import curses
import time


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
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        stdscr.clear()
        stdscr.addstr(0, 0, "curses text", curses.color_pair(47)) # bright g
        stdscr.addstr(1, 10, "curses text row 2", curses.color_pair(29)) # dark g
        stdscr.addstr(2, 0, "curses text row 3", curses.color_pair(197)) # red
        stdscr.addstr(3, 10, "try width and height %s and %s" % (self.width, self.height), curses.color_pair(131)) # brown
        stdscr.addstr(4, 0, "try snake head %s" % str(self.snake.head), curses.color_pair(227)) # yellow
        stdscr.addstr(5, 10, "try apple %s" % str(self.apple.position))
        stdscr.addstr(6, 0, "try score %s" % str(self.score))
        stdscr.addstr(7, 0, "PRESS ANY KEY...")
        stdscr.refresh()
        time.sleep(7)
        command = stdscr.getkey()
        try:
            direction = COMMANDS[command]
            stdscr.addstr(10, 10, "try direction %s" % str(direction))
        except KeyError:
            stdscr.addstr(10, 10, "wrong command but all good %s" % str(command))
        stdscr.refresh()
        time.sleep(7)


    def render(self):
        #curses.wrapper(self.curses_render, self)
        os.system("clear")
        print("############################")
        print("######## SCORE: %s ########" % self.score)
        print("+" + "-" * self.width + "+")
        for row in range(self.height):
            string_row = ""
            for col in range(self.width):
                if (row, col) == self.snake.head:
                    string_row += "X"
                elif (row, col) in self.snake.body[1:]:
                    string_row += "O"
                elif (row, col) == self.apple.position:
                    string_row += "*"
                else:
                    string_row += " "
            print("|%s|" % string_row)
        print("+" + "-" * self.width + "+")

    def run(self):
        while True:
            command = input()
            if command == "\x1b":
                break
            try:
                direction = COMMANDS[command]
            except KeyError:
                continue
            self.snake.direction = direction
            next_step = (
                self.snake.head[0] + self.snake.direction[0],
                self.snake.head[1] + self.snake.direction[1],
            )
            if (
                next_step in self.snake.body
                or (next_step[0] < 0 or next_step[0] > self.height - 1)
                or (next_step[1] < 0 or next_step[1] > self.width - 1)
            ):
                print("#################")
                print("### Game Over ###")
                print("#################")
                break
            self.snake.take_step(next_step)
            if self.snake.head == self.apple.position:
                self.increase_snake_tail()
                self.score += 1
                new_apple_position = self.random_apple_position()
                self.apple = Apple(new_apple_position)
            self.render()


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
    game = Game(10, 20)
    game.run()
