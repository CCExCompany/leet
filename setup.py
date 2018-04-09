#!/usr/bin/env python

import sys, os
from cx_Freeze import setup, Executable

dir_ = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_, "src"))

setup(
    name='leet',
    version=1.0,
    author='CCEx',
    description='Encryption tool',
    license='GPLv3',
    executables = [Executable("driver.py")]
)
