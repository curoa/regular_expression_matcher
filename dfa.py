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

    def hash_str(self):
        l = list(self)
        l.sort()
        hash_str = ''
        for v in l:
            hash_str += "{},".format(v)
        return hash_str

    def __hash__(self):
        return self.hash_str().__hash__()

    def __repr__(self):
        return "@" + self.hash_str()[:-1] + "/"


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
        self.indistinguishables = {} # key is HashableSet, value is HashableSet

    def convert(self, hs):
        """
        convert nfa to dfa

        care Dfa.states' NoneValueProperty
        """
        assert(type(hs) == HashableSet) # hs as DFA state, as NFA state set
        if hs in self.dfa.states:
            return
        self.dfa.states[hs] = None
        hs_extended, trans_dict = self.for_next_dfa_state(hs)
        if hs != hs_extended:
            self.indistinguishables[hs] = hs_extended
        self.dfa.states[HashableSet(hs_extended)] = Transitions.construct(trans_dict)
        for hs in self.dfa.states[hs_extended].values():
            self.convert(hs)

    def for_next_dfa_state(self, _hs):
        """
        途中で通ったNFAstateを追加
        Noneがあれば、さらにたどる
        hs_extended を返す。hs_extended にある trans をまとめる
        """
        hs = HashableSet(_hs)
        assert(id(hs) != id(_hs))
        target_trans_list = []
        next_nfa_states = set(hs) # stores distinations of epsilon_transition
        while not (len(next_nfa_states) == 0):
            # one step epsilon transition
            s = set()
            for nfa_key in next_nfa_states:
                for trans in self.nfa.states[nfa_key]:
                    if trans.char is None:
                        s.add(trans.to)
                    else:
                        target_trans_list.append(trans)
            next_nfa_states = s - hs
            hs = hs.union(next_nfa_states) # HashableSet.union returning HashableSet is better.
        return HashableSet(hs), target_trans_list

    def slim(self):
        pass

    @staticmethod
    def run(nfa):
        dm = DfaMaker(nfa)
        dm.convert(HashableSet([0]))
        print('dm.indistinguishables') # debug
        print(dm.indistinguishables) # debug
        dm.slim()
        return dm.dfa


