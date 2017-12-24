#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import os
import sys
import curses
import logging
from ui import MainWindow

class LeetLogger:
    def __init__(self):
        self.logger = logging.getLogger('leet')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('/tmp/leet.log')
        ch = logging.StreamHandler()
        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log(self, msg):
        self.logger.info(msg)

if __name__ == '__main__':
    logger = LeetLogger()
    curses.wrapper(MainWindow, logger)
#print(logger)
