#!/usr/bin/env python3

import sys
import os
import json
import argparse
from subprocess import call
from time import sleep
from os import path
from textwrap import wrap
from PyPDF2 import PdfFileMerger

LIBREOFFICE = '"C:\Program Files\LibreOffice\program\soffice.com"' if sys.platform == 'win32' else 'soffice'
BUILD_DIR = 'build'
OUT_DIR = 'playbook_output'
JSON_DIR = f'{OUT_DIR}/tracker_templates'


def staged_name(pbs):
    return '/'.join([BUILD_DIR, split_section(pbs)])

# return True if should build output.
def check_newer(pbs, extension):
    sn = staged_name(pbs) + extension
    pbn = pbs + '.odt'
    if path.exists(sn):
        if path.getmtime(sn) > path.getmtime(pbn):
            return True
        return False
    return False # doesn't exist, so build

def make_pdf(pbs):
    if check_newer(pbs, '.pdf'): return
    print("Building pdf:", pbs)
    call([LIBREOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', BUILD_DIR, pbs + ".odt"])
    sleep(0.25)

def make_txt(pbs):
    if check_newer(pbs, '.txt'): return
    print("Building text:", pbs)
    call([LIBREOFFICE, '--headless', '--convert-to', 'txt:Text (encoded):UTF8', '--outdir', BUILD_DIR, pbs + ".odt"])
    sleep(0.25)

def stage_section(pbs):
    make_pdf(pbs)
    make_txt(pbs)

def split_section(pbs):
    return pbs.split('/')[-1]


def parse_moves(pbs, do_wrap=False):
    with open(staged_name(pbs) + '.txt', encoding='utf8') as f:
        lines = f.readlines()
    
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

    if do_wrap:
        wrapped_moves = ['\n'.join(wrap(m)) for m in moves]
    else:
        wrapped_moves = moves
    
    return wrapped_moves


##
## BUILD STUFF BELOW HERE
##


# stage the meta section
META = 'common/meta'
stage_section(META)

already_staged = set()

def make_playbook(pb_name, pb_list):
    print("Making", pb_name)
    outfile = path.join(OUT_DIR, pb_name + ".pdf")
    outfile_json = path.join(JSON_DIR, pb_name + ".mutagen.json")
    
    # Convert from ODT to PDF (and text)
    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)
    
    # # extract JSON move list for PC playbooks only.
    if not 'gm_' in pb_name:
        all_moves = sum([parse_moves(pbs) for pbs in pb_list], [])
        with open(outfile_json, 'w', encoding='utf8') as json_out:
            json_out.write(json.dumps({'items': all_moves, 'status': ''}))

    # build PDF
    pdf_merger = PdfFileMerger()
    for pbs in pb_list:
        pdf_merger.append(staged_name(pbs) + '.pdf')
    
    pdf_merger.append(staged_name(META) + '.pdf')

    pdf_merger.write(outfile)
    pdf_merger.close()

os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

# Here's the default playbooks def file
pb_def_file = 'playbooks.txt'

# ...or one from the command line.
if len(sys.argv) > 1:
    pb_def_file = sys.argv[1]

# dictionary of all playbook defs
playbooks = {}

with open(pb_def_file, encoding='utf8') as pb_defs:
    lines = pb_defs.readlines()
    for line in lines:
        stripped = line.strip()
        if line.startswith('#'): continue
        if '=' not in stripped: continue
        splits = stripped.split('=')
        pb_name = splits[0].strip()
        playbooks[pb_name] = [s.strip() for s in splits[1].split()]

for k, v in playbooks.items():
    make_playbook(k, v)