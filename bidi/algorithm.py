# -*- coding: utf-8 -*-
# This file is part of python-bidi
#
# python-bidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Yaacov Zamir <kzamir_a_walla.co.il>,
# 2010-2014 Meir kriheli <meir@mksoft.co.il>
"bidirectional alogrithm implementation"
import sys

import inspect
import six
from collections import deque, namedtuple
from itertools import islice
from operator import itemgetter
from unicodedata import bidirectional, mirrored

from .definitions import (PARAGRAPH_LEVELS, IS_UCS2, SURROGATE_MIN,
                          SURROGATE_MAX, ISOLATE_INITIATORS, MAX_DEPTH,
                          X9_REMOVED)
from .helpers import least_greater_even, least_greater_odd
from .mirror import MIRRORED


LevelEntry = namedtuple(
    'LevelEntry',
    ['embedding_level', 'directional_override', 'directional_isolate']
)


class BidiLayout(object):

    def __init__(self, unistr, base_dir=None, upper_is_rtl=False, debug=False):
        self.text = unistr
        self.upper_is_rtl = upper_is_rtl
        self.base_dir = base_dir
        self._base_level = None
        self.debug = debug
        self._display = None

        self.chars = deque()

        # for embedded levels
        self.levels_stack = None  # will be set to a stack in X1
        self.overflow_isolate_count = 0
        self.overflow_embedding_count = 0
        self.valid_isolate_count = 0
        self.last_level_entry = None

        self.prepare()

    def iter_text(self):
        "yield chars, takes into account surrogate pairs if needed"

        # short circuit for UCS2
        if not IS_UCS2:
            for ch in self.text:
                yield ch
        else:
            prev_surrogate = False
            for ch in self.text:
                if SURROGATE_MIN <= ord(ch) <= SURROGATE_MAX:
                    prev_surrogate = ch
                    continue
                elif prev_surrogate:
                    ch = prev_surrogate + ch
                    prev_surrogate = False

                yield ch

    def calc_paragraph_level(self, chars=None):
        """Applies P2 and P3.

        P2_ :

        In each paragraph, find the first character of type L, AL, or R while
        skipping over any characters between an isolate initiator and its
        matching PDI or, if it has no matching PDI, the end of the paragraph.

        P3_ :

        If a character is found in P2 and it is of type AL or R, then set the
        paragraph embedding level to one; otherwise, set it to zero.

        .. _P2: http://www.unicode.org/reports/tr9/#P2
        .. _P3: http://www.unicode.org/reports/tr9/#P3
        """
        upper_is_rtl = self.upper_is_rtl
        isolate_initiator_level = 0

        if chars is None:
            chars = self.chars

        getter = itemgetter('ch')
        for ch in map(getter, chars):
            bidi_type = bidirectional(ch)

            if bidi_type in ISOLATE_INITIATORS:
                isolate_initiator_level += 1
                continue

            if bidi_type == 'PDI' and isolate_initiator_level > 0:
                isolate_initiator_level -= 1
                continue

            # ignore isolate initiators till it's matching PDI
            if isolate_initiator_level > 0:
                continue

            if upper_is_rtl and ch.isupper():
                bidi_type = 'R'

            base_level = PARAGRAPH_LEVELS.get(bidi_type)

            if base_level is not None:
                break

        if base_level is None:
            base_level = PARAGRAPH_LEVELS['L']

        return base_level

    @property
    def base_level(self):
        """Get the paragraph base embedding level. Returns 0 for LTR,
        1 for RTL.

        Lazy calculated on first access.

        Applies rules P2_ and P3_

        .. _P2: http://www.unicode.org/reports/tr9/#P2
        .. _P3: http://www.unicode.org/reports/tr9/#P3

        """
        if self._base_level is None:

            if self.base_dir is not None:
                self._base_level = PARAGRAPH_LEVELS[self.base_dir]
            else:
                self._base_level = self.calc_paragraph_level()

        return self._base_level

    def prepare(self):
        """Setup the initial chars and their attributes"""

        upper_is_rtl = self.upper_is_rtl

        self.chars.clear()

        for ch in self.iter_text():
            if upper_is_rtl and ch.isupper():
                bidi_type = 'R'
            else:
                bidi_type = bidirectional(ch)

            self.chars.append({
                'ch': ch,
                'level': None,
                'type': bidi_type,
                'orig': bidi_type,
            })

    def push_levels_entry(self, entry):
        "Appends entry to levels_stack, and sets it as last_level_entry"
        self.last_level_entry = entry
        self.levels_stack.append(entry)

    def pop_levels_entry(self):
        "Pops level entry, updates last_level_entry"
        stack = self.levels_stack
        entry = stack.pop()
        self.last_level_entry = stack[-1]
        return entry

    def is_valid_level_and_counters(self, level):
        return (level <= MAX_DEPTH and self.overflow_isolate_count == 0
                and self.overflow_embedding_count == 0)

    def X1(self):
        """X1_:

        * Set the stack to empty.
        * Push onto the stack an entry consisting of the paragraph embedding
          level, a neutral directional override status, and a false directional
          isolate status.
        * Set the overflow isolate count to zero.
        * Set the overflow embedding count to zero.
        * Set the valid isolate count to zero.

        .. _X1: http://www.unicode.org/reports/tr9/#X1
        """

        self.levels_stack = deque()
        self.push_levels_entry(LevelEntry(self.base_level, 'N', False))
        self.overflow_isolate_count = 0
        self.overflow_embedding_count = 0
        self.valid_isolate_count = 0

    def X2(self, idx):
        """X2_, With each RLE, perform the following steps:

        * Compute the least odd embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid, and the overflow isolate count and
          overflow embedding count are both zero, then this RLE is valid. Push
          an entry consisting of the new embedding level, neutral directional
          override status, and false directional isolate status onto the
          directional status stack.
        * Otherwise, this is an overflow RLE. If the overflow isolate count is
          zero, increment the overflow embedding count by one. Leave all other
          variables unchanged.

        .. _X2: http://www.unicode.org/reports/tr9/#X2
        """

        level = least_greater_odd(self.last_level_entry.embedding_level)

        if self.is_valid_level_and_counters(level):
            self.push_levels_entry(LevelEntry(level, 'N', False))
        elif self.overflow_isolate_count == 0:
            self.overflow_embedding_count += 1

    def X3(self, idx):
        """X3_, With each LRE, perform the following steps:

        * Compute the least even embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid, and the overflow isolate count and
          overflow embedding count are both zero, then this LRE is valid. Push
          an entry consisting of the new embedding level, neutral directional
          override status, and false directional isolate status onto the
          directional status stack.
        * Otherwise, this is an overflow LRE. If the overflow isolate count is
          zero, increment the overflow embedding count by one. Leave all other
          variables unchanged.

        .. _X3: http://www.unicode.org/reports/tr9/#X3
        """

        level = least_greater_even(self.last_level_entry.embedding_level)

        if self.is_valid_level_and_counters(level):
            self.push_levels_entry(LevelEntry(level, 'N', False))
        elif self.overflow_isolate_count == 0:
            self.overflow_embedding_count += 1

    def X4(self, idx):
        """X4_, With each RLO, perform the following steps:

        * Compute the least odd embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid, and the overflow isolate count and
          overflow embedding count are both zero, then this RLO is valid. Push
          an entry consisting of the new embedding level, right-to-left
          directional override status, and false directional isolate status
          onto the directional status stack.
        * Otherwise, this is an overflow RLO. If the overflow isolate count is
          zero, increment the overflow embedding count by one. Leave all other
          variables unchanged.

        .. _X4: http://www.unicode.org/reports/tr9/#X4
        """
        level = least_greater_odd(self.last_level_entry.embedding_level)

        if self.is_valid_level_and_counters(level):
            self.push_levels_entry(LevelEntry(level, 'R', False))
            self.levels_stack.append(self.last_level_entry)
        elif self.overflow_isolate_count == 0:
            self.overflow_embedding_count += 1

    def X5(self, idx):
        """X5_, With each LRO, perform the following steps:

        * Compute the least even embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid, and the overflow isolate count and
          overflow embedding count are both zero, then this LRO is valid. Push
          an entry consisting of the new embedding level, left-to-right
          directional override status, and false directional isolate status
          onto the directional status stack.
        * Otherwise, this is an overflow LRO. If the overflow isolate count is
          zero, increment the overflow embedding count by one. Leave all other
          variables unchanged.

        .. _X5: http://www.unicode.org/reports/tr9/#X5
        """
        level = least_greater_even(self.last_level_entry.embedding_level)

        if self.is_valid_level_and_counters(level):
            self.push_levels_entry(LevelEntry(level, 'L', False))
        elif self.overflow_isolate_count == 0:
            self.overflow_embedding_count += 1

    def X5a(self, idx):
        """X5a_, With each RLI, perform the following steps:

        * Set the RLI’s embedding level to the embedding level of the last
          entry on the directional status stack.
        * Compute the least odd embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid and the overflow isolate count and
          the overflow embedding count are both zero, then this RLI is valid.
          Increment the valid isolate count by one, and push an entry
          consisting of the new embedding level, neutral directional override
          status, and true directional isolate status onto the directional
          status stack.
        * Otherwise, this is an overflow RLI. Increment the overflow isolate
          count by one, and leave all other variables unchanged.

        .. _X5a: http://www.unicode.org/reports/tr9/#X5a
        """

        self.chars[idx]['level'] = self.last_level_entry.embedding_level

        level = least_greater_odd(self.last_level_entry.embedding_level)
        if self.is_valid_level_and_counters(level):
            self.valid_isolate_count += 1
            self.push_levels_entry(LevelEntry(level, 'N', True))
        else:
            self.overflow_isolate_count += 1

    def X5b(self, idx):
        """X5b_, With each LRI, perform the following steps:

        * Set the LRI’s embedding level to the embedding level of the last
          entry on the directional status stack.
        * Compute the least even embedding level greater than the embedding
          level of the last entry on the directional status stack.
        * If this new level would be valid and the overflow isolate count and
          the overflow embedding count are both zero, then this LRI is valid.
          Increment the valid isolate count by one, and push an entry
          consisting of the new embedding level, neutral directional override
          status, and true directional isolate status onto the directional
          status stack.
        * Otherwise, this is an overflow LRI. Increment the overflow isolate
          count by one, and leave all other variables unchanged

        .. _X5b: http://www.unicode.org/reports/tr9/#X5b
        """

        self.chars[idx]['level'] = self.last_level_entry.embedding_level

        level = least_greater_even(self.last_level_entry.embedding_level)
        if self.is_valid_level_and_counters(level):
            self.valid_isolate_count += 1
            self.push_levels_entry(LevelEntry(level, 'N', True))
        else:
            self.overflow_isolate_count += 1

    def X5c(self, idx):
        """X5c_, With each FSI:

        Apply rules P2 and P3 to the sequence of characters between the FSI and
        its matching PDI, or if there is no matching PDI, the end of the
        paragraph, as if this sequence of characters were a paragraph. If these
        rules decide on paragraph embedding level 1, treat the FSI as an RLI in
        rule X5a. Otherwise, treat it as an LRI in rule X5b.

        .. _X5c: http://www.unicode.org/reports/tr9/#X5c
        """
        level = self.calc_paragraph_level(islice(self.chars, 1, None))

        if level == PARAGRAPH_LEVELS['R']:
            self.X5a(idx)
        else:
            self.X5b(idx)

    def X6(self, idx):
        """X6_, For all types besides B, BN, RLE, LRE, RLO, LRO, PDF, RLI, LRI,
        FSI, and PDI:

        * Set the current character’s embedding level to the embedding level of
          the last entry on the directional status stack.
        * Whenever the directional override status of the last entry on the
          directional status stack is not neutral, reset the current character
          type according to the directional override status of the last entry
          on the directional status stack.

        .. _X6: http://www.unicode.org/reports/tr9/#X6
        """

        last_entry = self.last_level_entry
        ch = self.chars[idx]

        ch['level'] = last_entry.embedding_level

        if last_entry.directional_override != 'N':
            ch['type'] = last_entry.directional_override

    def X6a(self, idx):
        """X6a_, With each PDI, perform the following steps :


        * If the overflow isolate count is greater than zero, this PDI matches
          an overflow isolate initiator. Decrement the overflow isolate count
          by one.
        * Otherwise, if the valid isolate count is zero, this PDI does not
          match any isolate initiator, valid or overflow. Do nothing.
        * Otherwise, this PDI matches a valid isolate initiator. Perform the
          following steps:

            * Reset the overflow embedding count to zero. (This terminates the
              scope of those overflow embedding initiators within the scope of
              the matched isolate initiator whose scopes have not been
              terminated by a matching PDF, and which thus lack a matching
              PDF.)
            * While the directional isolate status of the last entry on the
              stack is false, pop the last entry from the directional status
              stack. (This terminates the scope of those valid embedding
              initiators within the scope of the matched isolate initiator
              whose scopes have not been terminated by a matching PDF, and
              which thus lack a matching PDF. Given that the valid isolate
              count is non-zero, the directional status stack must contain an
              entry with directional isolate status true before this step, and
              thus after this step the last entry on the stack will indeed have
              a true directional isolate status, i.e. represent the scope of
              the matched isolate initiator. This cannot be the stack's first
              entry, which always belongs to the paragraph level and has a
              false directional status, so there is at least one more entry
              before it on the stack.)
            * Pop the last entry from the directional status stack and
              decrement the valid isolate count by one. (This terminates the
              scope of the matched isolate initiator. Since the preceding step
              left the stack with at least two entries, this pop does not leave
              the stack empty.)

        * In all cases, set the PDI’s level to the embedding level of the last
          entry on the directional status stack left after the steps above.

        .. _X6a: http://www.unicode.org/reports/tr9/#X6a
        """

        if self.overflow_isolate_count > 0:
            self.overflow_isolate_count -= 1
        else:
            if self.valid_isolate_count != 0:
                self.overflow_embedding_count = 0

                while not self.last_level_entry.directional_isolate:
                    self.pop_levels_entry()

                self.pop_levels_entry()
                self.valid_isolate_count -= 1

        self.chars[idx]['level'] = self.last_level_entry.embedding_level

    def X7(self, idx):
        """X7_, With each PDF, perform the following steps:

        * If the overflow isolate count is greater than zero, do nothing. (This
          PDF is within the scope of an overflow isolate initiator. It either
          matches and terminates the scope of an overflow embedding initiator
          within that overflow isolate, or does not match any embedding
          initiator.)
        * Otherwise, if the overflow embedding count is greater than zero,
          decrement it by one. (This PDF matches and terminates the scope of an
          overflow embedding initiator that is not within the scope of an
          overflow isolate initiator.)
        * Otherwise, if the directional isolate status of the last entry on the
          directional status stack is false, and the directional status stack
          contains at least two entries, pop the last entry from the
          directional status stack. (This PDF matches and terminates the scope
          of a valid embedding initiator. Since the stack has at least two
          entries, this pop does not leave the stack empty.)
        * Otherwise, do nothing. (This PDF does not match any embedding
          initiator.)

        .. _X7: http://www.unicode.org/reports/tr9/#X7
        """

        if self.overflow_isolate_count == 0:

            if self.overflow_embedding_count > 0:
                self.overflow_embedding_count -= 1
            elif (not self.last_level_entry.directional_isolate
                  and len(self.levels_stack) > 1):
                self.pop_levels_entry()

    def explicit_levels_and_directions(self):
        "Applies X1-X7 (No X8 since we're handling single paragraphs)"

        MAPPINGS = {
            'RLE': self.X2,
            'LRE': self.X3,
            'RLO': self.X4,
            'LRO': self.X5,
            'RLI': self.X5a,
            'LRI': self.X5b,
            'FSI': self.X5c,
            'PDI': self.X6a,
            'PDF': self.X7,
        }
        self.X1()

        for idx, ch in enumerate(self.chars):
            ch_type = ch['type']
            method = MAPPINGS.get(ch_type)

            if method:
                method(idx)
            else:
                if ch_type not in ('BN', 'B'):
                    self.X6(idx)

    def X9(self):
        filtered = (ch for ch in self.chars if ch['type'] not in X9_REMOVED)
        self.chars = deque(filtered)

    def preparations_for_implicit_processing(self):
        "Applies X9-X10"

        self.X9()

    @property
    def display(self):

        if self._display is None:
            self.explicit_levels_and_directions()
            self.preparations_for_implicit_processing()

        return self._display


