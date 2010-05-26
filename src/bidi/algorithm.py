"""Implements Unicode 5.2.0 Bidirectional Algorithm"""

from paragraph import Paragraph

if __name__ == '__main__':
    uni_str = u'<H123>shalom</H123>'
    #uni_str = u'''DID YOU SAY '\u202Ahe said "\u202Bcar MEANS CAR\u202C"\u202C'?'''

    p = Paragraph(uni_str, upper_is_rtl=True)
    print p.get_display()
