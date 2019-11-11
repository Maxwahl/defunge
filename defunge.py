import random
import time
from enum import Enum


class bcolors:
    HIGHTLIGHT = '\033[7m'
    END = '\033[0m'


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def vector(self):
        if self == Direction.UP:
            return [0, -1]
        elif self == Direction.DOWN:
            return [0, 1]
        elif self == Direction.LEFT:
            return [-1, 0]
        elif self == Direction.RIGHT:
            return [1, 0]
        else:
            raise RuntimeError("WTF")


class Cursor:
    def __init__(self, field):
        self.x = 0
        self.y = 0
        self.field = field
        self.field.cursor = self
        self.direction = Direction.RIGHT

    def step(self):
        self.x += self.direction.vector()[0]
        self.y += self.direction.vector()[1]
        if self.x > self.field.max_x:
            self.x = 0
        if self.y > self.field.max_y:
            self.y = 0

    def symbol(self):
        return self.field.at(self.x, self.y)

    def change_dir(self, direction):
        self.direction = direction

    def random_dir(self):
        self.direction = random.choice(list(Direction))

    def __str__(self):
        return f"C[{self.x} {self.y}]"


class Stack:
    def __init__(self):
        self.entries = []

    def push(self, entry):
        self.entries.append(entry)

    def pop(self):
        return self.entries.pop()

    def add(self):
        self.push(self.pop() + self.pop())

    def subtract(self):
        self.push(self.pop() - self.pop())

    def multiply(self):
        self.push(self.pop() * self.pop())

    def divide(self):
        self.push(self.pop() / self.pop())

    def modulo(self):
        self.push(self.pop() % self.pop())

    def logic_not(self):
        if self.pop() == 0:
            self.push(1)
        else:
            self.push(0)

    def bigger_than(self):
        if self.pop() > self.pop():
            self.push(1)
        else:
            self.push(0)





def read_file(path: str):
    with open(path, 'r') as file:
        lines = file.readlines()
        ret = list(map(lambda s: list(s), lines))
        for sentence in ret:
            for index, symbol in enumerate(sentence):
                if symbol in ["\n"]:
                    del sentence[index]
        return ret




class Field:
    def __init__(self, field):
        self.field = field

        self.max_y = len(self.field)-1
        self.max_x = max(map(len, self.field))-1

        self.cursor = None

    def at(self, x, y):
        return self.field[y][x]

    def pretty_print(self):
        for y, line in enumerate(self.field):
            for x, symbol in enumerate(line):
                if x == self.cursor.x and y == self.cursor.y:
                    print(f"{bcolors.HIGHTLIGHT}{symbol}{bcolors.END}", end='', flush=False)
                else:
                    print(symbol, end='', flush=False)
            print(flush=False)
        print()


def change_dir(dir):
    def func(cursor):
        return cursor.change_dir(dir)
    return func


handlers = {
    '>': change_dir(Direction.RIGHT),
    '<': change_dir(Direction.LEFT),
    '^': change_dir(Direction.UP),
    'v': change_dir(Direction.DOWN),
    '?': Cursor.random_dir
}


def parse(path: str):
    field = Field(read_file(path))

    cursor = Cursor(field)

    while True:
        cursor.step()

        if cursor.symbol() in handlers:
            handlers[cursor.symbol()](cursor)

        print(cursor)
        print(cursor.symbol())
        field.pretty_print()
        time.sleep(0.1)


if __name__ == '__main__':
    parse("file.df")
