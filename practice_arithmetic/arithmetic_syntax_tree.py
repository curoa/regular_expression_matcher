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

    NUMBER = 'number' #FIXME I want to change to OPERAND
    PLUS = 'plus'
    MINUS = 'minus'
    MULTIPLY = 'multiply'
    DIVIDE = 'divide'


class Node():

    flg_tree_view = None # used pf()

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

    def __str__(self):
        return '\n'.join(self.pf())

    def __repr__(self):
        return pf(vars(self))

    def pf(self, flg_tree_view=True):
        Node.flg_tree_view = flg_tree_view
        depth = 0
        return self._pf(depth)

    def pf_as_tree(self):
        return self.pf(flg_tree_view=True)

    def pf_as_order(self):
        return self.pf(flg_tree_view=False)

    def _pf(self, depth):
        """
        return list of line
        """
        self_line = self.pf_one_node(depth)
        prev_out = self.prev._pf(depth + 1) if self.prev else []
        next_out = self.next._pf(depth + 1) if self.next else []
        out = []
        if Node.flg_tree_view:
            out.extend(prev_out)
            out.append(self_line)
            out.extend(next_out)
        else:
            out.extend(prev_out)
            out.extend(next_out)
            out.append(self_line)
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
    SPAR = '(' # start of parenthesis
    EPAR = ')' # end of parenthesis


class Parser():
    # not handle parenthesis

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
        return node

    def make_tree(self, formula):
        self.remain = list(formula)
        self.move_cursor_next() # set cursor start of formula
        return self.parse()

    def parse_binary_operator(self, end_cursors, read_term_func):
        node = read_term_func(end_cursors)
        while not (self.cursor in end_cursors):
            op = Parser.node_op_encorder[self.cursor]
            self.move_cursor_next()
            node_next = read_term_func(end_cursors)
            node = Node(op, node, node_next)
        return node


    def move_cursor_next(self):
        if len(self.remain) == 0:
            self.cursor = None
            return
        self.cursor = self.remain[0]
        self.remain.pop(0)

    def parse(self):
        end_cursors = [None, MathExpressionToken.EPAR.value]
        return self.parse_plus_minus_formura(end_cursors)

    def parse_plus_minus_formura(self, end_cursors):
        return self.parse_binary_operator(end_cursors, self.read_plus_minus_term)

    def read_plus_minus_term(self, parent_end_cursors):
        end_cursors = [
                MathExpressionToken.PLUS.value,
                MathExpressionToken.MINUS.value,
                ]
        end_cursors.extend(parent_end_cursors)
        return self.parse_multiply_devide_formura(end_cursors)

    def parse_multiply_devide_formura(self, end_cursors):
        return self.parse_binary_operator(end_cursors, self.read_multiply_devide_term)

    def read_multiply_devide_term(self, parent_end_cursors):
        end_cursors = [
                MathExpressionToken.MULTIPLY.value,
                MathExpressionToken.DIVIDE.value,
                ]
        end_cursors.extend(parent_end_cursors)
        return self.get_operand()

    def get_operand(self):
        if self.cursor == MathExpressionToken.SPAR.value:
            self.move_cursor_next()
            node = self.parse()
            assert(self.cursor == MathExpressionToken.EPAR.value)
            self.move_cursor_next() # shift away MathExpressionToken.EPAR
            return node
        num_str = ''
        valid_cursors = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ]
        while (self.cursor in valid_cursors):
            num_str += self.cursor
            self.move_cursor_next()
        if len(num_str) == 0:
            return None
        node = Node.constract_number_node(int(num_str))
        return node

