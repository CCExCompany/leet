#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import curses
from crypto import CaesarCipher
from curses import panel
from file_browser import FileBrowser

class Menu(object):
    def __init__(self, items, stdscreen):
        self.window = stdscreen.subwin(0,0)
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

        self.position = 0
        self.items = items
        self.items.append(('exit','exit'))

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()

        while True:
            self.window.refresh()
            curses.doupdate()
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                msg = '%d. %s' % (index, item[0])
                self.window.addstr(1 + index, 1, msg, mode)

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord('\n')]:
                if self.position == len(self.items)-1:
                    break
                else:
                    self.items[self.position][1]()

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

class MainWindow(object):
    def __init__(self, stdscreen, logger):
        self.screen = stdscreen
        self.logger = logger
        curses.curs_set(0)

        submenu_items = [
            ('Create new key', curses.beep),
            ('List keys', curses.beep),
            ('Remove existing key', curses.beep)
        ]
        submenu = Menu(submenu_items, self.screen)

        main_menu_items = [
            ('Encrypt file', self.encrypt_file_dlg),
            ('Decrypt file', curses.beep),
            ('Manage keys', submenu.display)
        ]
        main_menu = Menu(main_menu_items, self.screen)
        main_menu.display()
    
    def encrypt_file_dlg(self):
        input_file = self.get_file()
        self.logger.log('Encrypting '+input_file)
    
    def decrypt_file_dlg(self):
        input_file = self.get_file()
        self.logger.log('Decrypting '+input_file)
        
    def get_file(self):
        fb = FileBrowser(self.screen)
        fb.display()
        self.logger.log('Result of file selection window: '+fb.result)
        return fb.result
