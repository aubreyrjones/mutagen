#!/usr/bin/env python3

import sys
import json
from subprocess import call
from time import sleep
from os import path
from textwrap import wrap
from PyPDF2 import PdfFileMerger

LIBREOFFICE = '"C:\Program Files\LibreOffice\program\soffice.com"' if sys.platform == 'win32' else 'soffice'
BUILD_DIR = 'build'
OUT_DIR = 'complete'


def staged_name(pbs):
    return '/'.join([BUILD_DIR, split_section(pbs)])

# return True if should build object.
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
    with open(staged_name(pbs) + '.txt') as f:
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
    outfile = path.join(OUT_DIR, pb_name + ".pdf")
    outfile_json = path.join(OUT_DIR, pb_name + ".mutagen.json")
    
    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)
    
    # extract JSON move list
    all_moves = sum([parse_moves(pbs) for pbs in pb_list], [])
    with open(outfile_json, 'w') as json_out:
        json.dump({'items': all_moves, 'status': ''}, json_out)

    # build PDF
    pdf_merger = PdfFileMerger()
    for pbs in pb_list:
        pdf_merger.append(staged_name(pbs) + '.pdf')
    
    pdf_merger.append(staged_name(META) + '.pdf')

    pdf_merger.write(outfile)
    pdf_merger.close()


PLAYBOOKS = {
    'wizard': ['common/common', 'pcs/wizard']
}


for k, v in PLAYBOOKS.items():
    make_playbook(k, v)