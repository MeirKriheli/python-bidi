"bidirectional alogrithm implementation"

from unicodedata import bidirectional
import sys
import inspect
from collections import deque

# Some definitions
PARAGRAPH_LEVELS = { 'L':0, 'AL':1, 'R': 1 }
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
X6_IGNORED = X2_X5_MAPPINGS.keys() + ['BN', 'PDF', 'B']
X9_REMOVED = X2_X5_MAPPINGS.keys() + ['BN', 'PDF']

def debug_storage(storage, base_info=False, chars=True):
    "Display debug information for the storage"

    caller = inspect.stack()[1][3]
    sys.stderr.write('in %s\n' % caller)

    if base_info:
        sys.stderr.write(u'  base level : %d\n' % storage['base_level'])
        sys.stderr.write(u'  base dir   : %s\n' % storage['base_dir'])

    if chars:
        output = u'  Chars       : '
        for _ch in storage['chars']:
            if _ch != '\n':
                output += _ch['ch']
            else:
                output += 'C'
        sys.stderr.write(output + u'\n')

        output = u'  Res. levels : %s\n' % u''.join(
            [unicode(_ch['level']) for _ch in storage['chars']])
        sys.stderr.write(output)

        _types = [_ch['type'].ljust(3) for _ch in storage['chars']]

        for i in range(3):
            if i:
                output = u'                %s\n'
            else:
                output = u'  Res. types  : %s\n'
            sys.stderr.write(output % u''.join([_t[i] for _t in _types]))

def get_embedding_levels(text, storage, upper_is_rtl=False, debug=False):
    """Get the paragraph base embedding level and direction,
    set the storage to the array of chars"""

    base_level = None

    # P2
    for _ch in text:
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

    storage['base_level'] = base_level
    storage['base_dir'] = ('L', 'R')[base_level]

    # preset the storage's chars
    for _ch in text:
        bidi_type = bidirectional(_ch)
        storage['chars'].append({'ch':_ch, 'level':base_level, 'type':bidi_type,
                                 'orig':bidi_type})
    if debug:
        debug_storage(storage, base_info=True)

def explicit_embed_and_overrides(storage, debug=False):
    """Apply X1 to X8 rules of the unicode algorithm.

    See http://unicode.org/reports/tr9/#Explicit_Levels_and_Directions

    """
    overflow_counter = almost_overflow_counter = 0
    directional_override = 'N'
    levels = deque()

    #X1
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
                levels.append( (embedding_level, directional_override) )
                embedding_level, directional_override = new_level, override

            elif embedding_level == EXPLICIT_LEVEL_LIMIT -2:
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

    if debug:
        debug_storage(storage)


def get_display(unicode_or_str, encoding='utf-8', upper_is_rtl=False,
                debug=False):
    """Accepts unicode or string. In case it's a string, `encoding`
    is needed as it works on unicode ones (default:"utf-8").

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    Set `debug` to True to display the steps taken with the algorithm"

    """
    # create a skeleton to work on
    storage = {
        'base_level': None,
        'base_dir' : None,
        'chars': [],
    }

    # utf-8 ? we need unicode
    if isinstance(unicode_or_str, unicode):
        text = unicode_or_str
    else:
        text = unicode_or_str.decode(encoding)

    get_embedding_levels(text, storage, upper_is_rtl, debug)
    explicit_embed_and_overrides(storage, debug)

    return 'yo'
