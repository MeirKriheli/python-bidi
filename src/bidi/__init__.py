#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of python-bidi
#
# python-bidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Yaacov Zamir <kzamir_a_walla.co.il>,
# Meir kriheli <meir@mksoft.co.il>

"""
Partial implementation of Unicode Bidirectional Algorithm
http://www.unicode.org/unicode/reports/tr9/
test cases from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/

Algorithm parts implemented -
1. 3 levels of bidi nesting
2. can recognize bidi-types of Hebrew and Latin chars
3. implement bidi mirror of () and <>
"""

import string
import sys
from unicodedata import bidirectional, mirrored

def bidi_char_type(ch, upper_is_rtl=False):
    
    if upper_is_rtl and ch.isupper():
        return 'R'
    else:
        return bidirectional(ch)

def paragraph_level(unistr, upper_is_rtl=False):
    ''' partialy implements Find the Paragraph Level, Unicode 5.1.0 '''
    
    # P2: Unicode 5.1.0
    for ch in unistr:
        bidi_type = bidi_char_type(ch, upper_is_rtl)
        if bidi_type in ('R', 'L'):
            return bidi_type

    # default to L
    return 'L'

def eor_level(unistr, upper_is_rtl = False):
    ''' partialy implements end-of-level-run, Unicode 5.1.0 '''

    # not in Unicode 5.1.0
    for ch in unistr[::-1]:
        bidi_type = bidi_char_type(ch, upper_is_rtl)
        if bidi_type in ('R', 'L'):
            return bidi_type

    # default to L
    return 'L'
    
def resolve_weak_types (char_type_array, embed_level):
    ''' partialy implements Resolving Weak Types, Unicode 5.1.0 '''

    # W4: Unicode 5.1.0
    for i in range(1, len(char_type_array) - 1):
        prev_type, curr_type, next_type = char_type_array[i-1:i+2]

        if curr_type in ('ES','CS') and prev_type == 'EN' == next_type == 'EN':
            char_type_array[i] = 'EN'

    # W5: Unicode 5.1.0
    for i in range(len(char_type_array)):
        if char_type_array[i] in ('ES','CS'):
            char_type_array[i] = 'ON'

    # W7: Unicode 5.1.0
    last_strong_type = embed_level
    for i in range(len(char_type_array)):
        curr_type = char_type_array[i]
        if curr_type in('L', 'R'):
            last_strong_type = curr_type

        if curr_type == 'EN' and last_strong_type == 'L':
            char_type_array[i] = 'L'


def resolve_neutral_types (char_type_array, embed_level, eor):
    ''' partialy implements Resolving Neutral Types, Unicode 5.1.0 '''
    
    # find eor type
    
    # N1: Unicode 5.1.0
    for i in range (1, len(char_type_array) - 1):
        prev_type = char_type_array[i - 1]
        curr_type = char_type_array[i - 0]
        
        j = i + 1
        next_type = char_type_array[j]
        while j < len(char_type_array) and (next_type == 'WS' or next_type == 'ON'):
            next_type = char_type_array[j]
            j = j + 1
        if j == len(char_type_array):
            next_type = eor
            
        if prev_type == 'EN' : prev_type = 'R'
        if next_type == 'EN' : next_type = 'R'
        
        if curr_type in ('WS', 'ON') and prev_type == next_type and \
           prev_type in ('R', 'L'):
            char_type_array[i] = next_type
                
    # N2: Unicode 5.1.0
    for i in range(len(char_type_array)):
        if char_type_array[i] in ('WS', 'ON'):
            char_type_array[i] = embed_level
        
def resolve_implicit_levels (char_type_array, embed_level):
    ''' partialy implements Resolving Implicit Levels, Unicode 5.1.0
    we only implement levels 0,1 and 2'''
    
    IMPLICIT_LEVELS = {
        'L': {'L': '0 ', 'R': '1 ', 'EN': '2 '},
        'R': {'L': '2 ', 'R': '1 ', 'EN': '2 '},
    }
    IMPLICIT_TYPES = IMPLICIT_LEVELS['L'].keys()

    # I1 + I2: Unicode 5.1.0
    for i in range(len(char_type_array)):
        curr_type = char_type_array[i]
        
        if curr_type in IMPLICIT_TYPES:
            char_type_array[i] = IMPLICIT_LEVELS[embed_level][curr_type]
    
def reordering_resolved_levels (in_string, char_type_array):
    ''' partialy implements Reordering Resolved Levels, Unicode 5.1.0 
    we only implement levels 0,1 and 2'''
    
    # L2: Unicode 5.1.0
    
    # reverse level 2
    i = 0
    while i < len(char_type_array):
        curr_type = char_type_array[i]
        
        if curr_type == '2 ':
            revers_start = i
            while i < len(char_type_array) and curr_type == '2 ':
                curr_type = char_type_array[i]
                i = i + 1
                
            if i < len(char_type_array) or curr_type != '2 ':
                revers_end = i - 2
            else:
                revers_end = i - 1
                
            in_string = reverse_string (in_string, revers_start, revers_end)
            i = i - 1
            
        i = i + 1
    
    # reverse level 1
    i = 0
    while i < len(char_type_array):
        curr_type = char_type_array[i]
        
        if curr_type == '1 ' or curr_type == '2 ':
            revers_start = i
            while i < len(char_type_array) and (curr_type == '1 ' or curr_type == '2 '):
                curr_type = char_type_array[i]
                i = i + 1
                
            if i < len(char_type_array) or curr_type == '0 ':
                revers_end = i - 2
            else:
                revers_end = i - 1
            
            in_string = reverse_string (in_string, revers_start, revers_end)
            i = i - 1
            
        i = i + 1
    
    return in_string

