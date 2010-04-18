"""BiDi related helpers"""

import unicodedata

DIRECTION_NEUTRAL, DIRECTION_LTR, DIRECTION_RTL = range(3)

BIDI_CATEGORIES_LTR = ('L', 'LRE', 'LRO')
BIDI_CATEGORIES_RTL = ('R', 'AL', 'RLE', 'RLO')

def get_base_direction(unistr, encoding='utf-8'):
    """Returns the base direction of `unistr`

    `unistr` can be unicde or a string which will be decoded using `encoding`
    (default: utf-8)

    Returns one of: DIRECTION_NEUTRAL, DIRECTION_LTR or DIRECTION_RTL

    """
    if not unistr:
        return DIRECTION_NEUTRAL

    # we need unicode for unicodedata
    if type(unistr) != unicode:
        unistr = unistr.decode(encoding)

    for unichar in unistr:
        bidi_category = unicodedata.bidirectional(unichar)
        if bidi_category in BIDI_CATEGORIES_LTR:
            return DIRECTION_LTR
        elif bidi_category in BIDI_CATEGORIES_RTL:
            return DIRECTION_RTL

    return DIRECTION_NEUTRAL

def logical_to_visual(unistr, encoding='utf-8'):
    pass
