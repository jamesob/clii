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
    """Clone the branch so you can melt your computer."""
    branch = f' -b {branch}' if branch else ''

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

    print(all)
    print(message)


@cli.cmd
def add(*files, updated: Arg('-u', bool) = False):
    if cli.args.verbose:
        print(f"adding files: {files}")



if __name__ == '__main__':
    cli.run()
