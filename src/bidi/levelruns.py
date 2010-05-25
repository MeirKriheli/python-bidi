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
            self.resolve_weak_w1_to_w3,
            self.resolve_weak_w4_to_w7,
        )

        for step in steps:
            step()

    def resolve_weak_w1_to_w3(self):
        """Reslove weak type rules W1 - W3.

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

        # W3. Change all ALs to R
        for ex_ch in self.chars:
            if ex_ch.bidi_type == 'AL':
                ex_ch.bidi_type = 'R'

    def resolve_weak_w4_to_w7(self):
        """Reslove weak type rules W4 - W7.

        See: http://unicode.org/reports/tr9/#W4

        """
        for ex_ch in self.chars:
            bidi_type = ex_ch.bidi_type
            prev_type = ex_ch.prev_char.bidi_type
            next_type = ex_ch.next_char.bidi_type

            # W4. A single European separator between two European numbers
            # changes to a European number. A single common separator between
            # two numbers of the same type changes to that type.
            if bidi_type == 'ES' and (prev_type == next_type == 'EN'):
                ex_ch.bidi_type = 'EN'

            if bidi_type == 'CS' and prev_type == next_type and \
                       prev_type in ('AN', 'EN'):
                ex_ch.bidi_type = prev_type

            # W5. A sequence of European terminators adjacent to European
            # numbers changes to all European numbers.
            if bidi_type == 'EN':
                prev_ex_ch = ex_ch.prev_char
                while prev_ex_ch and prev_ex_ch.bidi_type == 'ET':
                    prev_ex_ch.bidi_type == 'EN'
                    prev_ex_ch = prev_ex_ch.prev_char
                next_ex_ch = ex_ch.next_char
                while next_ex_ch and next_ex_ch.bidi_type == 'ET':
                    next_ex_ch.bidi_type == 'EN'
                    next_ex_ch = next_ex_ch.next_char