# Some definitions
EXPLICIT_LEVEL_LIMIT = 62

_LEAST_GREATER_ODD = lambda x: (x + 1) | 1
_LEAST_GREATER_EVEN = lambda x: (x + 2) & ~1

X2_X5_MAPPINGS = {
    'RLE': (_LEAST_GREATER_ODD, 'N'),
    'LRE': (_LEAST_GREATER_EVEN, 'N'),
    'RLO': (_LEAST_GREATER_ODD, 'R'),
    'LRO': (_LEAST_GREATER_EVEN, 'L'),
}

# Added 'B' so X6 won't execute in that case and X8 will run it's course
X6_IGNORED = list(X2_X5_MAPPINGS.keys()) + ['BN', 'PDF', 'B']

_embedding_direction = lambda x: ('L', 'R')[x % 2]

_IS_UCS2 = sys.maxunicode == 65535
_SURROGATE_MIN, _SURROGATE_MAX = 55296, 56319  # D800, DBFF


def debug_storage(storage, base_info=False, chars=True, runs=False):
    "Display debug information for the storage"

    import codecs
    import locale
    import sys

    stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

    caller = inspect.stack()[1][3]
    stderr.write('in %s\n' % caller)

    if base_info:
        stderr.write(u'  base level  : %d\n' % storage['base_level'])
        stderr.write(u'  base dir    : %s\n' % storage['base_dir'])

    if runs:
        stderr.write(u'  runs        : %s\n' % list(storage['runs']))

    if chars:
        output = u'  Chars       : '
        for _ch in storage['chars']:
            if _ch != '\n':
                output += _ch['ch']
            else:
                output += 'C'
        stderr.write(output + u'\n')

        output = u'  Res. levels : %s\n' % u''.join(
            [unicode(_ch['level']) for _ch in storage['chars']])
        stderr.write(output)

        _types = [_ch['type'].ljust(3) for _ch in storage['chars']]

        for i in range(3):
            if i:
                output = u'                %s\n'
            else:
                output = u'  Res. types  : %s\n'
            stderr.write(output % u''.join([_t[i] for _t in _types]))


