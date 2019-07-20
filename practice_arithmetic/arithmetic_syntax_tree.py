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
import pysnooper
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
            MathExpressionToken.PLUS.value: NodeOperation.PLUS,
            MathExpressionToken.MINUS.value: NodeOperation.MINUS,
            MathExpressionToken.MULTIPLY.value: NodeOperation.MULTIPLY,
            MathExpressionToken.DIVIDE.value: NodeOperation.DIVIDE,
            }

    def __init__(self):
        self.remain = None # store remain formula
        self.cursor = None # store reading char

    @staticmethod
    def run(formula):
        parser = Parser()
        node = parser.make_tree(formula)
        pp('node') # debug
        pp(node) # debug
        return node

    def make_tree(self, formula):
        self.remain = list(formula)
        self.move_cursor_next()
        return self.parse()

    def move_cursor_next(self):
        if len(self.remain) == 0:
            self.cursor = None
            return
        self.cursor = self.remain[0]
        self.remain.pop(0)

    def parse(self):
        return self.read_plus_minus_formura()

    def read_plus_minus_formura(self):
        end_cursors = [None]
        node = self.read_plus_minus_term()
        while not (self.cursor in end_cursors):
            op = Parser.node_op_encorder[self.cursor]
            self.move_cursor_next()
            node_next = self.read_plus_minus_term()
            node = Node(op, node, node_next)
        return node

    def read_plus_minus_term(self):
        return self.read_number_formura()

    def read_number_formura(self):
        end_cursors = [
                None,
                MathExpressionToken.PLUS.value,
                MathExpressionToken.MINUS.value,
                ]
        num_str = ''
        while not (self.cursor in end_cursors):
            num_str += self.cursor
            self.move_cursor_next()
        if len(num_str) == 0:
            return None
        node = Node.constract_number_node(int(num_str))
        return node


