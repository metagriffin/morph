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

import sys, shlex
PY3 = sys.version_info[0] >= 3

truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))
falsy  = frozenset(('f', 'false', 'n', 'no', 'off', '0'))
booly  = frozenset(list(truthy) + list(falsy))

#------------------------------------------------------------------------------
if PY3:
  def isstr(obj):
    'Returns whether or not `obj` is a string-like object.'
    return isinstance(obj, str)
else:
  def isstr(obj):
    'Returns whether or not `obj` is a string-like object.'
    return isinstance(obj, basestring)

#------------------------------------------------------------------------------
def isseq(obj):
  '''
  Returns True if `obj` is a sequence-like object (but not a string or
  dict); i.e. a tuple, list, subclass thereof, or having an interface
  that supports iteration.
  '''
  return \
    not isstr(obj) \
    and not isdict(obj) \
    and ( isinstance(obj, (list, tuple)) \
          or callable(getattr(obj, '__iter__', None)))

#------------------------------------------------------------------------------
def isdict(obj):
  '''
  Returns True if `obj` is a dict-like object (but not a string or
  list); i.e. a dict, subclass thereof, or having an interface that
  supports key, value, and item iteration.
  '''
  return \
    not isstr(obj) \
    and ( isinstance(obj, dict) \
          or ( callable(getattr(obj, 'keys', None)) \
               and callable(getattr(obj, 'values', None)) \
               and callable(getattr(obj, 'items', None)) ))

#------------------------------------------------------------------------------
def tobool(obj, default=False):
  '''
  TODO: add docs
  '''
  if isstr(obj):
    lobj = obj.lower()
    if lobj in truthy:
      return True
    if lobj in falsy:
      return False
  if isinstance(obj, bool):
    return obj
  if default is not None:
    return default
  raise ValueError('invalid literal for tobool(): %r' % (obj,))

#------------------------------------------------------------------------------
def tolist(obj, flat=True):
  '''
  TODO: add docs
  '''
  if not obj:
    return []
  if isseq(obj):
    return flatten(obj) if flat else obj
  if isstr(obj):
    return shlex.split(obj)
  return [obj]

#------------------------------------------------------------------------------
def flatten(obj):
  '''
  TODO: add docs
  '''
  if isseq(obj):
    ret = []
    for item in obj:
      if isseq(item):
        ret.extend(flatten(item))
      else:
        ret.append(item)
    return ret
  if isdict(obj):
    ret = dict()
    for key, value in obj.items():
      for skey, sval in _relflatten(value):
        ret[key + skey] = sval
    return ret
  raise ValueError(
    'only list- and dict-like objects can be flattened, not %r' % (obj,))
def _relflatten(obj):
  if isseq(obj):
    for idx, subval in enumerate(obj):
      for skey, sval in _relflatten(subval):
        yield '[' + str(idx) + ']' + skey, sval
    return
  if isdict(obj):
    for skey, sval in flatten(obj).items():
      yield '.' + skey, sval
    return
  yield '', obj

#------------------------------------------------------------------------------
def unflatten(obj):
  '''
  TODO: add docs
  '''
  if not isdict(obj):
    raise ValueError(
      'only dict-like objects can be unflattened, not %r' % (obj,))
  ret = dict()
  sub = dict()
  for key, value in obj.items():
    if '.' not in key and '[' not in key:
      ret[key] = value
      continue
    if '.' in key and '[' in key:
      idx = min(key.find('.'), key.find('['))
    elif '.' in key:
      idx = key.find('.')
    else:
      idx = key.find('[')
    prefix = key[:idx]
    if prefix not in sub:
      sub[prefix] = dict()
    sub[prefix][key[idx:]] = value
  for pfx, values in sub.items():
    if pfx in ret:
      raise ValueError(
        'conflicting scalar vs. structure for prefix: %s' % (pfx,))
    ret[pfx] = _relunflatten(pfx, values)
  return ret
