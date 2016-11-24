# -*- coding: utf-8 -*-
import os
from wally.elastic.search import Search


def print_dashes():
    print("")
    for k in range(0, 100):
        print("-", end="")
    print("")
    print("")

print_dashes()
print_dashes()

print("Search for Japanese text: 何か調整が必要でしょうか?")
res = Search().search('何か調整が必要でしょうか?')
print_dashes()
#INFO 146167, 20229

print("Search for Japanese text changed: 調整必要?")
res = Search().search('調整必要')
print_dashes()

print("Search for text only in spam message:")
res = Search().search('upgraded to V.I.P access')
print_dashes()

print("Search for info number: 146167")
res = Search().search('146167')
print_dashes()