def get_base_level(text, upper_is_rtl=False):
    """Get the paragraph base embedding level. Returns 0 for LTR,
    1 for RTL.

    `text` a unicode object.

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    """

    base_level = None

    prev_surrogate = False
    # P2
    for _ch in text:
        # surrogate in case of ucs2
        if _IS_UCS2 and (_SURROGATE_MIN <= ord(_ch) <= _SURROGATE_MAX):
            prev_surrogate = _ch
            continue
        elif prev_surrogate:
            _ch = prev_surrogate + _ch
            prev_surrogate = False

        # treat upper as RTL ?
        if upper_is_rtl and _ch.isupper():
            base_level = 1
            break

        bidi_type = bidirectional(_ch)

        if bidi_type in ('AL', 'R'):
            base_level = 1
            break

        elif bidi_type == 'L':
            base_level = 0
            break

    # P3
    if base_level is None:
        base_level = 0

    return base_level


def get_embedding_levels(text, storage, upper_is_rtl=False, debug=False):
    """Get the paragraph base embedding level and direction,
    set the storage to the array of chars"""

    prev_surrogate = False
    base_level = storage['base_level']

    # preset the storage's chars
    for _ch in text:
        if _IS_UCS2 and (_SURROGATE_MIN <= ord(_ch) <= _SURROGATE_MAX):
            prev_surrogate = _ch
            continue
        elif prev_surrogate:
            _ch = prev_surrogate + _ch
            prev_surrogate = False

        if upper_is_rtl and _ch.isupper():
            bidi_type = 'R'
        else:
            bidi_type = bidirectional(_ch)
        storage['chars'].append(
            {'ch': _ch, 'level': base_level, 'type': bidi_type, 'orig': bidi_type})
    if debug:
        debug_storage(storage, base_info=True)


