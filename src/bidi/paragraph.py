"""bidirecional algorithm's paragraph"""

from collections import deque
from chartypes import ExChar, ExCharUpperRtl
from runs import LevelRun

PARAGRAPH_LEVELS = { 'L':0, 'AL':1, 'R': 1 }
EXPLICIT_LEVEL_LIMIT = 62

_LEAST_GREATER_ODD = lambda x: (x + 1) | 1
_LEAST_GREATER_EVEN = lambda x: (x + 2) & ~1

X2_X5_MAPPINGS = {
    'RLE': (_LEAST_GREATER_ODD, ''),
    'LRE': (_LEAST_GREATER_EVEN, ''),
    'RLO': (_LEAST_GREATER_ODD, 'R'),
    'LRO': (_LEAST_GREATER_EVEN, 'L'),
}

# Added 'B' so X6 won't execute in that case and X8 will run it's course
X6_IGNORED = X2_X5_MAPPINGS.keys() + ['BN', 'PDF', 'B']
X9_REMOVED = X2_X5_MAPPINGS.keys() + ['BN', 'PDF']

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
        self.level_runs = deque()

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

    def explicit_embed_and_overrides(self):
        """Apply X1 to X8 rules of the unicode algorithm.

        See http://unicode.org/reports/tr9/#Explicit_Levels_and_Directions

        """

        overflow_counter = almost_overflow_counter = 0
        directional_override = ''
        levels = deque()

        #X1
        embedding_level = self.level

        for ex_ch in self.storage:
            bidi_type = ex_ch.bidi_type

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
                    ex_ch.embed_level = embedding_level
                    if directional_override:
                        ex_ch.bidi_type = directional_override

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
                    embedding_level = ex_ch.embed_level =  self.level
                    directional_override = ''

    def remove_embed_and_overrides(self):
        """Removes the explicit embeds and overrides of types
        RLE, LRE, RLO, LRO, PDF, and BN. Adjusts extended chars
        next and prev as well

        Applies X9. See http://unicode.org/reports/tr9/#X9

        """
        new_storage = deque()

        for ex_ch in self.storage:
            if ex_ch.bidi_type in X9_REMOVED:
                # handle next, prev
                if ex_ch.prev_char:
                    ex_ch.prev_char.next_char = ex_ch.next_char
                if ex_ch.next_char:
                    ex_ch.next_char.prev_char = ex_ch.prev_char
            else:
                new_storage.append(ex_ch)
        self.storage = new_storage

    def split_level_runs(self):
        """Split the storage to various level runs.

        Applies X10. See http://unicode.org/reports/tr9/#X10
        """
        #run level depends on the higher of the two levels on either side of
        #the boundary If the higher level is odd, the type is R; otherwise,
        #it is L
        calc_level_run = lambda b_l, b_r: ['L', 'R'][max(b_l, b_r) % 2]

        sor = eor = None
        level_run_chars = []

        for ex_ch in self.storage:
            if not ex_ch.prev_char:
                sor = calc_level_run(self.level, ex_ch.embed_level)
                curr_level = prev_level = ex_ch.embed_level
            else:
                curr_level, prev_level = \
                    ex_ch.embed_level, ex_ch.prev_char.embed_level

            if curr_level != prev_level:
                eor = calc_level_run(prev_level, curr_level)
                lrun = LevelRun(sor, eor, level_run_chars)
                self.level_runs.append(lrun)

                sor = eor
                level_run_chars = []

            level_run_chars.append(ex_ch)

        # for the last char/runlevel
        eor = calc_level_run(curr_level, self.level)
        lrun = LevelRun(sor, eor, level_run_chars)
        self.level_runs.append(lrun)

    def reslove_level_runs(self):
        """Apply the resolving algorithms for each paragraph"""

        for lrun in self.level_runs:
            lrun.resolve()

    def reorder_resolved_levels(self):
        """L1 rules"""

        linebreaks = deque()

        # Fix next/prev links here on the fly as they were changed during
        # level run resolves. Those links will be used later on.
        self.storage[-1].next_char = None
        prev_char = None

        for ex_ch in self.storage:
            # Update prev/next if needed as they were changed during level run
            # resolves.
            if ex_ch.prev_char != prev_char:
                ex_ch.prev_char = prev_char
            if prev_char and prev_char.next_char != ex_ch:
                prev_char.next_char = ex_ch


            # L1. On each line, reset the embedding level of the following
            # characters to the paragraph embedding level:
            if ex_ch.orig_bidi_type in ('B', 'S'):
                # 1. Segment separators,
                # 2. Paragraph separators,
                ex_ch.embed_level = self.level

                # 3. Any sequence of whitespace characters preceding a segment
                # separator or paragraph separator
                prev_ws = prev_char
                while prev_ws and prev_ws.orig_bidi_type in ('BN', 'WS'):
                    prev_ws.embed_level = self.level
                    prev_ws = prev_ws.prev_char


            # store linebreaks for use in L1 clause 4
            if ex_ch.orig_bidi_type == 'B':
                linebreaks.append(ex_ch)

            prev_char = ex_ch


        for ex_ch in linebreaks:
            # 4. Any sequence of white space characters at the end of the line.
            prev_ws = ex_ch.prev_char

            while prev_ws and prev_ws in ('BN', 'WS'):
                prev_ws.embed_level = self.level
                prev_ws = prev_ws.prev_char



    def get_display(self):
        """Calls the algorithm steps, and returns the formatted display"""

        algorithm_steps = (
            self.set_storage_and_level,
            self.explicit_embed_and_overrides,
            self.remove_embed_and_overrides,
            self.split_level_runs,
            self.reslove_level_runs,
            self.reorder_resolved_levels,
        )

        for step in algorithm_steps:
            step()
