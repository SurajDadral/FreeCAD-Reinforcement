# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "Literal typehint"
__author__ = ""
__url__ = "https://www.freecadweb.org"


import typing


# Please keep __all__ alphabetized within each category.
__all__ = [
    # Super-special typing primitives.
    "Literal",
]


class _SpecialForm(typing._Final, typing._Immutable, _root=True):
    """Internal indicator of special typing constructs.
    See _doc instance attribute for specific docs.
    """

    __slots__ = ("_name", "_doc")

    def __new__(cls, *args, **kwds):
        """Constructor.

        This only exists to give a better error message in case
        someone tries to subclass a special typing object (not a good idea).
        """
        if (
            len(args) == 3
            and isinstance(args[0], str)
            and isinstance(args[1], tuple)
        ):
            # Close enough.
            raise TypeError(f"Cannot subclass {cls!r}")
        return super().__new__(cls)

    def __init__(self, name, doc):
        self._name = name
        self._doc = doc

    def __eq__(self, other):
        if not isinstance(other, _SpecialForm):
            return NotImplemented
        return self._name == other._name

    def __hash__(self):
        return hash((self._name,))

    def __repr__(self):
        return "typing." + self._name

    def __reduce__(self):
        return self._name

    def __call__(self, *args, **kwds):
        raise TypeError(f"Cannot instantiate {self!r}")

    def __instancecheck__(self, obj):
        raise TypeError(f"{self} cannot be used with isinstance()")

    def __subclasscheck__(self, cls):
        raise TypeError(f"{self} cannot be used with issubclass()")

    @typing._tp_cache
    def __getitem__(self, parameters):
        if self._name == "Literal":
            # There is no '_type_check' call because arguments to Literal[...]
            # are values, not types.
            return typing._GenericAlias(self, parameters)
        raise TypeError(f"{self} is not subscriptable")


Literal = _SpecialForm(
    "Literal",
    doc="""Special typing form to define literal types (a.k.a. value types).

This form can be used to indicate to type checkers that the corresponding
variable or function parameter has a value equivalent to the provided
literal (or one of several literals):

  def validate_simple(data: Any) -> Literal[True]:  # always returns True
      ...

  MODE = Literal['r', 'rb', 'w', 'wb']
  def open_helper(file: str, mode: MODE) -> str:
      ...

  open_helper('/some/path', 'r')  # Passes type check
  open_helper('/other/path', 'typo')  # Error in type checker

Literal[...] cannot be subclassed. At runtime, an arbitrary value
is allowed as type argument to Literal[...], but type checkers may
impose restrictions.
""",
)