def _relunflatten(pfx, values):
  if len(values) == 1 and values.keys()[0] == '':
    return values.values()[0]
  typ = set([k[0] for k in values.keys()])
  if len(typ) != 1:
    raise ValueError(
      'conflicting structures (dict vs. list) for prefix: %s' % (pfx,))
  typ = list(typ)[0]
  if typ == '.':
    return unflatten({k[1:]: v for k, v in values.items()})
  tmp = dict()
  for skey, sval in values.items():
    if skey[0] != '[':
      # this should never happen...
      raise ValueError('unexpected unflatten character "%s" (expected "[")'
                       % (skey[0],))
    idx = skey.find(']')
    if idx < 1:
      raise ValueError(
        'invalid list syntax (no terminating "]") in key "%s"'
        % (pfx + skey,))
    try:
      pos = int(skey[1:idx])
    except ValueError:
      raise ValueError(
        'invalid list syntax (bad index) in key "%s"'
        % (pfx + skey,))
    if pos not in tmp:
      tmp[pos] = dict()
    tmp[pos][skey[idx + 1:]] = sval
  return [_relunflatten(pfx + '[' + str(pos) + ']', tmp[pos])
          for pos in sorted(tmp.keys())]

#------------------------------------------------------------------------------
def properties(obj):
  for attr in dir(obj):
    if not attr.startswith('_') and not callable(getattr(obj, attr)):
      yield attr

#------------------------------------------------------------------------------
def pick(source, *keys, **kw):
  '''
  Given a `source` dict or object, returns a new dict that contains a
  subset of keys (each key is a separate positional argument) and/or
  where each key is a string and has the specified `prefix`, specified
  as a keyword argument. Also accepts the optional keyword argument
  `dict` which must be a dict-like class that will be used to
  instantiate the returned object. Note that if `source` is an object
  without an `items()` iterator, then the selected keys will be
  extracted as attributes. The `prefix` keyword only works with
  dict-like objects.
  '''
  rettype = kw.pop('dict', dict)
  prefix = kw.pop('prefix', None)
  if kw:
    raise ValueError('invalid pick keyword arguments: %r' % (kw.keys(),))
  if not source:
    return rettype()
  if prefix is not None:
    try:
      items = source.items()
    except AttributeError:
      items = None
    if items is not None:
      source = {k[len(prefix):]: v
                for k, v in items
                if getattr(k, 'startswith', lambda x: False)(prefix)}
    else:
      source = {attr[len(prefix):]: getattr(source, attr)
                for attr in properties(source)
                if attr.startswith(prefix)}
  if len(keys) <= 0:
    if prefix is not None:
      return rettype(source)
    return rettype()
  try:
    return rettype({k: v for k, v in source.items() if k in keys})
  except AttributeError:
    return rettype({k: getattr(source, k) for k in keys if hasattr(source, k)})

#------------------------------------------------------------------------------
def omit(source, *keys, **kw):
  '''
  Identical to the :func:`pick` function, but returns the complement,
  with the exception of the `prefix` parameter. In the `omit`
  scenario, it works as a wildcarded key, where all keys that have a
  ``startswith()`` function and it returns True of the `prefix` are
  excluded from the return structure.
  '''
  rettype = kw.pop('dict', dict)
  prefix = kw.pop('prefix', None)
  if kw:
    raise ValueError('invalid omit keyword arguments: %r' % (kw.keys(),))
  if not source:
    return rettype()
  if prefix is not None:
    try:
      items = source.items()
    except AttributeError:
      items = None
    if items is not None:
      source = {k: v
                for k, v in items
                if not getattr(k, 'startswith', lambda x: False)(prefix)}
    else:
      source = {attr: getattr(source, attr)
                for attr in properties(source)
                if not attr.startswith(prefix)}
  # if len(keys) <= 0:
  #   try:
  #     return rettype(source)
  #   except TypeError:
  #     return rettype({k: v for k, v in properties(source)})
  try:
    return rettype({k: v for k, v in source.items() if k not in keys})
  except AttributeError:
    pass
  try:
    return rettype({k: getattr(source, k)
                    for k in iter(source)
                    if k not in keys})
  except TypeError:
    return rettype({k: getattr(source, k)
                    for k in properties(source)
                    if k not in keys})

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
