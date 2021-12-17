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
import time
from scripts.make_odt import build_odt

# If you're on windows and didn't install LibreOffice in the default location, you'll need to edit that path
# just use forward slashes, not back-slashes.
LIBREOFFICE = 'C:/Program Files/LibreOffice/program/soffice.com' if sys.platform == 'win32' else 'soffice'

# These are probably fine for anybody, but they're configurable here anyway.
BUILD_DIR = 'build'
OUT_DIR = 'playbook_output'
JSON_DIR = f'{OUT_DIR}/tracker_templates'

# Name of the meta section appended to non-teaser playbooks.
META = 'common/meta.odt'


_time_rendering_pdfs = 0

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
    Get a section name as it appears in the build dir with that extension.
    '''
    basename = os.path.splitext(os.path.basename(pbs))[0]
    return '/'.join([BUILD_DIR, f'{basename}.{ext}'])

def needs_rebuilt(input_files: list, output_file):
    '''
    Return true if the output_file doesn't exist or is older than the input_files.
    '''
    for inf in input_files:
        if not path.exists(output_file): return True
        if path.getmtime(inf) > path.getmtime(output_file):
            return True
    return False


def make_pdf(input_filename):
    '''
    Builds a PDF from an ODT.
    '''
    print(f"\t\tRendering ", end='')
    render_start = time.time()

    call([LIBREOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', BUILD_DIR, input_filename])
    
    sn = staged_name(input_filename, 'pdf')

    while not os.path.exists(sn):
        sleep(0.1)
        # we need this loop here so that we don't get ahead of LibreOffice. 
        # If you have LibreOffice already open, the command-line program can 
        # quit before the file is written.
        # The timeout is so that we don't wait forever if there's a real problem.
        if (time.time() - render_start) > 30:
            print("\n\nLibreOffice took longer than 30 seconds to render a PDF. This is weird. I'm bailing out.\n\n")
            exit(10)
    
    render_end = time.time()
    elapsed_time = render_end - render_start
    global _time_rendering_pdfs
    _time_rendering_pdfs += elapsed_time
    print(f"took {elapsed_time:.2f}s.")

    return sn

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

def parse_span(section_seq):
    return sum([parse_moves(s) for s in section_seq], [])
    

def dump_json(parsed_moves, pb_name):
    return json.dumps({'items': markup_moves(parsed_moves), 
                       'status': '', 
                       'stuff': '', 
                       'markup_version': 1, 
                       'pb_name': pb_name})


def make_playbook(pb_name, human_name, pb_list):
    '''
    Build a playbook from its constituent sections.
    '''


    pdf_file = path.join(OUT_DIR, pb_name + ".pdf")
    json_file = path.join(JSON_DIR, pb_name + ".mutagen.json")

    print(f"*\nMaking `{human_name}`")
    print(f'\tFinal PDF file:\t\t\t\t{pdf_file}')
    print(f'\tFinal JSON file:\t\t\t{json_file}')
    print('\t*')

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
    
    resolved_inputs = list(map(resolve_input, pb_list))

    madeSomething = False

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
    web_section_list = list()
    for_web = list()

    for i, span in enumerate(spans):
        odtName = None
        if isinstance(span, list):
            parsed_moves = parse_span(span)
            web_section_list += span
            for_web += parsed_moves

            odtName = staged_name(pb_name + str(i), 'odt')

            # write XML and ODT
            if needs_rebuilt(span, odtName):
                madeSomething = True
                print(f'\tIntermediate ODT from text:\t\t{" ".join(span)}')
                xml = render_xml(parsed_moves)
                with open(staged_name(odtName, 'xml'), 'w', encoding='utf-8') as xmlfile:
                    # this is actually just written out for debug purposes. It's basically the last
                    # stage before everything disappears into an XML/OpenOffice black hole.
                    # the ODF library can give lots of errors, so we write the pre-XSLT XML first.
                    xmlfile.write(xml)
                build_odt(xml, odtName, human_name)
        else:
            odtName = span
        
        pdf_span_name = staged_name(odtName, 'pdf')
        pdfs.append(pdf_span_name)
        if needs_rebuilt([odtName], pdf_span_name):
            print(f"\tIntermediate PDF from ODT:\t\t{odtName}")
            make_pdf(odtName)

    # write JSON
    if '_gm' not in pb_name and needs_rebuilt(web_section_list, json_file):
        madeSomething = True
        with open(json_file, 'w', encoding='utf-8') as json_outfile:
            print(f'\tElectronic playbook from text:\t\t{" ".join(web_section_list)}')
            json_outfile.write(dump_json(for_web, human_name))

    # build PDF
    if needs_rebuilt(pdfs, pdf_file):
        madeSomething = True
        print(f'\tMerging final PDF:\t\t\t{" ".join(pdfs)}')
        pdf_merger = PdfFileMerger()
        for pdf in pdfs:
            pdf_merger.append(pdf)

        pdf_merger.write(pdf_file)
        pdf_merger.close()
    
    if not madeSomething: print("\tUp to date. Nothing done.")


##
## BUILD SCRIPT BELOW HERE
##

_build_start = time.time()

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

_build_finished = time.time()

total_elapsed = _build_finished - _build_start

print(f'\n\nBuild took {total_elapsed:.2f}s. Spent {_time_rendering_pdfs:.2f}s waiting for LibreOffice. {total_elapsed - _time_rendering_pdfs:.2f}s in this script.')

