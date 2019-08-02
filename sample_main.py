#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

handler = logging.FileHandler(filename="log")
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(handler)

#logger.warn('hello warn')
#logger.error('hello error')
#logger.info('hello info')
#logger.debug('hello debug')


import argparse
from pprint import pprint as pp

from syntax_tree_org import SyntaxTree

from syntax_tree import Parser
from nfa import NfaMaker
from nfa2dfa import Nfa2Dfa
from dfa_minimizer import DfaMinimizer

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This is hogehoge')
    args = parser.parse_args()

    regex = 'a(a|b)*a'
    print('regex = {}'.format(regex))

    #st = SyntaxTree(regex, debug=True)
    #st.make_tree()

    tree = Parser.run(regex)
    nfa = NfaMaker.run(tree)
    print('nfa') # debug
    print(nfa) # debug
    dfa = Nfa2Dfa.run(nfa)
    print('raw dfa') # debug
    print(dfa) # debug
    dfa = DfaMinimizer.run(dfa)
    print('dfa') # debug
    print(dfa) # debug

    true_list = [
            'aa',
            'aaa',
            'aba',
            'aaaa',
            'aaba',
            'abaa',
            'abba',
            ]
    for s in true_list:
        assert(dfa.is_accepted(s)), s

    false_list = [
            'ab',
            'ba',
            'bb',
            'baa',
            'bab',
            'bba',
            'bbb',
            'aab',
            'abb',
            'bab',
            'bbb',
            'c',
            'caaa',
            'acaa',
            'aaca',
            'aaac',
            'caba',
            'acba',
            'abca',
            'abac',
            'caaba',
            'acaba',
            'aacba',
            'aabca',
            'aabac',
            ]
    for s in false_list:
        assert(not dfa.is_accepted(s)), s

    print('\33[32m' + 'end' + '\033[0m')