def explicit_embed_and_overrides(storage, debug=False):
    """Apply X1 to X9 rules of the unicode algorithm.

    See http://unicode.org/reports/tr9/#Explicit_Levels_and_Directions

    """
    overflow_counter = almost_overflow_counter = 0
    directional_override = 'N'
    levels = deque()

    # X1
    embedding_level = storage['base_level']

    for _ch in storage['chars']:
        bidi_type = _ch['type']

        level_func, override = X2_X5_MAPPINGS.get(bidi_type, (None, None))

        if level_func:
            # So this is X2 to X5
            # if we've past EXPLICIT_LEVEL_LIMIT, note it and do nothing

            if overflow_counter != 0:
                overflow_counter += 1
                continue

            new_level = level_func(embedding_level)
            if new_level < EXPLICIT_LEVEL_LIMIT:
                levels.append((embedding_level, directional_override))
                embedding_level, directional_override = new_level, override

            elif embedding_level == EXPLICIT_LEVEL_LIMIT - 2:
                # The new level is invalid, but a valid level can still be
                # achieved if this level is 60 and we encounter an RLE or
                # RLO further on.  So record that we 'almost' overflowed.
                almost_overflow_counter += 1

            else:
                overflow_counter += 1
        else:
            # X6
            if bidi_type not in X6_IGNORED:
                _ch['level'] = embedding_level
                if directional_override != 'N':
                    _ch['type'] = directional_override

            # X7
            elif bidi_type == 'PDF':
                if overflow_counter:
                    overflow_counter -= 1
                elif almost_overflow_counter and \
                        embedding_level != EXPLICIT_LEVEL_LIMIT - 1:
                    almost_overflow_counter -= 1
                elif levels:
                    embedding_level, directional_override = levels.pop()

            # X8
            elif bidi_type == 'B':
                levels.clear()
                overflow_counter = almost_overflow_counter = 0
                embedding_level = _ch['level'] = storage['base_level']
                directional_override = 'N'

    # Removes the explicit embeds and overrides of types
    # RLE, LRE, RLO, LRO, PDF, and BN. Adjusts extended chars
    # next and prev as well

    # Applies X9. See http://unicode.org/reports/tr9/#X9
    storage['chars'] = [_ch for _ch in storage['chars']
                        if _ch['type'] not in X9_REMOVED]

    calc_level_runs(storage)

    if debug:
        debug_storage(storage, runs=True)


