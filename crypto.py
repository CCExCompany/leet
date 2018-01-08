#!/usr/bin/env python3

# Copyright by CCEx under GPLv3 license (c) 2017

from abc import ABC, abstractmethod, abstractproperty

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
    

class CaesarCipher(SymmetricAlgorithm):
    def __init__(self, key):
        self._key = key
    
    def encrypt(self, data: str):
        if self.key == None or not isinstance(self.key, int):
            raise ValueError("Invalid key")
            
        C = [chr(ord(data[i])+self.key) for i in range(len(data))]
        return ''.join(C)
    
    def decrypt(self, data: str) -> str:
        if self.key == None or not isinstance(self.key, int):
            raise ValueError("Invalid key")
            
        M = [chr(ord(data[i])-self.key) for i in range(len(data))]
        return ''.join(M)

def file_as_str(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()

def save_to_file(filename: str, data: str):
    with open(filename, "w") as f:
        f.write(data)
