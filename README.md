# clii

Okay, you and I both know the last thing that anyone needs is another way to
generate command line interfaces. The idea of adding an additional dependency
to your project just so you can learn yet another
only-slightly-more-ergonomic-than-stdlib interface for parsing args is right up
there with rewriting all your Makefiles in whatever flavor-of-the-week
Javascript-based build system. Don't do it.

Yes, instead of writing this library I should probably do something actually
useful like try to find a life partner or see how much grain alcohol I can
drink within the span of an X-Files episode, but each time I'm typing out some
overly verbose `argparse` incantation that I had to look up on docs.python.org
for the fourth time in a year, one of the few remaining shreds of childlike
wonder for computing left in my over-caffeinated heart gets crosslegged and
sets itself on fire.

[Click](https://click.palletsprojects.com/en/7.x/) sucks. It's a lot of code
and the interface is dogshit. [Docopt](https://github.com/docopt/docopt) is
neat but it's slow, a novelty, also a ton of code, and I have to read 3
examples each time before I use it.
[Argparse](https://docs.python.org/3/library/argparse.html) is an alright
builtin, and the noble progenitor of this library, but it's overly verbose and
wiring up subparsers that call functions is a pain.

Don't immolate the childlike wonder. Use function annotations. Use my stupid
library.

- **No dependencies.** This library has no dependencies and is a single file.
  You wanna vendor it? Vendor it.

- **Short implementation.** Take 10 minutes, skim the implementation, convince
  yourself I'm not exfiltrating your `id_rsa`, then vendor this puppy and never
  think about anything again.

- **Nothing to learn.** if you know how to use Python function annotations, you
  already know 98% of this library. 

- **Optimized for the common case.** Check out `test_bad_git.py`. I know what
  you want to do (create a subpar reproduction of git), and I've made it
  concise. 


## Installation

```sh
# Requires Python >=3.7
python3 -m pip install --user clii
```

## Substantial usage example

```python
#!/usr/bin/env python3.8
"""
A really lame version of git.
"""

from pathlib import Path
import typing as t

from clii import App, Arg


cli = App(description=__doc__)
cli.add_arg('--verbose', '-v', action='store_true', default=False)


@cli.cmd
def clone(url: str, target: Path, branch: t.Optional[str] = None):
    branch = f' -b {branch}' if branch else ''

    # We can reference global args since all parsed arguments are attached
    # to `cli.args` after parsing.
    if cli.args.verbose:
        print(f'git clone{branch} {url} {target}')


@cli.cmd
def push(remote: str, branch: str, force: bool = False):
    force_flag = ' -f' if force else ''

    if cli.args.verbose:
        print(f'git push{force_flag} {remote} {branch}')


@cli.cmd
def commit(all: Arg('-a', bool) = False,
           message: Arg('-m', str) = None):
    # Arguments are --all, -a and --message, -m
    print(all)
    print(message)


@cli.cmd
def add(*files, updated: Arg('-u', bool) = False):
    # `files` will be a variadic positional arg, while --updated/-u is a bool
    # flag.
    if cli.args.verbose:
        print(f"adding files: {files}")



if __name__ == '__main__':
    cli.run() 
```
