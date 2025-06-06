"""
This text provides an example of using docstrings.
"""

import logging


class MyClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def greet(name: str, age: int) -> str:
    print(f"__name__: {__name__}")
    return f"Hello, {name}. You are {age} years old."


def main():
    print(f"greet.__annotations__: {greet.__annotations__}")
    print(f"__doc__: {__doc__}")
    print(f"__file__: {__file__}")
    print(f"__name__: {__name__}")

    print(f"MyClass.__dict__: {MyClass.__dict__}")

    # Create an instance of MyClass
    myClassObj = MyClass(10, 20)

    # Access the __dict__ attribute of the instance
    print(f"obj.__dict__: {myClassObj.__dict__}")

    print(f"logging.__dict__.keys(): {logging.__dict__.keys()}")

    print("__builtins__")
    for builtin in dir(__builtins__):
        print(builtin)


if __name__ == "__main__":
    main()
