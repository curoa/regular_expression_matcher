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
from pprint import pprint as pp

import sys

class Node:

    def __init__(self, op, left=None, right=None, char=None):
        self.op = op
        self.char = char
        self.left = left
        self.right = right


class SyntaxTree:

    #TODO def syntax_error 

    TOKEN_CHAR = 'char'
    TOKEN_UNION = 'union'
    TOKEN_LPAR = 'lpar'
    TOKEN_RPAR = 'rpar'
    TOKEN_STAR = 'star'
    TOKEN_PLUS = 'plus'
    TOKEN_END = 'end'
    REGEX_TOKEN_DICT = {
            '|': TOKEN_UNION,
            '(': TOKEN_LPAR,
            ')': TOKEN_RPAR,
            '*': TOKEN_STAR,
            '+': TOKEN_PLUS,
            }

    def __init__(self, regex, debug=False):
        self.regex = list(regex)
        self.current_token = None
        self.token_char = None
        self.tree = None
        self.debug = debug

    def read_next_token(self): #TODO maybe bad name
        if len(self.regex) == 0:
            self.current_token = SyntaxTree.TOKEN_END
            return
        c = self.regex.pop(0)
        if c in SyntaxTree.REGEX_TOKEN_DICT.keys():
            self.current_token = SyntaxTree.REGEX_TOKEN_DICT[c]
        else:
            self.current_token = SyntaxTree.TOKEN_CHAR
            self.token_char = c

    def make_node(self, op, left, right): #TODO define op as constance
        node = Node(op, left, right)
        return node

    def make_atom(self, c):
        atom = Node(SyntaxTree.TOKEN_CHAR, char=c) #TODO check SyntaxTree.TOKEN_CHAR is correct?
        return atom

    def primary(self):
        if self.current_token == SyntaxTree.TOKEN_CHAR:
            x = self.make_atom(self.token_char)
            self.read_next_token()
        elif self.current_token == SyntaxTree.TOKEN_LPAR:
            self.read_next_token()
            x = self.parse_regex()
            if self.current_token != SyntaxTree.TOKEN_RPAR:
                self.syntax_error('Close parenthesis.')
            self.read_next_token()
        else:
            self.syntax_error("Normal character or open parenthesis is expected.")
        return x

    def factor(self):
        x = self.primary()
        if self.current_token == SyntaxTree.TOKEN_STAR: #TODO
            x = self.make_node('repeat', x, None)
            self.read_next_token()
        elif self.current_token == SyntaxTree.TOKEN_PLUS:
            x = self.make_node('concat', x, self.make_node('repeat', x, None))
            self.read_next_token()
        return x

    def term(self):
        target_token_list = [SyntaxTree.TOKEN_UNION, SyntaxTree.TOKEN_RPAR, SyntaxTree.TOKEN_END]
        if self.current_token in target_token_list:
            #TODO not executed but the case regex == ''
            x = self.make_node('empty')
        else:
            x = self.factor()
            while self.current_token not in target_token_list:
                x = self.make_node('concat', x, self.factor())
        return x

    def parse_regex(self):
        x = self.term()
        while self.current_token == SyntaxTree.TOKEN_UNION:
            self.read_next_token()
            x = self.make_node('union', x, self.term())
        return x

    def make_tree(self):
        self.read_next_token()
        self.tree = self.parse_regex()
        if self.current_token != SyntaxTree.TOKEN_END:
            print('Extra character at end of pattern.') #TODO rewrite as error
            sys.exit(1)
        if self.debug:
            print('---- Syntax Tree ----')
            self.dump_tree(self.tree)
            print()
        return self.tree

    def dump_tree(self, tree):
        op = tree.op
        if op == 'char':
            print("'{}'".format(tree.char), end='')
        elif op in  ['concat', 'union']:
            print('({} '.format(op), end='')
            self.dump_tree(tree.left)
            print(' ', end='')
            self.dump_tree(tree.right)
            print(')', end='')
        elif op == 'repeat':
            print('({} '.format(op), end='')
            self.dump_tree(tree.left)
            print(' ', end='')
            #TODO check why don't print right?
        elif op == 'empty':
            print('Empty')
        else:
            print('This can not happen in ') #TODO
            sys.exit(1)


