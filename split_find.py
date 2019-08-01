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

import math

class SplitFind:

    def __init__(self, target_ids):
        self.count_splited = 0 # for calc value over max cell_id. essentially store how many times splited.
        self.arr = {} # value is cell id # arr is better, but I use dict for easy.
        for target in target_ids:
            self.arr[target] = 0

    def __repr__(self):
        return pf(vars(self))

    def split(self, target_ids):
        operand = 2 ** self.count_splited
        for target in target_ids:
            self.arr[target] += operand
        self.count_splited += 1

    def find(self, target_id, default=None):
        return self.arr.get(target_id, default)

    def count_cells(self):
        cell_ids = set()
        for cell_id in self.arr.values():
            cell_ids.add(cell_id)
        return len(cell_ids)

    def slim(self):
        """
        adjust self.count_splited
        """
        convert_dict = {}
        for cell_id in sorted(self.arr.values()): # sort to unrandomize
            if cell_id not in convert_dict:
                convert_dict[cell_id] = len(convert_dict)
        for arr_key, cell_id in self.arr.items():
            self.arr[arr_key] = convert_dict[cell_id]
        self.count_splited = math.ceil(math.log2(len(convert_dict)))


