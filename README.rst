======
Morph!
======

.. warning::

  2013/11/08: under active development - come back soon!

Morph provides the following functions to help identify object types:

============================  =================================================
Name                          Functionality
============================  =================================================
``morph.isstr(obj)``          Is `obj` a string?
``morph.isseq(obj)``          Is `obj` an sequence-like (i.e. iterable) type
                              (but not a string or dict)?
``morph.isdict(obj)``         Is `obj` a dict-like type? This means that it
                              must have at least the following methods:
                              `keys()`, `values()`, and `items()`.
============================  =================================================


Morph provides the following functions to help morph objects:

============================  =================================================
Name                          Functionality
============================  =================================================
``morph.tobool(obj)``         Converts `obj` to a bool; if string-like, it
                              is matched against a list of "truthy" or "falsy"
                              strings; if bool-like, returns itself; then,
                              if the `default` parameter is not None, returns
                              that; otherwise throws a ValueError exception.
``morph.tolist(obj)``         Converts `obj` to a list; if string-like, it
                              splits it according to Unix shell semantics;
                              if seq-like, returns itself, and otherwise
                              returns a list with itself as single object.
``morph.pick(...)``           Extracts a subset of key/value pairs from a
                              dict-like object where the key is a specific
                              value or has a specific prefix.
``morph.omit(...)``           Converse of `morph.pick()`.
``morph.flatten(obj)``        Converts a multi-dimensional list or dict type
                              to a one-dimensional list or dict.
``morph.unflatten(obj)``      Reverses the effects of `flatten` (note that
                              lists cannot be unflattened).
============================  =================================================


Flattening
==========

When flattening a sequence-like object (i.e. list or tuple),
`morph.flatten` recursively reduces multi-dimensional arrays to a
single dimension, but only for elements of each descended list that
are list-like. For example:

.. code-block:: python

  [1, [2, [3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}], 4]]

  # is morphed to

  [1, 2, 3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}, 4]

When flattening a dict-like object, it collapses list- and dict-
subkeys into indexed and dotted top-level keys. For example:

.. code-block:: python

  {
    'a': {
      'b': 1,
      'c': [
        2,
        {
          'd': 3,
          'e': 4,
        }
      ]
    }
  }

  # is morphed to

  {
    'a.b':      1,
    'a.c[0]':   2,
    'a.c[1].d': 3,
    'a.c[1].e': 4,
  }

(This is primarily useful when dealing with INI files, which can only
be flat: the `flatten` and `unflatten` functions allow converting
between complex structures and flat INI files).

Note that lists can never be unflattened, and unflattening dicts is
not garanteed to be round-trip consistent. The latter can happen if
the dict-to-be-flattened had keys with special characters in them,
such as a period (``'.'``) or square brackets (``'[]'``).


Picking and Omitting
====================

Morph's `pick` and `omit` functions allow you to extract a set of keys
(or properties) from a dict-like object (or plain object). For
example:

.. code-block:: python

  d = {'foo': 'bar', 'zig.a': 'b', 'zig.c': 'd'}

  morph.pick(d, 'foo', 'zig.a')
  # ==> {'foo', 'bar', 'zig.a': 'b'}

  morph.pick(d, prefix='zig.')
  # ==> {'a': 'b', 'c': 'd'}

  morph.pick(d, 'c', prefix='zig.')
  # ==> {'c': 'd'}

  morph.omit(d, 'foo')
  # ==> {'zig.a': 'b', 'zig.c': 'd'}

  morph.omit(d, prefix='zig.')
  # ==> {'foo': 'bar'}

With some limitations, this also works on object properties. For
example:

.. code-block:: python

  class X():
    def __init__(self):
      self.foo = 'bar'
      self.zig1 = 'zog'
      self.zig2 = 'zug'
    def zigMethod(self):
      pass
  x = X()

  morph.pick(x, 'foo', 'zig1')
  # ==> {'foo': 'bar', 'zig1': 'zog'}

  morph.pick(x, prefix='zig')
  # ==> {'1': 'zog', '2': 'zug'}

  morph.pick(x)
  # ==> {}

  morph.omit(x, 'foo')
  # ==> {'zig1': 'zog', 'zig2': 'zug'}

  morph.omit(x, prefix='zig')
  # ==> {'foo': 'bar'}

  morph.omit(x)
  # ==> {'foo': 'bar', 'zig1': 'zog', 'zig2': 'zug'}
