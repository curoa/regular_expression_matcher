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
import pysnooper # @pysnooper.snoop()
from pprint import pprint as pp
from pprint import pformat as pf

class HashableSet(set):
    """
    This is danger.
    use as const.
    """

    def __hash__(self):
        l = list(self)
        l.sort()
        hash_str = ''
        for v in l:
            hash_str += "{},".format(v)
        return hash_str.__hash__()

class Transitions(dict):
    """
    key is char
    value is next HashableSet as DFA state
    """

    @staticmethod
    def construct(trans_list):
        t = Transitions()
        for trans in trans_list:
            if trans.char not in t:
                t[trans.char] = HashableSet()
            t[trans.char].add(trans.to)
        return t

class Dfa:
    """
    # NoneValueProperty
    when self.states[key] does not exist, the key is not visited.
    when self.states[key] exists but has None value,
    the key is visited but indistinguishable because of epsilon transitions.
    """

    def __init__(self):
        self.states = {} # states[HashableSet as DFA state][char] = HashableSet

    def __str__(self):
        return pf(vars(self))


class DfaMaker:

    def __init__(self, nfa):
        self.nfa = nfa
        self.dfa = Dfa()

    def gen(self, hs):
        """
        care Dfa.states' NoneValueProperty
        """
        #TODO epsilon move
        assert(type(hs) == HashableSet) # hs as DFA state, as NFA state set
        if hs in self.dfa.states:
            return
        self.dfa.states[hs] = self.make_transitions(hs)
        for hs in self.dfa.states[hs].values():
            self.gen(hs)

    def make_transitions(self, hs):
        target_trans_list = []
        for nfa_key in hs:
            trans_list = self.nfa.states[nfa_key]
            target_trans_list.extend(trans_list)
        return Transitions.construct(target_trans_list)


    @staticmethod
    def run(nfa):
        """
        convert nfa to dfa
        """
        dm = DfaMaker(nfa)
        dm.gen(HashableSet([0]))
        return dm.dfa


