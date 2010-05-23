"""Implements the level runs of the algorithm"""

from collections import deque
from chartypes import TextOrdering

class LevelRun(object):
    """Implement the level run of the alogrithm, prepending `sor` and `eor`
    to the list and setting ExChar's next and previous chars"""

    def __init__(self, sor, eor, extended_chars):
        """Prepends `sor` and appends `eor` to extended_chars"""

        self.chars = deque(extended_chars)
        self.chars.appendleft( TextOrdering(sor) )
        self.chars.append( TextOrdering(eor) )

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, repr(self.chars))