def calc_level_runs(storage):
    """Split the storage to run of char types at the same level.

    Applies X10. See http://unicode.org/reports/tr9/#X10
    """
    # run level depends on the higher of the two levels on either side of
    # the boundary If the higher level is odd, the type is R; otherwise,
    #it is L

    storage['runs'].clear()
    chars = storage['chars']

    # empty string ?
    if not chars:
        return

    calc_level_run = lambda b_l, b_r: ['L', 'R'][max(b_l, b_r) % 2]

    first_char = chars[0]

    sor = calc_level_run(storage['base_level'], first_char['level'])
    eor = None

    run_start = run_length = 0

    prev_level, prev_type = first_char['level'], first_char['type']

    for _ch in chars:
        curr_level, curr_type = _ch['level'], _ch['type']

        if curr_level == prev_level:
            run_length += 1
        else:
            eor = calc_level_run(prev_level, curr_level)
            storage['runs'].append({'sor': sor, 'eor': eor, 'start': run_start,
                                    'type': prev_type, 'length': run_length})
            sor = eor
            run_start += run_length
            run_length = 1

        prev_level, prev_type = curr_level, curr_type

    # for the last char/runlevel
    eor = calc_level_run(curr_level, storage['base_level'])
    storage['runs'].append({'sor': sor, 'eor': eor, 'start': run_start,
                            'type': curr_type, 'length': run_length})


