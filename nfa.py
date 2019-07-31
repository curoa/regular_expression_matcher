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

from syntax_tree import NodeOperation



class Transition:

    def __init__(self, to, char):
        self.to = to
        self.char = char

    def __str__(self):
        return "to {}, char {}".format(self.to, self.char)

class Nfa:
    """
    states[src_key] = list of Transition
    """

    def __init__(self):
        self.states = [] #TODO set is better. please change class commment, too.

    def gen_node(self):
        key = len(self.states)
        self.states.append([])
        # now, you can access self.states[key]
        return key

    def add_transition(self, key_from, key_to, trans_char=None):
        trans = Transition(key_to, trans_char)
        self.states[key_from].append(trans)

    def __str__(self):
        out = ""
        for i, trans_list in enumerate(self.states):
            out += "state {}\n".format(i)
            for trans in trans_list:
                out += " {}\n".format(trans.__str__())
        return out


class NfaMaker:

    @staticmethod
    def run(tree):
        #TODO name is funny
        nfa_maker = NfaMaker(tree)
        return nfa_maker.nfa

    def __init__(self, tree):
        self.nfa = Nfa()
        start = self.nfa.gen_node()
        end = self.nfa.gen_node()
        self.gen_nfa(tree, start, end)

    def gen_nfa(self, tree, entry, way_out):
        if tree.op == NodeOperation.CHAR:
            self.nfa.add_transition(entry, way_out, tree.char)
        elif tree.op == NodeOperation.CONCAT:
            state = self.nfa.gen_node()
            self.gen_nfa(tree.prev, entry, state)
            self.gen_nfa(tree.next, state, way_out)
        elif tree.op == NodeOperation.REPEAT:
            state_rs = self.nfa.gen_node() # state of repeat start
            state_re = self.nfa.gen_node() # state of repeat end
            self.nfa.add_transition(entry, state_rs, None)
            self.gen_nfa(tree.prev, state_rs, state_re)
            self.nfa.add_transition(state_re, state_rs, None)
            self.nfa.add_transition(state_rs, way_out, None)
        elif tree.op == NodeOperation.UNION:
            self.gen_nfa(tree.prev, entry, way_out)
            self.gen_nfa(tree.next, entry, way_out)
        else:
            print("This can not happen in ")
            sys.exit(1)


