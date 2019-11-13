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

    def horizontal_if(self, stack):
        a = stack.pop()
        if a == 0:
            self.change_dir(Direction.RIGHT)
        else:
            self.change_dir(Direction.LEFT)

    def vertical_if(self, stack):
        a = stack.pop()
        if a == 0:
            self.change_dir(Direction.DOWN)
        else:
            self.change_dir(Direction.UP)

    def skip(self):
        self.step()


class Stack:
    def __init__(self):
        self.entries = []
        self.out = ""

    def push(self, entry):
        self.entries.append(entry)

    def pop(self):
        return self.entries.pop()

    def add(self):
        self.push(self.pop() + self.pop())

    def subtract(self):
        a = self.pop()
        b = self.pop()
        self.push(b-a)

    def multiply(self):
        self.push(self.pop() * self.pop())

    def divide(self):
        a = self.pop()
        b = self.pop()
        self.push(int(b/a))

    def modulo(self):
        a = self.pop()
        b = self.pop()
        self.push(b % a)

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

    def duplicate(self):
        a = self.pop()
        self.push(a)
        self.push(a)

    def swap(self):
        a = self.pop()
        b = self.pop()
        self.push(a)
        self.push(b)

    def print_num(self):
        a = self.pop()
        self.out += a

    def print_ascii(self):
        a = self.pop()
        self.out += chr(a)

    def pop_output(self) -> str:
        out = self.out
        self.out = ""
        return out

    def read_num(self):
        num = int(input("> "))
        self.push(num)

    def read_ascii(self):
        char = ord(input("> "))
        self.push(char)

    def __str__(self):
        return str(self.entries)


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

        for line in self.field:
            l = len(line)
            for i in range(self.max_x - l + 1):
                line.append(' ')

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
        print("==========================")

    def get_to_stack(self, stack):
        x = stack.pop()
        y = stack.pop()
        v = self.at(x, y)
        stack.push(v)

    def put_from_stack(self, stack):
        x = stack.pop()
        y = stack.pop()
        v = stack.pop()
        self.field[y][x] = chr(v)


def change_dir(dir):
    def func(cursor):
        return cursor.change_dir(dir)
    return func


cursor_handlers = {
    '>': change_dir(Direction.RIGHT),
    '<': change_dir(Direction.LEFT),
    '^': change_dir(Direction.UP),
    'v': change_dir(Direction.DOWN),
    '?': Cursor.random_dir,
    '#': Cursor.skip
}

stack_handlers = {
    '*': Stack.multiply,
    '/': Stack.divide,
    '+': Stack.add,
    '-': Stack.subtract,
    '%': Stack.modulo,
    '`': Stack.bigger_than,
    '!': Stack.logic_not,
    ':': Stack.duplicate,
    '\\': Stack.swap,
    '$': Stack.pop,
    '.': Stack.print_num,
    ',': Stack.print_ascii,
    '&': Stack.read_num,
    '~': Stack.read_ascii
}

conditional_handlers = {
    '_': Cursor.horizontal_if,
    '|': Cursor.vertical_if
}

field_handler = {
    'g': Field.get_to_stack,
    'p': Field.put_from_stack,
}


def parse(path: str):
    field = Field(read_file(path))

    cursor = Cursor(field)

    stack = Stack()

    string_mode = False

    output = ""
    running = True

    while running:
        if string_mode:
            if cursor.symbol() in ['"']:
                string_mode = False
            else:
                stack.push(ord(cursor.symbol()))
        else:
            if cursor.symbol() in cursor_handlers:
                cursor_handlers[cursor.symbol()](cursor)
            if cursor.symbol() in stack_handlers:
                stack_handlers[cursor.symbol()](stack)
            if cursor.symbol().isdigit():
                stack.push(int(cursor.symbol()))
            if cursor.symbol() in conditional_handlers:
                conditional_handlers[cursor.symbol()](cursor, stack)
            if cursor.symbol() in field_handler:
                field_handler[cursor.symbol()](field, stack)
            if cursor.symbol() in ['"']:
                string_mode = True
            if cursor.symbol() in ['@']:
                running = False

        print(stack)
        output += stack.pop_output()
        field.pretty_print()
        print(output)

        time.sleep(0.01)
        cursor.step()


if __name__ == '__main__':
    parse("file.df")
