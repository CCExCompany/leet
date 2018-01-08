#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import curses
from crypto import CaesarCipher
from curses import panel
from curses.textpad import Textbox, rectangle
from file_browser import FileBrowser
from crypto import file_as_str, save_to_file
from functools import partial

class StringInput:
    def __init__(self, msg):
        self.msg = msg
        
    def get_line(self) -> str:
        curses.curs_set(1)
        #curses.idlok(1)
        
        inp = curses.newwin(8, 55, 0,0)
        inp.addstr(1,1, self.msg)
        sub = inp.subwin(3, 41, 2, 1)
        sub.border()
        
        # no need to handle enter as window is 1 line of size
        sub2 = sub.subwin(1, 40, 3, 2)
        tb = curses.textpad.Textbox(sub2)
        inp.refresh()
        tb.edit()
        
        text = tb.gather()
        curses.curs_set(0)
        return text.strip()[:-1].strip()
        
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
        self.keys = []
        self.selected_key = -1
        
        curses.curs_set(0)

        #si = StringInput()
        #logger.log("Line: "+si.get_line())
        #return
        
        submenu_items = [
            ('Create new key', self.add_key),
            ('List keys', self.list_keys),
            ('Remove existing key', curses.beep)
        ]
        submenu = Menu(submenu_items, self.screen)

        main_menu_items = [
            ('Encrypt file', self.encrypt_file_dlg),
            ('Decrypt file', self.decrypt_file_dlg),
            ('Manage keys', submenu.display)
        ]
        main_menu = Menu(main_menu_items, self.screen)
        main_menu.display()
    
    def encrypt_file_dlg(self):
        input_file = self.get_file()
        self.logger.log('Encrypting '+input_file)
        cs = CaesarCipher(self.keys[self.selected_key])
        M = file_as_str(input_file)
        C = cs.encrypt(M)
        self.logger.log('Plain text: '+M)
        self.logger.log('Ciphertext: '+C)
        ofname = input_file + '.encrypted.asc'
        save_to_file(ofname, C)
        self.logger.log('Saved ciphertext to ' + ofname) 
    
    def decrypt_file_dlg(self):
        input_file = self.get_file()
        self.logger.log('Decrypting '+input_file)
        cs = CaesarCipher(self.keys[self.selected_key])
        C = file_as_str(input_file)
        M = cs.decrypt(C)
        self.logger.log('Ciphertext: '+C)
        self.logger.log('Plain text: '+M)
        ofname = input_file + '.decrypted'
        save_to_file(ofname, M)
        self.logger.log('Saved plain text to ' + ofname)
        
    def get_file(self):
        fb = FileBrowser(self.screen)
        fb.display()
        self.logger.log('Result of file selection window: '+fb.result)
        return fb.result
    
    def add_key(self):
        key = StringInput("Enter the key as a single integer (1 <= key <= 32):").get_line()
        while True:
            try:
                key = int(key)
                if key < 1 or key > 32: raise ValueError
                break
            except ValueError:
                key = StringInput("Key is not valid. Try again:").get_line()
        
        self.keys.append(key)
        self.selected_key = len(self.keys) - 1
    
    def set_key(self, i):
        self.selected_key = i
        for ch in "Done":
            self.screen.echochar(ch)
        
    def list_keys(self):
        key_list = [(key, partial(self.set_key, i)) for i, key in enumerate(self.keys)]
        m = Menu(key_list, self.screen)
        m.display()
