from unicodedata import bidirectional, mirrored
from collections import namedtuple

PARAGRAPH_LEVELS = { 'L':0, 'AL':1, 'R': 1 }

ExtendedChar = namedtuple('ExtendedChar', 'ch biditype level')

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
    '''Return a list of ExtendedChar for each char mapped to it's bidirectional
    type and embeding level. 
    
    This will be used by the algorithm implemention for resolving

    '''
    return [ExtendedChar(ch, bidi_char_type_func(ch), None) for ch in unistr]
    
def explicit_embeddings_and_overrides(extended_chars, paragraph_level=None):
    '''Calucalte the levels taking into account Explicit Embeddings and
    Explicit Overrides.

    Implements X1-X9.

    '''

    for ex_ch in extended_chars:
        pass


if __name__ == '__main__':
    unistr = u'<H123>shalom</H123>'
    p_level = paragraph_level(unistr, bidirectional_uppercase_rtl)
    
    ex_chars = map_unistr(unistr, bidirectional_uppercase_rtl)

    print ex_chars
