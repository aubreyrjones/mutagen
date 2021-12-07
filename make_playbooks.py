#!/usr/bin/env python3

import sys
import os
import json
from subprocess import call
from time import sleep
from os import path
from textwrap import wrap
from PyPDF2 import PdfFileMerger

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

def parse_moves(pbs, do_wrap=False):
    '''
    Parse all the moves out of a plaintext playbook.
    '''
    with open(staged_name(pbs) + '.txt', encoding='utf8') as f:
        lines = f.readlines()
    
    moves = []
    latch = False

    for l in lines:
        if '►' in l or '§' in l:
            moves.append(l)  # add a new move to the end of the list.
            latch = True
        elif latch:
            moves[-1] += l  # append to the existing last move.

    if do_wrap:
        wrapped_moves = ['\n'.join(wrap(m)) for m in moves]
    else:
        wrapped_moves = moves
    
    # Strip leading and trailing whitespace from the move descriptions.
    # We want whitespace in the PDF version, but it looks bad in the
    # web app.
    wrapped_moves = [s.strip() for s in wrapped_moves]

    return wrapped_moves

def replace_symbol(move_text, sym, enableClick=True):
    clz = 'ntfs'
    if enableClick:
        clz = 'tfs'
    return move_text.replace(sym, f'<span class="{clz}">{sym}</span>')

def split_off_ititle(move_text, title_end):
    pre_pips = ''
    title_start = 0
    if move_text[0] in '○△▢●':
        pre_pips = move_text[0]
        title_start = 1

    # '○△▢'
    for s in '○△▢':
        m = move_text.find(s, title_start, title_end)
        if m > 0:
            return pre_pips, move_text[title_start:m], move_text[m:title_end]
    return pre_pips, move_text[title_start:title_end], ""

def markup_move(move_text):
    title_end = move_text.find('►')
    if title_end > 0:
        pre_pips, title, pips = split_off_ititle(move_text, title_end)

        move_text = f'{pre_pips}<span class="ititle">{title}</span>{pips} ► <span class="item-desc">{move_text[title_end + 2:]}</span>'
    elif move_text.startswith('§'):
        line_end = move_text.find("\n")
        if line_end > 0:
            section_title = move_text[:line_end]
            section_desc = f'<span class="sec-desc">{move_text[line_end:]}</span>'
        else:
            section_title = move_text
            section_desc = ""
        move_text = f'<span class="stitle">{section_title}</span>{section_desc}'

    #move_text = move_text.replace("\n\n", "<p class=\"inl\">")
    #move_text = move_text.replace("\n", '<br/>')
    for s in '○△▢':
        move_text = replace_symbol(move_text, s)
    move_text = replace_symbol(move_text, '●', False)
    return move_text

def markup_moves(move_list):
    return [markup_move(m) for m in move_list]

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
    
    # Convert from ODT to PDF (and text)
    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)
    
    # extract JSON move list for PC playbooks only.
    if '_teaser' not in pb_name and '_gm' not in pb_name:
        all_moves = markup_moves(sum([parse_moves(pbs) for pbs in pb_list], [])) # parse all the moves and put them in a single list together
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