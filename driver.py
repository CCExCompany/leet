#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import curses
import logging
from ui import MainWindow

class LeetLogger:
    def __init__(self):
        self.logger = logging.getLogger('leet')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('.leet.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    
    def log(self, msg):
        self.logger.info(msg)

if __name__ == '__main__':
    logger = LeetLogger()
    curses.wrapper(MainWindow, logger)
