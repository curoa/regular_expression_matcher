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

from arithmetic_syntax_tree import Parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This is hogehoge')
    args = parser.parse_args()

    formula = '12+4-3*7*8+2'
    formula = '1*(2+3)/4'

    pp('formula') # debug
    pp(formula) # debug
    node = Parser.run(formula)
    pp('node') # debug
    print(node) # debug
    pp(node.pf_as_tree()) # debug


    print('\33[32m' + 'end' + '\033[0m')
