from unicodedata import bidirectional, mirrored
from collections import namedtuple, deque

PARAGRAPH_LEVELS = { 'L':0, 'AL':1, 'R': 1 }

def bidirectional_uppercase_rtl(ch):
    '''Return the bidirectional type of a unicode char, treating upper
    case as RTL for testing.

    '''
    if ch.isupper():
        return 'R'

    return bidirectional(ch)

def paragraph_level(unistr, bidi_char_type_func=bidirectional):
    '''Return the paragraph embeding level.  Implements P2 and P3.
    
    `unistr` is a unicode object. Treating upper case as RTL can
    be used be setting `bidi_char_type_func` to `bidirectional_uppercase_rtl`

    '''
    for ch in unistr:
        embed_level = PARAGRAPH_LEVELS.get(bidi_char_type_func(ch), None)
        if embed_level is not None:
            return embed_level

    # default to zero, as specified in P3
    return PARAGRAPH_LEVELS['L']

def map_unistr(unistr, bidi_char_type_func=bidirectional):
    '''Return a list of Extended char dicts for each char mapped to it's bidirectional
    type and embeding level. e.g: 
    
    [{'ch':'A', biditype:'L, level:None}...]

    This will be used by the algorithm implemention for resolving

    '''
    return [{'ch':ch, 'biditype':bidi_char_type_func(ch), 'level':None} \
            for ch in unistr]
    
def explicit_embeddings_and_overrides(extended_chars, paragraph_level=None):
    '''Calucalte the levels taking into account Explicit Embeddings and
    Explicit Overrides. Yields an ExtendedChar with levels set
    only in case of X6 and X8, thus implementing X9

    Implements X1-X9.

    '''
    
    EXPLICIT_LEVEL_LIMIT = 62

    # if no paragraph_level default to 'L'. This is safe to do here as it
    # if paragraph_level is None or 0, it still works (0 will remain 0 after
    #  `or`). We also need to preserve the paragraph_level for X8 rule.
    #
    # Rule X1
    paragraph_level = paragraph_level or PARAGRAPH_LEVELS['L']
    embedding_level = paragraph_level 
    directional_override = ''

    queue = deque()
    overflow_counter = almost_overflow_counter = 0

    least_greater_odd = lambda x: (x + 1) | 1
    least_greater_even = lambda x: (x + 2) & ~1

    RULES_MAPPINGS = {
        'RLE': (least_greater_odd, ''),
        'LRE': (least_greater_even, ''),
        'RLO': (least_greater_odd, 'R'),
        'LRO': (least_greater_even, 'L'),
    }
    RULES_MAPPINGS_KEYS = RULES_MAPPINGS.keys()
    
    # Added 'B' so X6 won't execute in that case and X8 will run it's course
    RULE_X6_IGNORED = RULES_MAPPINGS_KEYS + ['BN', 'PDF', 'B'] 

    for ex_ch in extended_chars:
        biditype = ex_ch['biditype']

        #X2, X3, X4, X5 rules
        if biditype in RULES_MAPPINGS_KEYS:
            if overflow_counter != 0:
                overflow_counter += 1
                continue

            level_func, override = RULES_MAPPINGS[biditype]
            new_level = level_func(embedding_level)

            if new_level < EXPLICIT_LEVEL_LIMIT:
                queue.append( (embedding_level, directional_override) )
                embedding_level, directional_override = new_level, override

            elif embedding_level == 60:
                # The new level is invalid, but a valid level can still be
                # achieved if this level is 60 and we encounter an RLE or 
                # RLO further on.  So record that we 'almost' overflowed.
                almost_overflow_counter += 1

            else:
                overflow_counter += 1

        #X6 rule
        elif biditype not in RULE_X6_IGNORED:
            ex_ch['level'] = embedding_level
            if directional_override:
                ex_ch.biditype = directional_override

            yield ex_ch

        #X7 rule
        elif biditype == 'PDF':
            if overflow_counter:
                overflow_counter -= 1
            elif almost_overflow_counter and embedding_level != 61:
                almost_overflow_counter -= 1
            elif queue:
                embedding_level, directional_override = queue.pop()
        
        #X8 rule
        elif biditype == 'B':
            queue.clear()
            overflow_counter = almost_overflow_counter = 0
            embedding_level = ex_ch['level'] =  paragraph_level 
            directional_override = ''

            yield ex_ch

def resolve_runlevels(extended_chars, paragraph_level=None):
    """Split to chars of same run level and `sor` and `eor` for each level.

    Yields (sor, eor, [extended chars....])

    Implements X10.

    """
    paragraph_level = paragraph_level or PARAGRAPH_LEVELS['L']
    
    #run level depends on the higher of the two levels on either side of the 
    #boundary If the higher level is odd, the type is R; otherwise, it is L
    calc_runlevel = lambda b_left, b_right: ['L', 'R'][max(b_left, b_right) % 2]

    level_chars = []
    sor = None
    prev_char = None

    for ex_ch in extended_chars:
        if prev_char:
            curr_level, prev_level = ex_ch['level'], prev_char['level']
        else:
            # First char
            curr_level = prev_level = ex_ch['level']
            sor = calc_runlevel(paragraph_level, curr_level)

        if prev_level != curr_level:
            eor = calc_runlevel(prev_level, curr_level)
            yield (sor, eor, level_chars)

            sor = eor
            level_chars = []

        prev_char = ex_ch
        level_chars.append(ex_ch)

    # for the last char/runlevel
    eor = calc_runlevel(curr_level, paragraph_level)
    yield (sor, eor, level_chars)

if __name__ == '__main__':
    unistr = u'<H123>shalom</H123>'
    unistr = u'''DID YOU SAY '\u202Ahe said "\u202Bcar MEANS CAR\u202C"\u202C'?'''
    p_level = paragraph_level(unistr, bidirectional_uppercase_rtl)
    
    ex_chars = map_unistr(unistr, bidirectional_uppercase_rtl)
    ex_chars_with_levels = explicit_embeddings_and_overrides(ex_chars, p_level)

    run_levels = resolve_runlevels(ex_chars_with_levels, p_level)
