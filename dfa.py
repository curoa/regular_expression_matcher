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

from split_find import SplitFind

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
    """

    def __init__(self):
        self.states = {} # states[DFA_state][char] = DFA_state. DFA_state is HashableSet or int
        # key means DFA_state as key of self.states
        self.start_key = None # int or None
        self.accepted_keys = set()

    def __str__(self):
        return pf(vars(self))

    def get_state_ids(self):
        state_ids = set()
        for state in self.states:
            assert(type(state) is HashableSet or state is None)
            state_ids.add(state)
            if self.states[state] is None:
                continue
            for val in self.states[state].values():
                assert(type(val) is HashableSet)
                state_ids.add(val)
        return state_ids

    def get_alphabets(self):
        alphabets = set()
        for state in self.states:
            assert(type(state) is HashableSet or state is None)
            if self.states[state] is None:
                continue
            alphabets = alphabets.union(self.states[state].keys())
        return alphabets


class DfaMaker:

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
        hs_extended, trans_dict = self.for_next_dfa_state(hs)
        if hs != hs_extended:
            self.epsilon_extented[hs] = hs_extended
        self.dfa.states[hs_extended] = Transitions.construct(trans_dict)
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

    def unify_epsilon_extented(self):
        for state in list(self.dfa.states.keys()): # use list() to change dict size during iteration
            if self.dfa.states[state] is None:
                del self.dfa.states[state]
                continue
            for char in self.dfa.states[state]:
                dfa_state = self.dfa.states[state][char]
                unified = self.epsilon_extented.get(dfa_state, dfa_state)
                self.dfa.states[state][char] = unified

    def minimize_dfa_states(self):
        sf = SplitFind(self.dfa.get_state_ids())
        # split by accepted or not
        split = {True: set(), False: set()}
        accepted_nfa_key = 1 #FIXME hard cording
        for state in self.dfa.states:
            key = (accepted_nfa_key in state)
            split[key].add(state)
        for dfa_ids in split.values():
            sf.split(dfa_ids)
        # split by distinguishable
        bef_count_cells = -1
        while not (sf.count_cells() == bef_count_cells):
            bef_count_cells = sf.count_cells()
            for char in self.dfa.get_alphabets():
                split = {}
                # calc split
                for state in self.dfa.states.keys():
                    dst = self.dfa.states[state].get(char)
                    cell_id = sf.find(dst)
                    if cell_id not in split:
                        split[cell_id] = set()
                    split[cell_id].add(state)
                # split
                for dfa_ids in split.values():
                    sf.split(dfa_ids)
        # convert dfa ids
        sf.slim()
        new_dfa = Dfa()
        #TODO state is bad name, state_key is correct. check other place, too.
        for state in list(self.dfa.states.keys()): # use list() to change dict size during iteration
            assert(self.dfa.states[state] is not None)
            converted = sf.find(state)
            new_dfa.states[converted] = {}
            for char, dst in self.dfa.states[state].items():
                new_dfa.states[converted][char] = sf.find(dst)
        start_nfa_key = 0 #FIXME hard cording
        accepted_nfa_key = 1 # FIXME hard cording
        for old_key, new_key in sf.arr.items():
            assert(type(old_key) is HashableSet)
            if accepted_nfa_key in old_key:
                new_dfa.accepted_keys.add(new_key)
            elif start_nfa_key in old_key:
                new_dfa.start_key = new_key
        self.dfa = new_dfa

    def slim(self):
        print('self.dfa') # debug
        print(self.dfa) # debug
        self.unify_epsilon_extented()
        self.minimize_dfa_states()

    @staticmethod
    def run(nfa):
        dm = DfaMaker(nfa)
        dm.convert(HashableSet([0]))
        print('dm.epsilon_extented') # debug
        print(dm.epsilon_extented) # debug
        dm.slim()
        return dm.dfa


