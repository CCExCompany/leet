#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

#import ncurses
from crypto import CaesarCipher

class MainWindow(object):
    def __init__(self):
        pass
        
    def show(self):
        print('Showing ncurses window here!')
        print('Emulating a user who wants to encrypt a message!')
        
        message = "Phoenix"
        key = 2
        cipher = CaesarCipher(key)
        C = cipher.encrypt(message)
        M = cipher.decrypt(C)
        assert M == message
        
        print('Encrypted message:', C)
        print('Decrypted message:', M)
        
