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
import shutil
from scripts.make_odt import build_odt

# If you're on windows and didn't install LibreOffice in the default location, you'll need to edit that path
LIBREOFFICE = 'C:\Program Files\LibreOffice\program\soffice.com' if sys.platform == 'win32' else 'soffice'

# These are probably fine for anybody, but they're broken out here anyway.
BUILD_DIR = 'build'
OUT_DIR = 'playbook_output'
JSON_DIR = f'{OUT_DIR}/tracker_templates'

# Name of the meta section appended to playbooks.
META = 'common/meta.odt'


#
# Build-related functions.
#

def split_section(pbs):
    '''
    Get just the section name from a section path.
    '''
    return pbs.split('/')[-1]

def staged_name(pbs, ext):
    '''
    Get a section name as it appears in the build dir.
    '''
    basename = os.path.splitext(os.path.basename(pbs))[0]
    return '/'.join([BUILD_DIR, f'{basename}.{ext}'])

def needs_rebuilt(input_files, output_file):
    '''
    Return true if the output is newer than the input.
    '''
    for inf in input_files:
        if not path.exists(output_file): return True
        if path.getmtime(inf) > path.getmtime(output_file):
            return True
    return False # doesn't exist, so build

def make_pdf(input_filename):
    '''
    Builds a PDF from an ODT.
    '''
    print("\t\tBuilding pdf:", input_filename)
    call([LIBREOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', BUILD_DIR, input_filename])
    sleep(0.55) # we need this here so that we don't get ahead of LibreOffice.
    return staged_name(input_filename, 'pdf')

def copy_odt(input_filename):
    '''
    Copy an ODT into staging.
    '''
    shutil.copy(input_filename, staged_name(input_filename, 'odt'))


def resolve_input(section_name):
    if os.path.exists(section_name + '.txt'):
        return section_name + '.txt'
    elif os.path.exists(section_name + '.odt'):
        return section_name + '.odt'
    else:
        print("Input file not found: " + section_name)
        exit(1)

def is_odt(filename):
    return filename.endswith('.odt')

already_staged = set()

def stage_section(section_name):
    input_file = resolve_input(section_name)

    if is_odt(input_file):
        copy_odt(input_file)

def parse_and_markup_span(section_seq):
    parsed_moves = sum([parse_moves(s) for s in section_seq], [])
    
    web_markup = markup_moves(parsed_moves)
    xml_markup = render_xml(parsed_moves)
    return {'json': json.dumps({'items': web_markup, 'status': ''}),
            'xml': xml_markup}
    

def make_playbook(pb_name, human_name, pb_list):
    '''
    Build a playbook from its constituent sections.
    '''

    print("Making", pb_name)
    if len(pb_list) < 1:
        print(f'ERROR! No playbook sections specified. Skipping {pb_name}.')
        return

    # don't add the rules if it's a teaser "playbook".
    if '_teaser' not in pb_name:
        pb_list.append('common/meta')

    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)

    pdf_file = path.join(OUT_DIR, pb_name + ".pdf")
    json_file = path.join(JSON_DIR, pb_name + ".mutagen.json")
    
    resolved_inputs = list(map(resolve_input, pb_list))

    spans = []
    for sec in resolved_inputs:
        if is_odt(sec):
            spans.append(sec)
        else:
            if spans and isinstance(spans[-1], list):
                spans[-1].append(sec)
            else:
                spans.append([sec])

    pdfs = list()
    for i, span in enumerate(spans):
        odtName = None
        if isinstance(span, list):
            markups = parse_and_markup_span(span)
            odtName = staged_name(pb_name + str(i), 'odt')
            if needs_rebuilt(span, odtName):
                print(f'\tBuilding ODT from text: {" ".join(span)}')
                with open(staged_name(odtName, 'xml'), 'w') as xmlfile:
                    xmlfile.write(markups['xml'])
                build_odt(markups['xml'], odtName, human_name)
            with open(json_file, 'w') as json_outfile:
                json_outfile.write(markups['json'])
        else:
            odtName = span
        pdf_span_name = staged_name(odtName, 'pdf')
        pdfs.append(pdf_span_name)
        if needs_rebuilt([odtName], pdf_span_name):
            print(f"\tBuilding PDF from ODT: {odtName}")
            make_pdf(odtName)

    # build PDF
    if needs_rebuilt(pdfs, pdf_file):
        print(f'\tJoining PDFs: {" ".join(pdfs)}')
        pdf_merger = PdfFileMerger()
        for pdf in pdfs:
            pdf_merger.append(pdf)

        pdf_merger.write(pdf_file)
        pdf_merger.close()
    else:
        print("\tNothing to do.")


##
## BUILD SCRIPT BELOW HERE
##

# set up
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


# stage the meta section
#stage_section(META)


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
with open(pb_def_file, encoding='utf-8-sig') as pb_defs:
    lines = pb_defs.readlines()

    for line in lines:
        try:
            stripped = line.strip()
            if stripped.startswith('#'): continue
            if '=' not in stripped: continue
            splits = stripped.split('=')
            human_name = splits[0].strip()
            pb_name = splits[1].strip()
            playbooks[pb_name] = (human_name, [s.strip() for s in splits[2].split()])
        except Exception as ex:
            print(ex)
            print("Error in playbook definition file", pb_def_file, "line:", line)
            exit(1)

for k, v in playbooks.items():
    make_playbook(k, v[0], v[1])