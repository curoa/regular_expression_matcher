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

class DfaMinimizer:

    def __init__(self, dfa):
        self.dfa = dfa

    def split_by_accepted_or_not(self, sf):
        """
        split DFA states by accepted or not

        sf: initialized SplitFind

        update sf
        """
        split = {True: set(), False: set()}
        accepted_nfa_key = 1 #FIXME hard cording
        for state in self.dfa.states:
            key = (accepted_nfa_key in state)
            split[key].add(state)
        for dfa_ids in split.values():
            sf.split(dfa_ids)

    def split_by_distinguishable(self, sf):
        """
        split DFA states by accepted or not

        sf: SplitFind split by accepted or not

        update sf
        """
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

    def make_new_dfa_with_new_ids(self, sf):
        """
        sf: SplitFind
        """
        new_dfa = Dfa()
        # make new_dfa with new ids
        for state in self.dfa.states.keys():
            assert(self.dfa.states[state] is not None)
            converted = sf.find(state)
            new_dfa.states[converted] = {}
            for char, dst in self.dfa.states[state].items():
                new_dfa.states[converted][char] = sf.find(dst)
        # register start_key, accepted_keys
        start_nfa_key = 0 #FIXME hard cording
        accepted_nfa_key = 1 # FIXME hard cording
        for old_key, new_key in sf.arr.items():
            assert(type(old_key) is HashableSet)
            if accepted_nfa_key in old_key:
                new_dfa.accepted_keys.add(new_key)
            elif start_nfa_key in old_key:
                new_dfa.start_key = new_key
        return new_dfa

    def minimize_dfa_states(self):
        sf = SplitFind(self.dfa.get_state_ids())
        self.split_by_accepted_or_not(sf)
        self.split_by_distinguishable(sf)
        sf.slim()
        new_dfa = self.make_new_dfa_with_new_ids(sf)
        self.dfa = new_dfa

    @staticmethod
    def run(dfa):
        dm = DfaMinimizer(dfa)
        dm.minimize_dfa_states()
        return dm.dfa


