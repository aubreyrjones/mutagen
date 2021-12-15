#!/usr/bin/env python3

import sys
import os
import json
from subprocess import call
from time import sleep
from os import path
from textwrap import wrap
from PyPDF2 import PdfFileMerger
from scripts.parse_text import parse_moves, markup_moves, render_xml

# If you're on windows and didn't install LibreOffice in the default location, you'll need to edit that path
LIBREOFFICE = 'C:\Program Files\LibreOffice\program\soffice.com' if sys.platform == 'win32' else 'soffice'

# These are probably fine for anybody, but they're broken out here anyway.
BUILD_DIR = 'build'
OUT_DIR = 'playbook_output'
JSON_DIR = f'{OUT_DIR}/tracker_templates'

# Name of the meta section appended to playbooks.
META = 'common/meta'


#
# Build-related functions.
#

def staged_name(pbs):
    '''
    Get a section name as it appears in the build dir.
    '''
    return '/'.join([BUILD_DIR, split_section(pbs)])

def check_newer(pbs, extension):
    '''
    Return true if the output is newer than the input.
    '''
    sn = staged_name(pbs) + extension
    pbn = pbs + '.odt'
    if path.exists(sn):
        if path.getmtime(sn) > path.getmtime(pbn):
            return True
        return False
    return False # doesn't exist, so build

def make_pdf(pbs):
    '''
    Stage the PDF for a single section into ./build
    '''
    if check_newer(pbs, '.pdf'): return
    print("Building pdf:", pbs)
    call([LIBREOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', BUILD_DIR, pbs + ".odt"])
    sleep(0.25)

def make_txt(pbs):
    '''
    Stage the plain-text for a single section into ./build (this is for later parsing)
    '''
    if check_newer(pbs, '.txt'): return
    print("Building text:", pbs)
    call([LIBREOFFICE, '--headless', '--convert-to', 'txt:Text (encoded):UTF8', '--outdir', BUILD_DIR, pbs + ".odt"])
    sleep(0.25)

def stage_section(pbs):
    '''
    Get a section ready for inclusion in playbooks.
    '''
    make_pdf(pbs)
    make_txt(pbs)

def split_section(pbs):
    '''
    Get just the section name from a section path.
    '''
    return pbs.split('/')[-1]

# track sections that are already built so we don't rebuild them for
# each playbook that references them.
already_staged = set()

def make_playbook(pb_name, pb_list):
    '''
    Build a playbook from its constituent sections.
    '''

    print("Making", pb_name)
    if len(pb_list) < 1:
        print(f'ERROR! No playbook sections specified. Skipping {pb_name}.')
        return

    outfile = path.join(OUT_DIR, pb_name + ".pdf")
    outfile_json = path.join(JSON_DIR, pb_name + ".mutagen.json")
    outfile_xml = path.join(BUILD_DIR, pb_name + ".xml")
    
    # Convert from ODT to PDF (and text)
    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)
    
    # extract JSON move list for PC playbooks only.
    if '_teaser' not in pb_name and '_gm' not in pb_name:
        all_moves = markup_moves(sum([parse_moves(staged_name(pbs)) for pbs in pb_list], [])) # parse all the moves and put them in a single list together
        with open(outfile_xml, 'w', encoding='utf8') as xml_out:
            xml_out.write(render_xml(all_moves))
        with open(outfile_json, 'w', encoding='utf8') as json_out: 
            json_out.write(json.dumps({'items': all_moves, 'status': ''})) # and write it out as JSON

    # build PDF
    pdf_merger = PdfFileMerger()
    for pbs in pb_list:
        pdf_merger.append(staged_name(pbs) + '.pdf')
    
    # don't add the rules if it's a teaser "playbook".
    if '_teaser' not in pb_name:
        pdf_merger.append(staged_name(META) + '.pdf')

    pdf_merger.write(outfile)
    pdf_merger.close()


##
## BUILD SCRIPT BELOW HERE
##

# set up
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


# stage the meta section
stage_section(META)


# Here's the default playbooks def file
pb_def_file = 'playbooks.txt'

# ...or one from the command line.
if len(sys.argv) > 1:
    pb_def_file = sys.argv[1]


# dictionary of all playbook defs
playbooks = {}

# open the playbook definition and parse the lines
# skip line starting with `#` as comments.
# skip any line that doesn't have a `=` in it
with open(pb_def_file, encoding='utf8') as pb_defs:
    lines = pb_defs.readlines()

    for line in lines:
        try:
            stripped = line.strip()
            if stripped.startswith('#'): continue
            if '=' not in stripped: continue
            splits = stripped.split('=')
            pb_name = splits[0].strip()
            playbooks[pb_name] = [s.strip() for s in splits[1].split()]
        except:
            print("Error in playbook definition file", pb_def_file, "line:", line)
            exit(1)

for k, v in playbooks.items():
    make_playbook(k, v)