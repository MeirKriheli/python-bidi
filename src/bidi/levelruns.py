"""Implements the level runs of the algorithm"""

from collections import deque
from chartypes import TextOrdering

class LevelRun(object):
    """Implement the level run of the alogrithm, prepending `sor` and `eor`
    to the list and setting ExChar's next and previous chars"""

    def __init__(self, sor, eor, extended_chars):
        """Prepends `sor` and appends `eor` to extended_chars"""

        self.chars = deque(extended_chars)

        # create sor and eor
        self.sor = TextOrdering(sor, next_char=self.chars[0])
        self.eor = TextOrdering(eor, prev_char=self.chars[-1])

        # update prev and next of chars
        self.chars[0].prev_char = self.sor
        self.chars[-1].next_char = self.eor

    def __repr__(self):

        return '<%s: (%s, %d %s of level %d, %s)>' % \
            (self.__class__.__name__, self.sor, len(self.chars),
            self.chars[0].__class__.__name__, self.chars[0].embed_level,
            self.eor)

    def resolve(self):
        """Apply level run resolves"""

        steps = (
            self.resolve_weak_w1_w2,
        )

        for step in steps:
            step()

    def resolve_weak_w1_w2(self):
        """Reslove weak type rules W1 and W2.

        See: http://unicode.org/reports/tr9/#W1

        """
        prev_strong = self.sor.bidi_type

        for ex_ch in self.chars:
            # W1. Examine each nonspacing mark (NSM) in the level run, and
            # change the type of the NSM to the type of the previous character.
            # If the NSM is at the start of the level run, it will get the type
            # of sor.
            bidi_type = ex_ch.bidi_type
            if bidi_type == 'NSM':
                ex_ch.bidi_type = bidi_type = ex_ch.prev_char.bidi_type

            # W2. Search backward from each instance of a European number until
            # the first strong type (R, L, AL, or sor) is found. If an AL is
            # found, change the type of the European number to Arabic number.
            if bidi_type == 'EN' and prev_strong == 'AL':
                ex_ch.bidi_type = 'AN'

            # update prev_strong if needed
            if bidi_type in ('R', 'L', 'AL'):
                prev_strong = bidi_type
