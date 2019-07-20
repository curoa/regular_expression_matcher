#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pysnooper

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
from pprint import pformat as pf

from enum import Enum

class NodeOperation(Enum):

    NUMBER = 'number'
    PLUS = 'plus'
    MINUS = 'minus'
    MULTIPLY = 'multiply'
    DIVIDE = 'divide'


class Node():

    def __init__(self, op, prev=None, _next=None, value=None):
        assert(type(op) is NodeOperation)
        assert(prev is None or isinstance(prev, Node)), pf(prev)
        assert(_next is None or isinstance(_next, Node)), pf(_next)
        self.op = op
        self.prev = prev
        self.next = _next
        self.value = value # used if op == NodeOperation.NUMBER

    @staticmethod
    def constract_number_node(value):
        return Node(NodeOperation.NUMBER, value=value)

    def __repr__(self):
        return '\n'.join(self.pf())
        #return pf(self.pf())

    def repr_vervose(self):
        return pf(vars(self))

    def pf(self, depth=0):
        """
        return list of line
        """
        out = []
        if self.prev is not None:
            out.extend(self.prev.pf(depth + 1))
        out.append(self.pf_one_node(depth))
        if self.next is not None:
            out.extend(self.next.pf(depth + 1))
        return out

    def pf_one_node(self, depth):
        """
        return str as line
        """
        if self.op == NodeOperation.NUMBER:
            line = 'value: {}'.format(self.value)
        else:
            line = 'op: {}'.format(self.op)
        out = '-' * depth + line
        return out


class MathExpressionToken(Enum):

    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    LPAR = '('
    RPAR = ')'


class Parser():
    # not handle parenthesis
    # not handle multi, devide

    node_op_encorder = {
            '+': NodeOperation.PLUS,
            '-': NodeOperation.MINUS,
            '*': NodeOperation.MULTIPLY,
            '/': NodeOperation.DIVIDE,
            }

    @staticmethod
    def make_tree(formula):
        node = Parser.parse(list(formula))
        pp('node') # debug
        pp(node) # debug
        return node

    @staticmethod
    def parse(formula):
        # only plus
        prev_node, remain = Parser.read_plus_term(formula)
        if len(remain) == 0:
            return prev_node
        op = remain[0]
        next_node = Parser.parse(remain[1:])
        node = Node(Parser.node_op_encorder[op], prev_node, next_node)
        return node

    @staticmethod
    def read_plus_term(formula):
        term = ''
        separaters = ['+', '-']
        while not (len(formula) == 0 or formula[0] in separaters):
            term += str(formula.pop(0))
        node = Node.constract_number_node(int(term))
        return node, formula


