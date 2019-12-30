# clii

A dead simple way to generate a CLI (via argparse) using Python 3.7+ function
annotations.

Right now it's nearly featureless, but it does support subcommands! See
`test_clii.py` for more details.

It has no dependencies and is implemented in a single file to be suitable for
vendoring if you don't want to deal with PyPI -- just yank `clii.py` and 
stick it somewhere in your project.

## Installation

```sh
python3.7 -m pip install --user clii
```

## Usage

```python
from clii import App, Arg

cli = App(description=__doc__)


@cli.main
def say_hello(name: str, 
              greeting: Arg('-g', str, 'Greeting to use') = 'hello'):
    """Greet somebody."""
    print(f'{greeting}, {name}')


if __name__ == '__main__':
    cli.run() 
```

gives you

```sh
$ ./test_hello.py -h

usage: test_hello.py [-h] [--greeting GREETING] name

Greet somebody.

positional arguments:
  name

  optional arguments:
    -h, --help            show this help message and exit
    --greeting GREETING, -g GREETING
                            Greeting to use. Default: hello
```
