#!/usr/bin/env python3.7
"""
An example usage of clii.
"""
from clii import App

cli = App(description=__doc__)


@cli.cmd
@cli.arg('a', '-a', help='The value a')
def sum_(a, b: int, c: int = 0) -> int:
    """Sum two numbers."""
    print(a + b + c)
    return a + b + c


@cli.cmd
def divide(a: int = 0, b: int = 1) -> float:
    """Divide two numbers."""
    print(a / b)
    return a / b


if __name__ == '__main__':
    cli.run()
