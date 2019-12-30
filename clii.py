"""
clii

The easiest damned argparse wrapper there ever was.


Copyright 2019 James O'Beirne

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
import functools
import inspect
import typing as t
import logging

logger = logging.getLogger('clii')


class Arg:
    def __init__(self,
                 name_or_flags: t.Union[str, t.Sequence[str]],
                 type: object = str,
                 help: str = '',
                 default: object = inspect.Parameter.empty,
                 is_kwarg: bool = False,
                 ):
        self.all_names = []

        if isinstance(name_or_flags, str):
            self.name = name_or_flags
            self.all_names.append(self.name)
        else:
            self.name = name_or_flags[0]
            self.all_names = list(name_or_flags)

        self.type = type
        self.default = default
        self.is_kwarg = is_kwarg
        self.help = help

    @classmethod
    def from_parameter(cls, param: inspect.Parameter) -> 'Arg':
        type = param.annotation
        arg = None

        def is_kwarg(p):
            return p.default != inspect.Parameter.empty

        if isinstance(type, cls):
            # User already specified an Arg, just use that.
            arg = type
            arg.is_kwarg = is_kwarg(param)
            arg.default = param.default
            arg.update_name(param.name)
            return arg
        return cls(
            param.name,
            type=param.annotation,
            default=param.default,
            is_kwarg=is_kwarg(param),
        )

    @classmethod
    def from_func(cls, func: t.Callable) -> t.Sequence['Arg']:
        sig = inspect.signature(func)

        return tuple(
            cls.from_parameter(param)
            for param in sig.parameters.values())

    def add_to_parser(self, parser: argparse.ArgumentParser):
        kwargs = dict(default=self.default, type=self.type, help=self.arg_help)

        if self.is_kwarg:
            kwargs['dest'] = self.name

        parser.add_argument(*self.names, **kwargs)

    def update_name(self, name: str):
        if name not in self.all_names:
            self.all_names.insert(0, name)
        else:
            assert self.all_names[0] == name

        self.name = name

    @property
    def names(self) -> t.Tuple[str]:
        if not self.is_kwarg:
            return (self.name,)

        assert all(i.startswith('-') for i in self.all_names[1:])
        assert self.name == self.all_names[0]
        return (f'--{self.name}',) + tuple(self.all_names[1:])

    @property
    def arg_help(self) -> str:
        out = self.help or ''
        if self.default is not inspect.Parameter.empty:
            if out:
                out += '. '
            out += f'Default: {self.default}'
        return out


class App:
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(*args, **kwargs)
        self.subparsers = None

    def main(self, fnc):
        self.parser.set_defaults(func=fnc)

        for arg in Arg.from_func(fnc):
            arg.add_to_parser(self.parser)

        if not self.parser.description:
            self.parser.description = fnc.__doc__

        @functools.wraps(fnc)
        def wrapper(*args, **kwargs):
            return fnc(*args, **kwargs)
        return wrapper

    def subcommand(self, fnc):
        if not self.subparsers:
            self.subparsers = self.parser.add_subparsers()

        sub = self.subparsers.add_parser(
            fnc.__name__, description=fnc.__doc__)

        for arg in Arg.from_func(fnc):
            arg.add_to_parser(sub)

        sub.set_defaults(func=fnc)

        @functools.wraps(fnc)
        def wrapper(*args, **kwargs):
            return fnc(*args, **kwargs)
        return wrapper

    def run(self):
        args = vars(self.parser.parse_args())
        logger.debug("Parsed args: %s", args)
        fnc = args.pop('func')
        fnc(**args)
