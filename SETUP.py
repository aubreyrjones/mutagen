#!/usr/bin/env python3

from subprocess import check_call

try:
    check_call(['pip3', 'install', 'pypdf2', 'lxml', 'odfpy'])
except:
    print("Could not install requirements. Is Python 3 installed correctly?")
    input("Hit enter to quit.")
else:
    print("Requirements successfully installed.")
    input("Hit enter to quit.")