def reverse_string (in_string, start, end):
    ''' just reverse string parts '''
    temp_string = map(lambda x:x, in_string)
    out_string = map(lambda x:x, in_string)
    
    for i in range(start, end + 1):
        out_string[i] = temp_string[start + end - i]
    
    return string.join(out_string, '')


def applay_bidi_mirrore (in_string, char_type_array):
    ''' partialy implements Bidi_Mirrored, Unicode 5.1.0 '''
    out_string = map(lambda x:x, in_string)
    
    for i in range (0, len(char_type_array)):
        curr_type = char_type_array[i]
        
        if curr_type != '0 ':
            if out_string[i] == '(':
                out_string[i] = ')'
            elif out_string[i] == ')':
                out_string[i] = '('
            if out_string[i] == '<':
                out_string[i] = '>'
            elif out_string[i] == '>':
                out_string[i] = '<'
    
    return string.join(out_string, '')
    
def string_to_letters (in_string):
    ''' string to letters array '''
    return map(lambda x: x + u' ', in_string)

def string_to_bidi_char_types (in_string, uper_is_rtl = False):
    ''' string to bidi char types array '''
    return map(lambda x: bidi_char_type(x, uper_is_rtl), in_string)

def do_bidi (in_string, uper_is_rtl = False):
    ''' wrapper for doing bidi on strings '''
    # get input
    char_array = string_to_letters (in_string)
    embed_level = paragraph_level (in_string, uper_is_rtl)
    eor = eor_level (in_string, uper_is_rtl)
    
    # get char types
    char_type_array  = string_to_bidi_char_types (in_string, uper_is_rtl)
    
    # resolve week char types
    resolve_weak_types (char_type_array, embed_level)
    
    # resolve neutral char types
    resolve_neutral_types (char_type_array, embed_level, eor)
    
    # resolve mplicit levels
    resolve_implicit_levels (char_type_array, embed_level)
    
    # applay bidi mirror
    out_string = applay_bidi_mirrore (in_string, char_type_array)

    # reorder string
    return reordering_resolved_levels (out_string, char_type_array)
    
def debug_string (in_string, uper_is_rtl = False):
    ''' wrapper for doing bidi on strings with debug information output '''
    # get input
    char_array = string_to_letters (in_string)
    embed_level = paragraph_level (in_string, uper_is_rtl)
    eor = eor_level (in_string, uper_is_rtl)
    
    # get char types
    char_type_array  = string_to_bidi_char_types (in_string, uper_is_rtl)
    
    # print input string
    print string.join(char_array, '')
    print string.join(char_type_array, '')
    
    # resolve week char types
    resolve_weak_types (char_type_array, embed_level)
    print string.join(char_type_array, '')
    
    # resolve neutral char types
    resolve_neutral_types (char_type_array, embed_level, eor)
    print string.join(char_type_array, '')
    
    # resolve mplicit levels
    resolve_implicit_levels (char_type_array, embed_level)
    print string.join(char_type_array, '')
    
    # applay bidi mirror
    out_string = applay_bidi_mirrore (in_string, char_type_array)
    
    # reorder string
    out_string = reordering_resolved_levels (out_string, char_type_array)
    
    print in_string
    print out_string
    
    # print embed level
    print 'Paragraph level: ' + paragraph_level (in_string, uper_is_rtl) + eor_level (in_string, uper_is_rtl)

def main():
        
    if len(sys.argv) == 2:
        print do_bidi(unicode(sys.argv[1], 'utf-8'), False)
        sys.exit(0)
    
    if len(sys.argv) == 3 and sys.argv[2] == '--capsrtl':
        print do_bidi(unicode(sys.argv[1], 'utf-8'), True)
        sys.exit(0)
    
    if len(sys.argv) == 3 and sys.argv[2] == '--debug':
        debug_string(unicode(sys.argv[1], 'utf-8'), False)
        sys.exit(0)
    
    if len(sys.argv) == 4 and (sys.argv[2] == '--debug' or sys.argv[3] == '--debug') \
            and (sys.argv[2] == '--capsrtl' or sys.argv[3] == '--capsrtl'):
        debug_string(unicode(sys.argv[1], 'utf-8'), True)
        sys.exit(0)
    
    print
    print
    print 'usage: pybidi.py "string" [--caprtl] [--debug]'
    print 'caprtl - Caps Latin chars are rtl (testing)'
    print 'debug - Show algorithm steps'
    
    sys.exit(1)
        
if __name__ == "__main__":
    main()
