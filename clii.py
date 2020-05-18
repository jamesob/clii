"""
clii

The easiest damned argparse wrapper there ever was.


Copyright 2020 James O'Beirne

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
import os
import logging


logger = logging.getLogger('clii')
if os.environ.get('CLII_DEBUG'):
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class Arg:
    def __init__(self,
                 name_or_flags: t.Union[str, t.Sequence[str]],
                 type: object = str,
                 help: str = '',
                 default: object = inspect.Parameter.empty,
                 is_kwarg: bool = False,
                 is_vararg: bool = False,
                 dest: t.Optional[str] = None,
                 ):
        names: t.List[str] = (
            [name_or_flags] if isinstance(name_or_flags, str) else
            list(name_or_flags))

        # Store original parameter name unmangled (e.g. no '-' for '_' sub).
        self.dest = dest or names[0]

        if is_kwarg:
            names = [n.replace('_', '-') for n in names]

        self.name = names[0]
        self.all_names = list(names)
        self.type = type
        self.default = default
        self.is_kwarg = is_kwarg
        self.is_vararg = is_vararg
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
            arg.dest = param.name
            return arg
        return cls(
            param.name,
            type=param.annotation,
            default=param.default,
            is_kwarg=is_kwarg(param),
            is_vararg=(param.kind == inspect.Parameter.VAR_POSITIONAL),
            dest=param.name,
        )

    @classmethod
    def from_func(cls, func: t.Callable) -> t.Sequence['Arg']:
        return tuple(
            cls.from_parameter(param) for param in
            _get_func_params(func) if
            # Ignore kwargs; they can't be sensibly interpreted into CLI flags.
            param.kind != inspect.Parameter.VAR_KEYWORD)

    def add_to_parser(self, parser: argparse.ArgumentParser):
        kwargs = dict(
            default=self.default, type=self.type, help=self.arg_help)

        if self.is_kwarg:
            kwargs['dest'] = self.dest
        elif self.is_vararg:
            kwargs['nargs'] = '*'
            kwargs.pop('default', '')
            if kwargs.get('type') == inspect.Parameter.empty:
                kwargs.pop('type')

        if self.type == bool or self.default in [True, False]:
            kwargs['action'] = 'store_false' if self.default else 'store_true'
            kwargs.pop('type', '')

        logger.debug(f"Attaching argument: {self.names} -> {kwargs}")
        parser.add_argument(*self.names, **kwargs)  # type: ignore

    def update_name(self, name: str):
        if name not in self.all_names:
            self.all_names.insert(0, name)
        else:
            assert self.all_names[0] == name

        self.name = name

    @property
    def names(self) -> t.Tuple[str, ...]:
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


def _get_func_params(func, kind_filter: t.Optional[t.List[str]] = None,
                     ) -> t.List[inspect.Parameter]:
    ps = list(inspect.signature(func).parameters.values())
    if kind_filter:
        ps = [p for p in ps if p.kind in kind_filter]
    return ps


class App:
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(*args, **kwargs)
        self.subparsers = None

    def add_arg(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)
        return self.parser

    add_argument = add_arg

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

    def cmd(self, fnc):
        if not self.subparsers:
            self.subparsers = self.parser.add_subparsers()

        sub = self.subparsers.add_parser(
            fnc.__name__.replace('_', '-'), description=fnc.__doc__)

        for arg in Arg.from_func(fnc):
            arg.add_to_parser(sub)

        sub.set_defaults(func=fnc)

        @functools.wraps(fnc)
        def wrapper(*args, **kwargs):
            return fnc(*args, **kwargs)
        return wrapper

    def run(self):
        self.args = self.parser.parse_args()
        args = vars(self.args)
        logger.debug("Parsed args: %s", args)
        fnc = args.pop('func')
        vararg_params = _get_func_params(
            fnc, kind_filter=[inspect.Parameter.VAR_POSITIONAL])
        varargs = []

        if vararg_params:
            varargs = args.pop(vararg_params[0].name)

        func_args = {}

        # Only pull in those parameters which `fnc` accepts, since the
        # global parser may have pulled in more.
        for p in _get_func_params(fnc):
            if p.kind == inspect.Parameter.VAR_POSITIONAL:
                continue
            func_args[p.name] = args[p.name]

        return fnc(*varargs, **func_args)
