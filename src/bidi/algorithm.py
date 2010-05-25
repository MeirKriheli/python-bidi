"""Implements Unicode 5.2.0 Bidirectional Algorithm"""

from paragraph import Paragraph

if __name__ == '__main__':
    import pprint
    uni_str = u'<H123>shalom</H123>'
    uni_str = u'''DID YOU SAY '\u202Ahe said "\u202Bcar MEANS CAR\u202C"\u202C'?'''

    #p_level = paragraph_level(uni_str, bidirectional_uppercase_rtl)
   #
    #ex_chars = map_unistr(uni_str, bidirectional_uppercase_rtl)
    #ex_chars_with_levels = explicit_embeddings_and_overrides(ex_chars, p_level)

    #run_levels = list(resolve_runlevels(ex_chars_with_levels, p_level))
    #pprint.pprint(run_levels)

    #run_levels_weak_resolved = [resolve_weak_types(*l) for l in run_levels]
    #pprint.pprint(run_levels_weak_resolved)

    #run_levels_neutral_resolved = [resolve_neutral_types(*l) for l in run_levels_weak_resolved]
    #pprint.pprint(run_levels_neutral_resolved)

    p = Paragraph(uni_str, upper_is_rtl=True)
    p.get_display()

    pprint.pprint(p.storage)
    for lrun in p.level_runs:
        pprint.pprint(lrun)
    print len(p.level_runs), p.level
    pprint.pprint(list(p.storage))