def resolve_weak_types(storage, debug=False):
    """Reslove weak type rules W1 - W3.

    See: http://unicode.org/reports/tr9/#Resolving_Weak_Types

    """

    for run in storage['runs']:
        prev_strong = prev_type = run['sor']
        start, length = run['start'], run['length']
        chars = storage['chars'][start:start+length]
        for _ch in chars:
            # W1. Examine each nonspacing mark (NSM) in the level run, and
            # change the type of the NSM to the type of the previous character.
            # If the NSM is at the start of the level run, it will get the type
            # of sor.
            bidi_type = _ch['type']

            if bidi_type == 'NSM':
                _ch['type'] = bidi_type = prev_type

            # W2. Search backward from each instance of a European number until
            # the first strong type (R, L, AL, or sor) is found. If an AL is
            # found, change the type of the European number to Arabic number.
            if bidi_type == 'EN' and prev_strong == 'AL':
                _ch['type'] = 'AN'

            # update prev_strong if needed
            if bidi_type in ('R', 'L', 'AL'):
                prev_strong = bidi_type

            prev_type = _ch['type']

        # W3. Change all ALs to R
        for _ch in chars:
            if _ch['type'] == 'AL':
                _ch['type'] = 'R'

        # W4. A single European separator between two European numbers changes
        # to a European number. A single common separator between two numbers of
        # the same type changes to that type.
        for idx in range(1, len(chars) - 1):
            bidi_type = chars[idx]['type']
            prev_type = chars[idx-1]['type']
            next_type = chars[idx+1]['type']

            if bidi_type == 'ES' and (prev_type == next_type == 'EN'):
                chars[idx]['type'] = 'EN'

            if bidi_type == 'CS' and prev_type == next_type and \
                    prev_type in ('AN', 'EN'):
                chars[idx]['type'] = prev_type

        # W5. A sequence of European terminators adjacent to European numbers
        # changes to all European numbers.
        for idx in range(len(chars)):
            if chars[idx]['type'] == 'EN':
                for et_idx in range(idx-1, -1, -1):
                    if chars[et_idx]['type'] == 'ET':
                        chars[et_idx]['type'] = 'EN'
                    else:
                        break
                for et_idx in range(idx+1, len(chars)):
                    if chars[et_idx]['type'] == 'ET':
                        chars[et_idx]['type'] = 'EN'
                    else:
                        break

        # W6. Otherwise, separators and terminators change to Other Neutral.
        for _ch in chars:
            if _ch['type'] in ('ET', 'ES', 'CS'):
                _ch['type'] = 'ON'

        # W7. Search backward from each instance of a European number until the
        # first strong type (R, L, or sor) is found. If an L is found, then
        # change the type of the European number to L.
        prev_strong = run['sor']
        for _ch in chars:
            if _ch['type'] == 'EN' and prev_strong == 'L':
                _ch['type'] = 'L'

            if _ch['type'] in ('L', 'R'):
                prev_strong = _ch['type']

    if debug:
        debug_storage(storage, runs=True)


