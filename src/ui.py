#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

import npyscreen
import os
import json
from crypto import AESCipher
from crypto import file_as_str, save_to_file


class KeyDatabase(object):
    def __init__(self, filename=".keys.json"):
        self.filename = filename
        self.password = None
        self.keys = []
    
    def load_keys(self, password):
        self.password = password
        
        if not os.path.isfile(self.filename):
            self.keys = []
            return True # no keys saved before
        
        encrypted_keys = []
        with open('.keys.json', 'r') as f:
            encrypted_keys = list(json.loads(f.read()))
        encrypted_keys, check = encrypted_keys[:-1], encrypted_keys[-1]
        
        c = AESCipher(self.password)
        if c.decrypt(check) != 'CHECK':
            self.password = None
            return False # wrong password
        keys = [c.decrypt(key) for key in encrypted_keys]
        return True
    
    def save_keys(self):
        c = AESCipher(self.password)
        encrypted_keys = [c.encrypt(key) for key in self.keys] + [c.encrypt('CHECK')]
        with open('.keys.json', 'w') as f: # save key
            f.write(json.dumps(encrypted_keys))
    
    def update_record(self, record_id, key):
        assert len(key) > 0
        self.keys[record_id] = key
        r = self.save_keys()
        assert r

    def delete_record(self, record_id):
        self.keys.pop(record_id)  
        r = self.save_keys()
        assert r
        
    def list_all_records(self):
        return self.keys
    
    def get_record(self, record_id):
        return self.keys[record_id]


# --- Widget classes ---
class ExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.setNextForm(None)
        self.parent.parentApp.switchFormNow()


class EncryptButton(npyscreen.ButtonPress):
    def whenPressed(self):
        if self.parent.parentApp.key_password is None:
            self.parent.parentApp.switchForm("PASSWORDINPUT")
        else:
            self.parent.parentApp.switchForm("ENCRYPTFILE")


class DecryptButton(npyscreen.ButtonPress):
    def whenPressed(self):
        if self.parent.parentApp.key_password is None:
            self.parent.parentApp.switchForm("PASSWORDINPUT")
        else:
            self.parent.parentApp.switchForm("DECRYPTFILE")


class KeyManageButton(npyscreen.ButtonPress):
    def whenPressed(self):
        if self.parent.parentApp.key_password is None:
            self.parent.parentApp.switchForm("PASSWORDINPUT")
        else:
            self.parent.parentApp.switchForm("KEYMANAGE")
            

class PaswordInputButton(npyscreen.ButtonPress):
    def whenPressed(self):
        password = self.parent.password_input.value
        self.parent.parentApp.key_password = password
        
        r = self.parent.parentApp.database.load_keys(password)
        if not r:
            npyscreen.notify_confirm("Password entered incorrectly!")
            self.parent.parentApp.key_password = None
            
        self.parent.parentApp.switchFormPrevious()
        
class BackButton(npyscreen.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchFormPrevious()


# --- Forms ---
class MainForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleFixedText, name = "NOTE" , value="You must select a key prior to encryption/decryption")
        self.add(EncryptButton,   name = "Encrypt file")
        self.add(DecryptButton,   name = "Decrypt file")
        self.add(KeyManageButton, name = "Manage keys")
        self.add(ExitButton, name = "Exit", relx = 5, rely = 7)
        self.name = "Leet main menu"

class PasswordInputForm(npyscreen.Form):
    def create(self):
        self.password_input = self.add(npyscreen.TitleText, name = "Keystore password:", value="")
        self.add(PaswordInputButton, name = "Submit", relx = 10, rely = 6)
 
        
class EncryptForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleFixedText, name = "ENC FORM" , value="You must select a key prior to encryption/decryption")
        self.add(BackButton, name = "Back", relx = 10, rely = 6)
  
    
class DecryptForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleFixedText, name = "DEC FORM" , value="You must select a key prior to encryption/decryption")
        self.add(BackButton, name = "Back", relx = 10, rely = 6)
   
    
class KeyManageForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleFixedText, name = "OK", value = "")
    
    def do_smth(self):
        self.password = self.parentApp.key_password


class RecordList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(RecordList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record
        })

    def display_value(self, vl):
        return "%s, %s" % (vl[1], vl[2])
    
    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm('EDITKEY').value =act_on_this[0]
        self.parent.parentApp.switchForm('EDITKEY')

    def when_add_record(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITKEY').value = None
        self.parent.parentApp.switchForm('EDITKEY')
    
    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.database.delete_record(self.values[self.cursor_line][0])
        self.parent.update_list()


class RecordListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = RecordList
    def beforeEditing(self):
        self.update_list()
    
    def update_list(self):
        self.wMain.values = self.parentApp.database.list_all_records()
        self.wMain.display()
    
    
class EditRecord(npyscreen.ActionForm):
    def create(self):
        self.value = None
        self.key   = self.add(npyscreen.TitleText, name = "Last Name:",)
        
    def beforeEditing(self):
        if self.value:
            record = self.parentApp.database.get_record(self.value)
            self.name = "Record id : %s" % record[0]
            self.key_id          = record[0]
            self.key.value       = record[1]
        else:
            self.name = "New Record"
            self.key_id          = ''
            self.key.value       = ''
    
    def on_ok(self):
        if self.record_id: # We are editing an existing record
            self.parentApp.database.update_record(self.key_id, key=self.key.value)
        else: # We are adding a new record.
            self.parentApp.database.add_record(key=self.key.value)
        self.parentApp.switchFormPrevious()
    
    def on_cancel(self):
        self.parentApp.switchFormPrevious()
