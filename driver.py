#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import os
import sys
import curses
from ui import MainWindow

if __name__ == '__main__':
    curses.wrapper(MainWindow)
