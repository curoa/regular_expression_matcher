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

from dfa import Dfa, Transitions, HashableSet
from split_find import SplitFind

class Nfa2Dfa:
    """
    NFA state n_i \in N
    DFA state d_i \in D
    d_i \subset N
    D \subset 2^N
    """

    def __init__(self, nfa):
        self.nfa = nfa
        self.dfa = Dfa()
        self.epsilon_extented = {} # key is HashableSet, value is HashableSet

    def convert(self, hs):
        """
        convert nfa to dfa

        handle Dfa.states without Dfa.start_key, Dfa.accepted_keys

        handle Dfa.states with NoneValueProperty
        # NoneValueProperty
        when Dfa.states[key] does not exist, the key is not visited.
        when Dfa.states[key] exists but has None value,
        the key is visited but indistinguishable because of epsilon transitions.
        """
        assert(type(hs) == HashableSet) # hs as DFA state, as NFA state set
        if hs in self.dfa.states:
            return
        self.dfa.states[hs] = None
        hs_extended, trans_dict = self.extend_by_epsilon(hs)
        if hs != hs_extended:
            self.epsilon_extented[hs] = hs_extended
        self.dfa.states[hs_extended] = Transitions.construct(trans_dict)
        for hs in self.dfa.states[hs_extended].values():
            self.convert(hs)

    def extend_by_epsilon(self, _hs):
        """
        Extend DFA state by epsilon transition.
        extended state is super set of original state.
        epsilon transition is represented by None char Transition.

        return target_trans_list, too.
        target_trans_list is union of Extend DFA states' trans list
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

    def unify_epsilon_extented(self):
        for state in list(self.dfa.states.keys()): # use list() to change dict size during iteration
            if self.dfa.states[state] is None:
                del self.dfa.states[state]
                continue
            for char in self.dfa.states[state]:
                dfa_state = self.dfa.states[state][char]
                unified = self.epsilon_extented.get(dfa_state, dfa_state)
                self.dfa.states[state][char] = unified


    @staticmethod
    def run(nfa):
        n2d = Nfa2Dfa(nfa)
        n2d.convert(HashableSet([0]))
        n2d.unify_epsilon_extented()
        return n2d.dfa


