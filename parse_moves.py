#!/usr/bin/env python3

import argparse
import sys

ap = argparse.ArgumentParser(description="Parse moves from text into JSON.")
ap.add_argument('playbook', type=str, help='Playbook input text.')
ap.add_argument('outfile', type=str, help='JSON output location.')
args = ap.parse_args()

infile = open(args.playbook, 'r', encoding="utf8")

lines = infile.readlines()

moves = []

for l in lines:
    if '►' in l:
        moves.append(l)
    elif len(moves) > 0:
        moves[-1] += l


print(moves[0])
