#!/usr/bin/env python3.8
import clii


def test_helps_from_doc():
    def test_func(foo, bar, baz):
        """
        Does something.

        Args:
          foo: monetary insolvency
          bar: whoa whoa whoa
          baz: what's up?
        """

    def other_func(a, b):
        pass

    assert (
        clii._get_helps_from_func(test_func, ['foo', 'bar', 'buzz']) ==
        {'foo': 'monetary insolvency', 'bar': 'whoa whoa whoa'})

    assert clii._get_helps_from_func(other_func, ['a']) == {}


if __name__ == '__main__':
    test_helps_from_doc()
