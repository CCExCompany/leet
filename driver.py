#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import os
import sys

if getattr(sys, 'frozen', False):
    # frozen
    dir_ = os.path.dirname(sys.executable)
else:
    # unfrozen
    dir_ = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(dir_, "src"))

import npyscreen
from ui import *


# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application
class LeetApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.key_password = None
        self.database = KeyDatabase(filename=".keys.json")
        
        self.addForm("MAIN", MainForm)
        self.addForm("ENCRYPTFILE", EncryptForm)
        self.addForm("DECRYPTFILE", DecryptForm)
        self.addForm("KEYMANAGE", RecordListDisplay)
        self.addForm("EDITKEY", EditRecord)
        self.addForm("PASSWORDINPUT", PasswordInputForm)
        
        #self.setNextFormPrevious()


if __name__ == '__main__':
    LA = LeetApp()
    LA.run()
