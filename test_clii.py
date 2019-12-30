#!/usr/bin/env python3.7
"""
An example usage of clii.
"""
from clii import App, Arg

cli = App(description=__doc__)


@cli.subcommand
def sum_(a: Arg('-a', int, "The value a"), b: int, c: int = 0) -> int:
    """Sum two numbers."""
    print(a + b + c)
    return a + b + c


@cli.subcommand
def divide(a: int = 0, b: int = 1) -> float:
    """Divide two numbers."""
    print(a / b)
    return a / b


def many_int(s: str) -> [int]:
    return [int(i) for i in s.split(',')]


@cli.subcommand
def sum_many(args: Arg('ints', many_int, "Ints to sum")) -> int:
    """Sum an arbitrary number of ints."""
    print(sum(args))
    return sum(args)


if __name__ == '__main__':
    cli.run()