def resolve_neutral_types(storage, debug):
    """Resolving neutral types. Implements N1 and N2

    See: http://unicode.org/reports/tr9/#Resolving_Neutral_Types

    """

    for run in storage['runs']:
        start, length = run['start'], run['length']
        # use sor and eor
        chars = [{'type': run['sor']}] + storage['chars'][start:start+length] +\
                [{'type': run['eor']}]
        total_chars = len(chars)

        seq_start = None
        for idx in range(total_chars):
            _ch = chars[idx]
            if _ch['type'] in ('B', 'S', 'WS', 'ON'):
                # N1. A sequence of neutrals takes the direction of the
                # surrounding strong text if the text on both sides has the same
                # direction. European and Arabic numbers act as if they were R
                # in terms of their influence on neutrals. Start-of-level-run
                # (sor) and end-of-level-run (eor) are used at level run
                # boundaries.
                if seq_start is None:
                    seq_start = idx
                    prev_bidi_type = chars[idx-1]['type']
            else:
                if seq_start is not None:
                    next_bidi_type = chars[idx]['type']

                    if prev_bidi_type in ('AN', 'EN'):
                        prev_bidi_type = 'R'

                    if next_bidi_type in ('AN', 'EN'):
                        next_bidi_type = 'R'

                    for seq_idx in range(seq_start, idx):
                        if prev_bidi_type == next_bidi_type:
                            chars[seq_idx]['type'] = prev_bidi_type
                        else:
                            # N2. Any remaining neutrals take the embedding
                            # direction. The embedding direction for the given
                            # neutral character is derived from its embedding
                            # level: L if the character is set to an even level,
                            # and R if the level is odd.
                            chars[seq_idx]['type'] = \
                                _embedding_direction(chars[seq_idx]['level'])

                    seq_start = None

    if debug:
        debug_storage(storage)


def resolve_implicit_levels(storage, debug):
    """Resolving implicit levels (I1, I2)

    See: http://unicode.org/reports/tr9/#Resolving_Implicit_Levels

    """
    for run in storage['runs']:
        start, length = run['start'], run['length']
        chars = storage['chars'][start:start+length]

        for _ch in chars:
            # only those types are allowed at this stage
            assert _ch['type'] in ('L', 'R', 'EN', 'AN'),\
                '%s not allowed here' % _ch['type']

            if _embedding_direction(_ch['level']) == 'L':
                # I1. For all characters with an even (left-to-right) embedding
                # direction, those of type R go up one level and those of type
                # AN or EN go up two levels.
                if _ch['type'] == 'R':
                    _ch['level'] += 1
                elif _ch['type'] != 'L':
                    _ch['level'] += 2
            else:
                # I2. For all characters with an odd (right-to-left) embedding
                # direction, those of type L, EN or AN  go up one level.
                if _ch['type'] != 'R':
                    _ch['level'] += 1

    if debug:
        debug_storage(storage, runs=True)


def reverse_contiguous_sequence(chars, line_start, line_end, highest_level,
                                lowest_odd_level):
    """L2. From the highest level found in the text to the lowest odd
    level on each line, including intermediate levels not actually
    present in the text, reverse any contiguous sequence of characters
    that are at that level or higher.

    """
    for level in range(highest_level, lowest_odd_level-1, -1):
        _start = _end = None

        for run_idx in range(line_start, line_end+1):
            run_ch = chars[run_idx]

            if run_ch['level'] >= level:
                if _start is None:
                    _start = _end = run_idx
                else:
                    _end = run_idx
            else:
                if _end:
                    chars[_start:+_end+1] = \
                        reversed(chars[_start:+_end+1])
                    _start = _end = None

        # anything remaining ?
        if _start is not None:
            chars[_start:+_end+1] = \
                reversed(chars[_start:+_end+1])


