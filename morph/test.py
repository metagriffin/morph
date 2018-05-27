# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/11/08
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import unittest

import morph

#------------------------------------------------------------------------------
class TestMorph(unittest.TestCase):

  maxDiff = None

  #----------------------------------------------------------------------------
  def test_isstr(self):
    self.assertTrue(morph.isstr(''))
    self.assertTrue(morph.isstr(u''))
    self.assertTrue(morph.isstr('abc'))
    self.assertTrue(morph.isstr(u'abc'))
    self.assertFalse(morph.isstr(['a', 'b', 'c']))
    self.assertFalse(morph.isstr(('a', 'b', 'c')))
    self.assertFalse(morph.isstr(list('abc')))
    self.assertFalse(morph.isstr(dict(abc='def')))
    self.assertFalse(morph.isstr(17))

  #----------------------------------------------------------------------------
  def test_isseq(self):
    self.assertTrue(morph.isseq(['a', 'b', 'c']))
    self.assertTrue(morph.isseq(('a', 'b', 'c')))
    self.assertTrue(morph.isseq(set(['a', 'b', 'c'])))
    class mylist(list): pass
    self.assertTrue(morph.isseq(mylist()))
    class myiter(object):
      def __iter__(self):
        return iter(['a', 'b', 'c'])
    self.assertTrue(morph.isseq(myiter()))
    self.assertFalse(morph.isseq('abc'))
    self.assertFalse(morph.isseq(u'abc'))
    class myobj(object): pass
    self.assertFalse(morph.isseq(myobj()))
    self.assertFalse(morph.isseq(dict(abc='def')))

  #----------------------------------------------------------------------------
  def test_isdict(self):
    self.assertTrue(morph.isdict(dict()))
    self.assertTrue(morph.isdict(dict(abc='def')))
    self.assertFalse(morph.isdict('abc'))
    self.assertFalse(morph.isdict(u'abc'))
    self.assertFalse(morph.isdict(['a', 'b', 'c']))

  #----------------------------------------------------------------------------
  def test_tobool(self):
    self.assertTrue(morph.tobool('true'))
    self.assertTrue(morph.tobool('TRUE'))
    self.assertTrue(morph.tobool('yes'))
    self.assertTrue(morph.tobool('yEs'))
    self.assertTrue(morph.tobool('1'))
    self.assertFalse(morph.tobool('false'))
    self.assertFalse(morph.tobool('FALSE'))
    self.assertFalse(morph.tobool('nada'))
    self.assertFalse(morph.tobool('No'))
    self.assertFalse(morph.tobool('no'))
    self.assertFalse(morph.tobool('0'))
    self.assertIsNone(morph.tobool('nada', default=None))
    with self.assertRaises(ValueError) as cm:
      morph.tobool('nada', default=ValueError)
    self.assertTrue(morph.tobool(True))
    self.assertFalse(morph.tobool(False))

  #----------------------------------------------------------------------------
  def test_tolist(self):
    self.assertEqual(morph.tolist(['abc', 'def']), ['abc', 'def'])
    self.assertEqual(morph.tolist('abcdef'), ['abcdef'])
    self.assertEqual(morph.tolist('abc def'), ['abc', 'def'])
    self.assertEqual(morph.tolist('ab cd ef'), ['ab', 'cd', 'ef'])
    self.assertEqual(morph.tolist('"ab cd"\nef'), ['ab cd', 'ef'])

  #----------------------------------------------------------------------------
  def test_flatten(self):
    self.assertEqual(
      morph.flatten([1, [2, [3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}], 4]]),
      [1, 2, 3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}, 4])
    self.assertEqual(
      morph.flatten({'a': {'b': 'c'}}),
      {'a.b': 'c'})
    self.assertEqual(
      morph.flatten({'a': {'b': 1, 'c': [2, {'d': 3, 'e': 4}]}}),
      {'a.b': 1, 'a.c[0]': 2, 'a.c[1].d': 3, 'a.c[1].e': 4})
    self.assertEqual(
      morph.flatten({'a': {'b': [[1, 2], [3, {'x': 4, 'y': 5}, 6]]}}),
      {'a.b[0][0]':   1,
       'a.b[0][1]':   2,
       'a.b[1][0]':   3,
       'a.b[1][1].x': 4,
       'a.b[1][1].y': 5,
       'a.b[1][2]':   6,
      })

  #----------------------------------------------------------------------------
  def test_unflatten_fail(self):
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a.b': 'c', 'a[0]': 'no'})
    self.assertEqual(
      str(cm.exception),
      'conflicting structures (dict vs. list) for prefix: a')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a': 'b', 'a.b': 'c'})
    self.assertEqual(
      str(cm.exception),
      'conflicting scalar vs. structure for prefix: a')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a[0': 'b'})
    self.assertEqual(
      str(cm.exception),
      'invalid list syntax (no terminating "]") in key "a[0"')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a[NADA]': 'b'})
    self.assertEqual(
      str(cm.exception),
      'invalid list syntax (bad index) in key "a[NADA]"')

  #----------------------------------------------------------------------------
  def test_unflatten_ok(self):
    self.assertEqual(
      morph.unflatten({'a.b': 'c', 'd': 'e'}),
      {'a': {'b': 'c'}, 'd': 'e'})
    self.assertEqual(
      morph.unflatten({'a.b': 1, 'a.c[0]': 2, 'a.c[1]': 3, 'a.c[2]': 4}),
      {'a': {'b': 1, 'c': [2, 3, 4]}})
    self.assertEqual(
      morph.unflatten({'a.b': 1, 'a.c[0]': 2, 'a.c[1].d': 3, 'a.c[1].e': 4}),
      {'a': {'b': 1, 'c': [2, {'d': 3, 'e': 4}]}})
    self.assertEqual(
      morph.unflatten({
        'a.b[0][0]':   1,
        'a.b[0][1]':   2,
        'a.b[1][0]':   3,
        'a.b[1][1].x': 4,
        'a.b[1][1].y': 5,
        'a.b[1][2]':   6,
        }),
      {'a': {'b': [[1, 2], [3, {'x': 4, 'y': 5}, 6]]}})

  #----------------------------------------------------------------------------
  def test_pick(self):
    class aadict(dict): pass
    d = aadict(foo='bar', zig=87, ziggy=78)
    self.assertEqual(morph.pick(d, 'foo'), {'foo': 'bar'})
    self.assertEqual(morph.pick(d, 'foo', dict=aadict), {'foo': 'bar'})
    self.assertEqual(morph.pick(d), {})
    self.assertEqual(morph.pick(d, prefix='zi'), {'g': 87, 'ggy': 78})
    self.assertIsInstance(morph.pick(d, 'foo'), dict)
    self.assertNotIsInstance(morph.pick(d, 'foo'), aadict)
    self.assertIsInstance(morph.pick(d, 'foo', dict=aadict), aadict)
    self.assertEqual(morph.pick(d), {})

  #----------------------------------------------------------------------------
  def test_pick_object(self):
    class Thing(object):
      def __init__(self):
        self.foo = 'bar'
        self.zig1 = 'zog'
        self.zig2 = 'zug'
      def zigSomeMethod(self):
        pass
    src = Thing()
    self.assertEqual(
      morph.pick(src, 'foo', 'zig1'),
      {'zig1': 'zog', 'foo': 'bar'})
    self.assertEqual(
      morph.pick(src, prefix='zig'),
      {'1': 'zog', '2': 'zug'})
    self.assertEqual(morph.pick(src), {})

  #----------------------------------------------------------------------------
  def test_pick_tree(self):
    src = {
      'a': 'a',
      'b': {'x': 'b.x', 'y': 'b.y'},
      'b.x': 'b-dot-x',
      'c': [
        {'x': 'c0.x', 'y': 'c0.y'},
        {'x': 'c1.x', 'y': 'c1.y'},
      ],
    }
    self.assertEqual(
      morph.pick(src, 'a', 'b.x', tree=True),
      {'a': 'a', 'b': {'x': 'b.x'}})
    self.assertEqual(
      morph.pick(src, 'a', 'b.x'),
      {'a': 'a', 'b.x': 'b-dot-x'})
    # TODO: add support for this...
    # self.assertEqual(
    #   morph.pick(src, 'c[0].x', tree=True),
    #   {'c': [{'x': 'c0.x'}]})
    # self.assertEqual(
    #   morph.pick(src, 'c[].x', tree=True),
    #   {'c': [{'x': 'c0.x'}, {'x': 'c1.x'}]})

  #----------------------------------------------------------------------------
  def test_omit(self):
    class aadict(dict): pass
    d = aadict(foo='bar', zig=87, ziggy=78)
    self.assertEqual(morph.omit(d, 'foo'), {'zig': 87, 'ziggy': 78})
    self.assertEqual(morph.omit(d, prefix='zig'), {'foo': 'bar'})
    self.assertEqual(morph.omit(d), {'foo': 'bar', 'zig': 87, 'ziggy': 78})

  #----------------------------------------------------------------------------
  def test_omit_object(self):
    class Thing(object):
      def __init__(self):
        self.foo = 'bar'
        self.zig1 = 'zog'
        self.zig2 = 'zug'
      def zigSomeMethod(self):
        pass
    src = Thing()
    self.assertEqual(
      morph.omit(src, 'foo', 'zig1'),
      {'zig2': 'zug'})
    self.assertEqual(
      morph.omit(src, prefix='zig'),
      {'foo': 'bar'})
    self.assertEqual(
      morph.omit(src), {'foo': 'bar', 'zig1': 'zog', 'zig2': 'zug'})

  #----------------------------------------------------------------------------
  def test_omit_tree(self):
    src = {
      'a': 'a',
      'b': {'x': 'b.x', 'y': 'b.y'},
      'b.x': 'b-dot-x',
      'c': [
        {'x': 'c0.x', 'y': 'c0.y'},
        {'x': 'c1.x', 'y': 'c1.y'},
      ],
    }
    self.assertEqual(
      morph.omit(src, 'a', 'b.x', 'c', tree=True),
      {'b': {'y': 'b.y'}, 'b.x': 'b-dot-x'})
    self.assertEqual(
      morph.omit(src, 'a', 'b.x', 'c'),
      {'b': {'x': 'b.x', 'y': 'b.y'}})

    # src = {'a': 'a', 'b': [{'x': 'b0.x', 'y': 'b0.y'}, {'x': 'b1.x', 'y': 'b1.y'}]}
    # self.assertEqual(
    #   morph.omit(src, 'b[0].x'),
    #   {'a': 'a', 'b': [{'y': 'b0.y'}, {'x': 'b1.x', 'y': 'b1.y'}]})
    # self.assertEqual(
    #   morph.omit(src, 'b[].x'),
    #   {'a': 'a', 'b': [{'y': 'b0.y'}, {'y': 'b1.y'}]})

  #----------------------------------------------------------------------------
  def test_xform_seq(self):
    stack = []
    def double(value, **kws):
      stack.append((value, kws))
      return value * 2
    src = [4, 'foo', -2.25]
    self.assertEqual(
      morph.xform(src, double),
      [8, 'foofoo', -4.5])
    self.assertEqual(stack, [
      (4, dict(index=0, seq=src, root=src)),
      ('foo', dict(index=1, seq=src, root=src)),
      (-2.25, dict(index=2, seq=src, root=src)),
    ])

  #----------------------------------------------------------------------------
  def test_xform_dict(self):
    stack = []
    def double(value, **kws):
      stack.append((value, kws))
      return value * 2
    src = {4: 'four', 'foo': 'bar', 'float': -2.25}
    self.assertEqual(
      morph.xform(src, double),
      {8: 'fourfour', 'foofoo': 'barbar', 'floatfloat': -4.5})
    self.assertEqual(sorted(stack), sorted([
      (4, dict(item_value='four', dict=src, root=src)),
      ('four', dict(item_key=4, dict=src, root=src)),
      ('foo', dict(item_value='bar', dict=src, root=src)),
      ('bar', dict(item_key='foo', dict=src, root=src)),
      ('float', dict(item_value=-2.25, dict=src, root=src)),
      (-2.25, dict(item_key='float', dict=src, root=src)),
    ]))

  #----------------------------------------------------------------------------
  def test_xform_combined(self):
    stack = []
    def double(value, **kws):
      stack.append((value, kws))
      return value * 2
    src = {'key': [8, {'k2': -2}]}
    self.assertEqual(
      morph.xform(src, double),
      {'keykey': [16, {'k2k2': -4}]})
    self.assertEqual(stack, [
      (8, dict(index=0, seq=[8, {'k2': -2}], root=src)),
      (-2, dict(item_key='k2', dict={'k2': -2}, root=src)),
      ('k2', dict(item_value=-2, dict={'k2': -2}, root=src)),
      ('key', dict(item_value=[8, {'k2': -2}], dict=src, root=src)),
    ])


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
