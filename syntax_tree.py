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

from enum import Enum


class NodeOperation(Enum):

    CHAR = 'char'
    CONCAT = 'concat'
    REPEAT = 'repeat'
    UNION = 'union'


class Node():

    def __init__(self, nop, prev=None, _next=None, char=None):
        #FIXME consider list instead of prev, next
        assert(type(nop) is NodeOperation)
        assert(prev is None or isinstance(prev, Node))
        assert(_next is None or isinstance(_next, Node))
        self.op = nop
        self.prev = prev
        self.next = _next
        self.char = char # not RegularExpressionMetaToken

    @staticmethod
    def constract_openrad(char):
        return Node(NodeOperation.CHAR, None, None, char)

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
        if self.op == NodeOperation.CHAR:
            line = 'char: {}'.format(self.char)
        else:
            line = 'op: {}'.format(self.op)
        out = '-' * depth + line
        return out


class RegularExpressionMetaToken(Enum):

    UNION = '|'
    SPAR = '(' # start of parenthesis
    EPAR = ')' # end of parenthesis
    STAR = '*' # 0 or more
    PLUS = '+' # 1 or more #TODO unsupported

class Parser():

    def __init__(self):
        self.remain = None # store remain regex
        self.cursor = None # store reading char

    @staticmethod
    def run(regex):
        parser = Parser()
        node = parser.make_tree(regex)
        return node

    def make_tree(self, regex):
        """
        return Node
        """
        self.remain = list(regex)
        self.move_cursor_next() # set cursor start of regex
        return self.parse()

    def move_cursor_next(self):
        if len(self.remain) == 0:
            self.cursor = None
            return
        self.cursor = self.remain[0]
        self.remain.pop(0)

    def parse(self):
        end_cursors = [None, RegularExpressionMetaToken.EPAR.value]
        return self.parse_union(end_cursors)

    def parse_union(self, end_cursors):
        node = self.read_union_term(end_cursors)
        while not (self.cursor in end_cursors):
            op = NodeOperation.UNION
            self.move_cursor_next()
            node_next = self.read_union_term(end_cursors)
            node = Node(op, node, node_next)
        return node


    def read_union_term(self, parent_end_cursors):
        end_cursors = [
                RegularExpressionMetaToken.UNION.value,
                ]
        end_cursors.extend(parent_end_cursors)
        return self.parse_concat(end_cursors)

    def parse_concat(self, end_cursors):
        node = self.read_concat_term(end_cursors)
        while not (self.cursor in end_cursors):
            op = NodeOperation.CONCAT
            #self.move_cursor_next()
            node_next = self.read_concat_term(end_cursors)
            node = Node(op, node, node_next)
        return node

    def read_concat_term(self, parent_end_cursors):
        end_cursors = parent_end_cursors
        return self.parse_repeat(end_cursors)

    def parse_repeat(self, end_cursors):
        #TODO this is star only
        node = self.get_operand()
        if self.cursor == RegularExpressionMetaToken.STAR.value:
            op = NodeOperation.REPEAT
            self.move_cursor_next()
            node = Node(op, node, None)
        return node

    def get_operand(self):
        if self.cursor == RegularExpressionMetaToken.SPAR.value:
            return self.parse_parenthesis()
        node = Node.constract_openrad(self.cursor)
        self.move_cursor_next()
        return node

    def parse_parenthesis(self):
        self.move_cursor_next()
        node = self.parse()
        assert(self.cursor == RegularExpressionMetaToken.EPAR.value)
        self.move_cursor_next() # shift away RegularExpressionMetaToken.EPAR
        return node

