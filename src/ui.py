#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import curses
import os
import json
from crypto import AESCipher
from curses import panel
from curses.textpad import Textbox, rectangle
from file_browser import FileBrowser
from crypto import file_as_str, save_to_file
from functools import partial

class WarningWindow:
    def __init__(self, msg):
        self.msg = msg
        
    def display(self):
        box = curses.newwin(8, 55, 0, 0)
        box.addstr(1,1, self.msg)
        box.addstr(3,1, "Press any key to continue")
        box.border()
        curses.doupdate()
        
        # Get a key and clear it
        box.getch()
        box.erase()
        os.system("clear")

class StringInput:
    def __init__(self, msg):
        self.msg = msg
        
    def get_line(self) -> str:
        curses.curs_set(1)
        
        inp = curses.newwin(8, 55, 0,0)
        inp.addstr(1,1, self.msg)
        sub = inp.subwin(3, 41, 2, 1)
        sub.border()
        
        # no need to handle enter as window is 1 line of size
        sub2 = sub.subwin(1, 40, 3, 2)
        tb = curses.textpad.Textbox(sub2, insert_mode=True)
        inp.refresh()
        tb.edit()
        
        text = tb.gather()
        curses.curs_set(0)
        curses.doupdate()
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
        self.keys = None #self._readkeys()
        self.password = None
        self.selected_key = -1
        
        curses.curs_set(0)

        main_menu_items = [
            ('Encrypt file', self.encrypt_file_dlg),
            ('Decrypt file', self.decrypt_file_dlg),
            ('Manage keys', self.manage_keys)
        ]
        main_menu = Menu(main_menu_items, self.screen)
        main_menu.display()
    
    def manage_keys(self):
        submenu_items = [
            ('Create new key', self.add_key),
            ('List keys', self.list_keys),
            ('Remove existing key', self.delete_key)
        ]
        submenu = Menu(submenu_items, self.screen)


        if self.keys != None:
            submenu.display()
            return
            
        self.keys = self._readkeys()
        if self.keys == None:
            w = WarningWindow('Wrong password!')
            w.display()
        elif self.keys == [] and self.password == None:
            pass1 = StringInput("Please set the password for keys protection").get_line()
            pass2 = StringInput("Please confirm your password by typping it again").get_line()
            if pass1 != pass2:
                w = WarningWindow('Different passwords entered, please retry')
                w.display()
            else:
                self.password = pass1
                submenu.display()
        else:
            submenu.display() # ok

    def _readkeys(self):
        if not os.path.isfile('.keys.json'):
            return [] # no keys saved
        
        encrypted_keys = []
        self.password = StringInput("Enter the password to unlock the keys").get_line()
        with open('.keys.json', 'r') as f:
            encrypted_keys = list(json.loads(f.read()))
        encrypted_keys, check = encrypted_keys[:-1], encrypted_keys[-1]
        
        c = AESCipher(self.password)
        if c.decrypt(check) != 'CHECK':
            self.password = None
            return None # wrong password
        keys = [c.decrypt(key) for key in encrypted_keys]
        return keys
        
    def encrypt_file_dlg(self):
        if self.keys == None or len(self.keys) == 0 or self.selected_key == -1:
            w = WarningWindow('Please select the key first')
            w.display()
            return
             
        input_file = self.get_file()
        if input_file in ['', ' ', '.', '..']:
            return
        if len(self.keys) == 0:
            warn = WarningWindow("You must add at least one key first!")
            warn.display()
            return
            
        self.logger.log('Encrypting '+input_file)
        cs = AESCipher(self.keys[self.selected_key])
        M = file_as_str(input_file)
        C = cs.encrypt(M)
        self.logger.log('Plain text: '+M)
        self.logger.log('Ciphertext: '+C)
        ofname = input_file + '.encrypted.asc'
        save_to_file(ofname, C)
        self.logger.log('Saved ciphertext to ' + ofname) 
    
    def decrypt_file_dlg(self):
        if self.keys == None or len(self.keys) == 0 or self.selected_key == -1:
            w = WarningWindow('Please select the key first')
            w.display()
            return
        
        input_file = self.get_file()
        if input_file in ['', ' ', '.', '..']:
            return
        if len(self.keys) == 0:
            warn = WarningWindow("You must add at least one key first!")
            warn.display()
            return
            
        self.logger.log('Decrypting '+input_file)
        cs = AESCipher(self.keys[self.selected_key])
        C = file_as_str(input_file)
        M = cs.decrypt(C)
        self.logger.log('Ciphertext: '+C)
        self.logger.log('Plain text: '+M)
        ofname = input_file + '.decrypted'
        save_to_file(ofname, M)
        self.logger.log('Saved plain text to ' + ofname)
        
    def get_file(self):
        fb = FileBrowser(self.screen, self.logger)
        fb.display()
        self.logger.log('Result of file selection window: '+fb.result)
        return fb.result
    
    def add_key(self):
        key = StringInput("Enter the key as a single line and press ENTER:").get_line()
        
        self.keys.append(key)
        self.selected_key = len(self.keys) - 1
        
        c = AESCipher(self.password)
        encrypted_keys = [c.encrypt(key) for key in self.keys] + [c.encrypt('CHECK')]
        with open('.keys.json', 'w') as f: # save key
            f.write(json.dumps(encrypted_keys))
    
    def set_key(self, i):
        self.selected_key = i
        warn = WarningWindow("Key selected")
        warn.display()
        
    def list_keys(self):
        key_list = [(key, partial(self.set_key, i)) for i, key in enumerate(self.keys)]
        m = Menu(key_list, self.screen)
        m.display()
    
    def _del_key(self, key):
        if key in self.keys:
            self.keys.remove(key)
            warn = WarningWindow("Key removed!")
            warn.display()
            
    def delete_key(self):
        m = key_list = [(key, partial(self._del_key, key)) for key in self.keys]
        m = Menu(key_list, self.screen)
        m.display()
        
        c = AESCipher(self.password)
        encrypted_keys = [c.encrypt(key) for key in self.keys] + [c.encrypt('CHECK')]
        with open('.keys.json', 'w') as f: # save keys
            f.write(json.dumps(encrypted_keys))
