"""bidirecional algorithm's paragraph"""

from collections import deque
from chartypes import ExChar, ExCharUpperRtl

PARAGRAPH_LEVELS = { 'L':0, 'AL':1, 'R': 1 }

class Paragraph(object):
    """The entry point for the bidirecional algorithm.
    
    Implement X1-X10 including spliting to run levels.
    
    """


    def __init__(self, unicode_or_str, encoding='utf-8', upper_is_rtl=False):
        """Accepts unicode or string. In case it's a string, `encoding`
        is needed as it works on unicode ones (default:"utf-8").

        Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
        for debugging (default: False).
        """

        if isinstance(unicode_or_str, unicode):
            self.text = unicode_or_str
        else:
            self.text = unicode_or_str.decode(encoding)

        self.storage = deque()
        self.level = None

        if upper_is_rtl:
            self._char_type = ExCharUpperRtl
        else:
            self._char_type = ExChar

    def set_storage_and_level(self):
        """Maps the paragraph text to extended chars and sets the paragraph
        embedding level (P2 and P3).

        """
        prev = None
        for unicode_char in self.text:
            extended_char = self._char_type(unicode_char, prev_char=prev)
            self.storage.append(extended_char)

            # P2
            if self.level is None:
                self.level = PARAGRAPH_LEVELS.get(extended_char.bidi_type, None)

            if prev:
                prev.next_char = extended_char

            prev = extended_char

        # P3
        if self.level is None:
            self.level = PARAGRAPH_LEVELS['L']

    def get_display(self):

        algorithm_steps = [ self.set_storage_and_level ]

        for step in algorithm_steps:
            step()
