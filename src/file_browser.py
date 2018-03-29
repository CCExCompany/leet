#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import curses
import time
import random
import cgitb, os, sys
from abc import ABC, abstractmethod, abstractproperty

class Entry(ABC):
    @abstractproperty
    def icon(self):
        pass
    
    @abstractmethod
    def expand(self):
        pass
    
    @abstractmethod
    def collapse(self):
        pass
        
    @abstractmethod
    def traverse(self):
        pass
        
    # factory method
    @staticmethod
    def get(name):
        if not os.path.isdir(name): 
            return File(name)
        else: 
            return Dir(name)
    
class File(Entry):
    def __init__(self, name):
        self.name = name
    
    @property
    def icon(self): 
        return '   '
    
    def render(self, depth, width):
        s = '%s%s %s' % (' ' * 4 * depth, self.icon, os.path.basename(self.name))
        s += ' ' * (width - len(s))
        return s
    
    def traverse(self): 
        yield self, 0
    
    def expand(self): 
        pass
    
    def collapse(self): 
        pass

class Dir(File):
    def __init__(self, name):
        File.__init__(self, name)
        try: 
            self.kidnames = sorted(os.listdir(name))
        except: 
            self.kidnames = None
        self.kids = None
        self.expanded = False
    
    @property
    def icon(self):
        if self.expanded: 
            return '[-]'
        elif self.kidnames is None: 
            return '[X]'
        elif self.children: 
            return '[+]'
        else: 
            return '[ ]'
    
    @property
    def children(self):
        if self.kidnames is None: return []
        if self.kids is None:
            self.kids = [Entry.get(os.path.join(self.name, kid))
                         for kid in self.kidnames]
        return self.kids
    
    def expand(self): 
        self.expanded = True
        
    def collapse(self): 
        self.expanded = False
        
    def traverse(self):
        yield self, 0
        if not self.expanded: 
            return
        for child in self.children:
            for kid, depth in child.traverse():
                yield kid, depth + 1

class FileBrowser:
    def __init__(self, stdscreen, logger):
        self.window = stdscreen.subwin(0,0)
        self.window.keypad(1)
        self.logger = logger
        cgitb.enable(format="text")
        self.ESC = 27
        self.result = ''
        self.start = '.'
    
    def display(self):
        mydir = Entry.get(self.start)
        mydir.expand()
        curidx = 3
        pending_action = None
        pending_save = False

        while True:
            self.window.clear()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            line = 0
            offset = max(0, curidx - curses.LINES + 3)
            for data, depth in mydir.traverse():
                if line == curidx:
                    self.window.attrset(curses.color_pair(1) | curses.A_BOLD)
                    if pending_action:
                        getattr(data, pending_action)()
                        pending_action = None
                    elif pending_save:
                        if os.path.isdir(data.name):
                            pending_save = False
                            if data.name != '.' or data.name != '..':
                                getattr(data, 'expand')()
                        else: # result is file, ok!
                            self.result = data.name
                            return
                else:
                    self.window.attrset(curses.color_pair(0))
                if 0 <= line - offset < curses.LINES - 1:
                    self.window.addstr(line - offset, 0,
                                  data.render(depth, curses.COLS))
                line += 1
            self.window.refresh()
            
            ch = self.window.getch()
            if ch == curses.KEY_UP: 
                curidx -= 1
            elif ch == curses.KEY_DOWN: 
                curidx += 1
            elif ch == curses.KEY_RIGHT: 
                pending_action = 'expand'
            elif ch == curses.KEY_LEFT: 
                pending_action = 'collapse'
            elif ch == self.ESC:
                os.system("clear") 
                return
            elif ch == ord('\n'):
                pending_save = True
            curidx %= line