def reorder_resolved_levels(storage, debug):
    """L1 and L2 rules"""

    # Applies L1.

    should_reset = True
    chars = storage['chars']

    for _ch in chars[::-1]:
        # L1. On each line, reset the embedding level of the following
        # characters to the paragraph embedding level:
        if _ch['orig'] in ('B', 'S'):
            # 1. Segment separators,
            # 2. Paragraph separators,
            _ch['level'] = storage['base_level']
            should_reset = True
        elif should_reset and _ch['orig'] in ('BN', 'WS'):
            # 3. Any sequence of whitespace characters preceding a segment
            # separator or paragraph separator
            # 4. Any sequence of white space characters at the end of the
            # line.
            _ch['level'] = storage['base_level']
        else:
            should_reset = False

    max_len = len(chars)

    # L2 should be per line
    # Calculates highest level and loweset odd level on the fly.

    line_start = line_end = 0
    highest_level = 0
    lowest_odd_level = EXPLICIT_LEVEL_LIMIT

    for idx in range(max_len):
        _ch = chars[idx]

        # calc the levels
        char_level = _ch['level']
        if char_level > highest_level:
            highest_level = char_level

        if char_level % 2 and char_level < lowest_odd_level:
            lowest_odd_level = char_level

        if _ch['orig'] == 'B' or idx == max_len - 1:
            line_end = idx
            # omit line breaks
            if _ch['orig'] == 'B':
                line_end -= 1

            reverse_contiguous_sequence(chars, line_start, line_end,
                                        highest_level, lowest_odd_level)

            # reset for next line run
            line_start = idx+1
            highest_level = 0
            lowest_odd_level = EXPLICIT_LEVEL_LIMIT

    if debug:
        debug_storage(storage)


def apply_mirroring(storage, debug):
    """Applies L4: mirroring

    See: http://unicode.org/reports/tr9/#L4

    """
    # L4. A character is depicted by a mirrored glyph if and only if (a) the
    # resolved directionality of that character is R, and (b) the
    # Bidi_Mirrored property value of that character is true.
    for _ch in storage['chars']:
        unichar = _ch['ch']
        if mirrored(unichar) and \
                _embedding_direction(_ch['level']) == 'R':
            _ch['ch'] = MIRRORED.get(unichar, unichar)

    if debug:
        debug_storage(storage)


def get_empty_storage():
    """Return an empty storage skeleton, usable for testing"""
    return {
        'base_level': None,
        'base_dir': None,
        'chars': [],
        'runs': deque(),
    }


def get_display(unicode_or_str, encoding='utf-8', upper_is_rtl=False,
                base_dir=None, debug=False):
    """Accepts unicode or string. In case it's a string, `encoding`
    is needed as it works on unicode ones (default:"utf-8").

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    Set `base_dir` to 'L' or 'R' to override the calculated base_level.

    Set `debug` to True to display (using sys.stderr) the steps taken with the
    algorithm.

    Returns the display layout, either as unicode or `encoding` encoded
    string.

    """
    storage = get_empty_storage()

    # utf-8 ? we need unicode
    if isinstance(unicode_or_str, six.text_type):
        text = unicode_or_str
        decoded = False
    else:
        text = unicode_or_str.decode(encoding)
        decoded = True

    if base_dir is None:
        base_level = get_base_level(text, upper_is_rtl)
    else:
        base_level = PARAGRAPH_LEVELS[base_dir]

    storage['base_level'] = base_level
    storage['base_dir'] = ('L', 'R')[base_level]

    get_embedding_levels(text, storage, upper_is_rtl, debug)
    explicit_embed_and_overrides(storage, debug)
    resolve_weak_types(storage, debug)
    resolve_neutral_types(storage, debug)
    resolve_implicit_levels(storage, debug)
    reorder_resolved_levels(storage, debug)
    apply_mirroring(storage, debug)

    chars = storage['chars']
    display = u''.join([_ch['ch'] for _ch in chars])

    if decoded:
        return display.encode(encoding)
    else:
        return display
