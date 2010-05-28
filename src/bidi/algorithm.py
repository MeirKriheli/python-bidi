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

def debug_storage(storage, base_info=False, chars=True, runs=False):
    "Display debug information for the storage"

    caller = inspect.stack()[1][3]
    sys.stderr.write('in %s\n' % caller)

    if base_info:
        sys.stderr.write(u'  base level  : %d\n' % storage['base_level'])
        sys.stderr.write(u'  base dir    : %s\n' % storage['base_dir'])

    if runs:
        sys.stderr.write(u'  runs        : %s\n' % list(storage['runs']))

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
        if upper_is_rtl and _ch.isupper():
            bidi_type = 'R'
        else:
            bidi_type = bidirectional(_ch)
        storage['chars'].append({'ch':_ch, 'level':base_level, 'type':bidi_type,
                                 'orig':bidi_type})
    if debug:
        debug_storage(storage, base_info=True)

def explicit_embed_and_overrides(storage, debug=False):
    """Apply X1 to X9 rules of the unicode algorithm.

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

    #Removes the explicit embeds and overrides of types
    #RLE, LRE, RLO, LRO, PDF, and BN. Adjusts extended chars
    #next and prev as well

    #Applies X9. See http://unicode.org/reports/tr9/#X9
    storage['chars'] = [_ch for _ch in storage['chars']\
                        if _ch not in X9_REMOVED]

    calc_level_runs(storage)

    if debug:
        debug_storage(storage, runs=True)

def calc_level_runs(storage):
    """Split the storage to run of char types at the same level.

    Applies X10. See http://unicode.org/reports/tr9/#X10
    """
    #run level depends on the higher of the two levels on either side of
    #the boundary If the higher level is odd, the type is R; otherwise,
    #it is L

    storage['runs'].clear()
    chars = storage['chars']

    #empty string ?
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

        if curr_level == prev_level and curr_type == prev_type:
            run_length += 1
        else:
            eor = calc_level_run(prev_level, curr_level)
            storage['runs'].append({'sor':sor, 'eor':eor, 'start':run_start,
                            'type': prev_type,'length': run_length})
            sor = eor
            run_start += run_length
            run_length = 1

        prev_level, prev_type = curr_level, curr_type

    # for the last char/runlevel
    eor = calc_level_run(curr_level, storage['base_level'])
    storage['runs'].append({'sor':sor, 'eor':eor, 'start':run_start,
                            'type':curr_type, 'length': run_length})

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
                _ch['type']= bidi_type = prev_type

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
        for idx in range(1, len(chars) -1 ):
            bidi_type = chars[idx]['type']
            prev_type = chars[idx-1]['type']
            next_type = chars[idx-1]['type']

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
                        chars[et_idx]['type'] == 'EN'
                    else:
                        break
                for et_idx in range(idx+1, len(chars)):
                    if chars[et_idx]['type'] == 'ET':
                        chars[et_idx]['type'] == 'EN'
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
        'runs' : deque(),
    }

    # utf-8 ? we need unicode
    if isinstance(unicode_or_str, unicode):
        text = unicode_or_str
    else:
        text = unicode_or_str.decode(encoding)

    get_embedding_levels(text, storage, upper_is_rtl, debug)
    explicit_embed_and_overrides(storage, debug)
    resolve_weak_types(storage, debug)

    return 'yo'
