"""Varoius char types for the algorithm implementation"""
import unicodedata

class ExChar(object):
    """Extended char for unicode bidirectional algorithm"""

    def __init__(self, unicode_char, prev_char=None, next_char=None):
        """Get the unicode_char and pre populate the fields"""

        self.uni_char = unicode_char
        self.bidi_type = unicodedata.bidirectional(unicode_char)

        # Those will be filled later on by the algorithm
        self.embed_level = None
        self.prev_char, self.next_char = prev_char, next_char

    
    def get_embedding_direction(self):
        """
        The default direction of the current embedding level (for the
        character in question) is called the embedding direction. It
        is L if the embedding level is even, and R if the embedding
        level is odd.

        See http://unicode.org/reports/tr9/#BD3

        """
        if self.embed_level % 2:
            return 'R'
        else:
            return 'L'
    
    embedding_direction = property(get_embedding_direction)

    @property
    def next_bidi_type(self):
        """Return the next char's bidirectional type"""

        if self.next_char:
            return self.next_char.bidi_type

        return None

    @property
    def prev_bidi_type(self):
        """Return the prev char's bidirectional type"""

        if self.prev_char:
            return self.prev_char.bidi_type

        return None

    def __repr__(self):
        return u'<%s %s (bidi type:%s)>' % (self.__class__.__name__,
                                unicodedata.name(self.uni_char), self.bidi_type)

class ExCharUpperRtl(ExChar):
    """An extended char which treats upper case chars as a strong 'R'
    (for debugging purpose)

    """

    def __init__(self, unicode_char, prev_char=None, next_char=None):
        """Treats unicode_char's bidi_type as strong R in case of
        upper case.

        """
        super(ExCharUpperRtl, self).__init__(unicode_char, prev_char, next_char)

        if unicode_char.isupper():
            self.bidi_type = 'R'

class TextOrdering(object):
    """Dummy ExChar like, used for algorithm's `sor` and `eor`"""

    def __init__(self, bidi_type):
        """Set `bidi_type` to L or R"""

        self.bidi_type = bidi_type
