#!/usr/bin/env python3.7
from clii import App, Arg

cli = App(description=__doc__)


@cli.main
def say_hello(name: str,
              greeting: Arg('-g', str, 'Greeting to use') = 'hello'):
    """Greet somebody."""
    print(f'{greeting}, {name}')


if __name__ == '__main__':
    cli.run()
