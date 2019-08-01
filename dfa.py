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


