# syntax_tree.py
import sys

class Node:
    def __init__(self, op, left=None, right=None, char=None):
        self.op = op
        self.char = char
        self.left = left
        self.right = right

class SyntaxTree:
    def __init__(self, regex, debug=False):
        self.regex = list(regex)
        self.current_token = None
        self.current_token = None
        self.tree = None
        self.debug = debug

    def get_token(self):
        if len(self.regex) == 0:
            self.current_token = 'end'
            return
        c = self.regex.pop(0)
        if c == '|':
            self.current_token = 'union'
        elif c == '(':
            self.current_token = 'lpar'
        elif c == ')':
            self.current_token = 'rpar'
        elif c == '*':
            self.current_token = 'star'
        elif c == '+':
            self.current_token = 'plus'
        else:
            self.current_token = 'char'
            self.token_char = c

    def make_node(self, op, left, right):
        node = Node(op, left, right)
        return node

    def make_atom(self, c):
        atom = Node('char', char=c)
        return atom

    def primary(self):
        if self.current_token == 'char':
            x = self.make_atom(self.token_char)
            self.get_token()
        elif self.current_token == 'lpar':
            self.get_token()
            x = self.parse_regex()
            if self.current_token != 'rpar':
                self.syntax_error("Close paren is expected.")
            self.get_token()
        else:
            self.syntax_error("Normal character or open paren is expected.")
        return x

    def factor(self):
        x = self.primary()
        if self.current_token == 'star':
            x = self.make_node('closure', x, None)
            self.get_token()
        elif self.current_token == 'plus':
            x = self.make_node('concat', x, self.make_node('closure', x, None))
            self.get_token()
        return x

    def term(self):
        if self.current_token in ['union', 'rpar', 'end']:
            x = self.make_node('empty')
        else:
            x = self.factor()
            while self.current_token not in ['union', 'rpar', 'end']:
                x = self.make_node('concat', x, self.factor())
        return x

    def parse_regex(self):
        x = self.term()
        while self.current_token == 'union':
            self.get_token()
            x = self.make_node('union', x, self.term())
        return x

    def make_tree(self):
        self.get_token()
        self.tree = self.parse_regex()
        if self.current_token != 'end':
            print("Extra character at end of pattern.")
            sys.exit(1)
        if self.debug:
            print("------ Syntax Tree ------")
            self.dump_tree(self.tree)
            print()
        return self.tree

    def dump_tree(self, tree):
        op = tree.op
        if op == 'char':
            print("'{}'".format(tree.char), end="")
        elif op == 'concat':
            print("(concat ", end="")
            self.dump_tree(tree.left)
            print(" ", end="")
            self.dump_tree(tree.right)
            print(")", end="")
        elif op == 'union':
            print("(or ", end="")
            self.dump_tree(tree.left)
            print(" ", end="")
            self.dump_tree(tree.right)
            print(")", end="")
        elif op == 'closure':
            print("(closure )", end="")
            self.dump_tree(tree.left)
            print(")", end="")
        elif op == 'empty':
            print("Empty")
        else:
            print("This cannot happen in ")
            sys.exit(1)
r = SyntaxTree("a(a|b)*a", debug=True)
r.make_tree()
