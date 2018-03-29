#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

from abc import ABC, abstractmethod, abstractproperty
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


''' Symmetric algorithm interface (via abstract class) '''
class SymmetricAlgorithm(ABC):
    @property
    def key(self):
        return self._key
    
    @key.setter
    def key(self, value):
        self._key = value
    
    @abstractmethod
    def encrypt(self, data):
        pass
    
    @abstractmethod
    def decrypt(self, data):
        pass
    
    
''' Deprecated class for testing purposes '''
class CaesarCipher(SymmetricAlgorithm):
    def __init__(self, key):
        self._key = key
    
    def encrypt(self, data: str):
        if self.key == None or not isinstance(self.key, int):
            raise ValueError("Invalid key")
            
        C = [chr(ord(data[i]) + self.key) for i in range(len(data))]
        return ''.join(C)
    
    def decrypt(self, data: str) -> str:
        if self.key == None or not isinstance(self.key, int):
            raise ValueError("Invalid key")
            
        M = [chr(ord(data[i]) - self.key) for i in range(len(data))]
        return ''.join(M)

''' This class implements AES encryption using PyCrypto '''
''' NOTE: Using CBC mode in current implementation '''
class AESCipher(SymmetricAlgorithm):
    # Sets the key and block size
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()
        self.bs = 32
    
    # Pad data up to block size
    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]
    
    def encrypt(self, data: str):
        data = self.pad(data)
        iv = Random.new().read(AES.block_size)
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        C = iv + aes.encrypt(data)
        
        return base64.b64encode(C).decode('utf-8')
    
    def decrypt(self, data: str) -> str:
        data = base64.b64decode(data)
        iv = data[:AES.block_size]
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        M = aes.decrypt(data[AES.block_size:])
        
        return self.unpad(M).decode('utf-8')


''' Utility functions for file I/O '''
def file_as_str(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()

def save_to_file(filename: str, data: str):
    with open(filename, "w") as f:
        f.write(data)
