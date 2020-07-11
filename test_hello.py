#!/usr/bin/env python3.7
from clii import App, Arg

cli = App(description=__doc__)
cli.add_arg('--verbose', '-v', action='store_true', default=False)


@cli.main
def say_hello(name: str,
              greeting: Arg('-g', str, 'Greeting to use') = 'sup',
              num_times: int = 1):
    """Reach out and greet somebody."""
    for _ in range(num_times):
        print(f'{greeting}, {name}')


if __name__ == '__main__':
    cli.run()
