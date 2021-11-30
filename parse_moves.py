#!/usr/bin/env python3

import argparse
import json
from textwrap import wrap

ap = argparse.ArgumentParser(description="Parse moves from text into JSON.")
ap.add_argument('--wrap', default=False, const=True, action='store_const', help="Hard-wrap text")
ap.add_argument('playbook', type=str, help='Playbook input text.')
args = ap.parse_args()

infile = open(args.playbook, 'r', encoding="utf8")

lines = infile.readlines()

moves = []
latch = False

for l in lines:
    if '►' in l:
        moves.append(l)
        latch = True
    elif '§' in l:
        latch = False
        continue
    elif latch:
        moves[-1] += l

if args.wrap:
    wrapped_moves = ['\n'.join(wrap(m)) for m in moves]
else:
    wrapped_moves = moves

out_dict = {'items': wrapped_moves, 'status': ''}

print(json.dumps(out_dict))

