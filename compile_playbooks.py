#!/usr/bin/env python3
import sys
import os
import json
import io
from subprocess import call
from time import sleep
from os import path
from textwrap import wrap
import zipfile
from PyPDF2 import PdfFileMerger, PdfFileReader
from scripts.parse_text import parse_moves, markup_moves, render_xml, MARKUP_VERSION
import shutil
import time
import datetime
from scripts.make_odt import build_odt

# If you're on windows and didn't install LibreOffice in the default location, you'll need to edit that path
# just use forward slashes, not back-slashes.
LIBREOFFICE = 'C:/Program Files/LibreOffice/program/soffice.com' if sys.platform == 'win32' else 'soffice'

# These are probably fine for anybody, but they're configurable here anyway.
BUILD_DIR = 'build'
OUT_DIR = 'playbook_output'
JSON_DIR = f'{BUILD_DIR}/tracker_templates'

# Name of the meta section appended to non-teaser playbooks.
META = 'common/meta.odt'

OUT_EXT = 'pdf'
DOT_OUT_EXT = '.' + OUT_EXT

_build_time = datetime.datetime.now().strftime("%Y%m%d%H%M")


_time_rendering_pdfs = 0

EPB_README = '''I applaud your curiosity checking in here.
The other file in this `.zip` is an electronic playbook.
It's a JSON file full of special semantic XHTML markup.
At the time of this writing, these electronic playbooks are
compatible with `mutagenrpg.com/all`. If you got this out of a 
PDF, you don't need to extract anything; just upload the 
PDF to the website. If you don't have a PDF, you can upload
this `.zip` file or the `.json`.
'''

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
    sn = staged_name(input_filename, "pdf")

    if os.path.exists(sn):
        # delete it first so we can reliably check that it's been created.
        print(f"\t\tRemoving stale PDF:\t\t{sn}")
        os.remove(sn)
    
    print(f"\t\tRendering ", end='')
    render_start = time.time()

    call([LIBREOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', BUILD_DIR, input_filename])

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
    print(f"took {elapsed_time:.2f}s:\t\t-> {sn}")

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
    

def dump_json(parsed_moves, pb_name, pdf_url, homepage, game_title):
    return json.dumps({'items': markup_moves(parsed_moves), 
                       'status': '', 
                       'stuff': '', 
                       'markup_version': MARKUP_VERSION, 
                       'pdf': pdf_url,
                       'homepage': homepage,
                       'game_title': game_title,
                       'pb_name': pb_name}, indent=1)


def recover_json_from_zip(zipstream):
    try:
        instream = io.BytesIO(zipstream)
        with zipfile.ZipFile(instream, 'r') as zf:
            files = zf.namelist()
            for f in files:
                if f.lower().endswith('.json'):
                    return zf.read(f)
        return None
    except Exception as ex:
        print("\n", ex)
        return None
        

def recover_json_from_pdf(filename):
    try:
        with open(filename, 'rb') as instream:
            reader = PdfFileReader(instream)
            catalog = reader.trailer["/Root"]
            fileNames = catalog['/Names']['/EmbeddedFiles']['/Names']
            for f in fileNames:
                if isinstance(f, str):
                    name = f
                    dataIndex = fileNames.index(f) + 1
                    fDict = fileNames[dataIndex].getObject()
                    fData = fDict['/EF']['/F'].getData()
                    if name.lower().endswith('.zip'):
                        recovered = recover_json_from_zip(fData)
                        if recovered: return recovered
        return None
    except Exception as ex:
        print("\n", ex)
        return None    


def compress_json(json_file):
    outstream = io.BytesIO()
    with zipfile.ZipFile(outstream, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('readme.txt', EPB_README.encode('utf8'))
        zf.writestr(os.path.basename(json_file), open(json_file, 'rb').read())
    return outstream.getvalue()


def make_playbook(pb_name, human_name, pb_list, game_title, author_info, metadata):
    '''
    Build a playbook from its constituent sections.
    '''

    if len(pb_list) < 1:
        print(f'ERROR! No playbook sections specified. Skipping {pb_name}.')
        return

    gets_json = '_teaser' not in pb_name

    pdf_basename = pb_name + (DOT_OUT_EXT if gets_json else '.pdf')
    pdf_file = path.join(OUT_DIR, pdf_basename)
    json_file = path.join(JSON_DIR, pb_name + ".mutagen.json")

    # don't add the rules if it's a teaser "playbook".
    if '_teaser' not in pb_name:
        pb_list.append('common/meta')

    # resolve inputs to existing files.
    resolved_inputs = list(map(resolve_input, pb_list))

    print(f"Making `{human_name}`")
    print(f'\tInput sections:\t\t\t\t{" ".join(resolved_inputs)}')
    print(f'\tOutput PDF:\t\t\t\t-> {pdf_file}')
    print('\t*')

    for pbs in pb_list:
        if pbs in already_staged: continue
        already_staged.add(pbs)
        stage_section(pbs)
        

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
                build_odt(xml, odtName, human_name, game_title, author_info)
        else:
            odtName = span
        
        pdf_span_name = staged_name(odtName, "pdf")
        pdfs.append(pdf_span_name)
        if needs_rebuilt([odtName], pdf_span_name):
            print(f"\tIntermediate PDF from ODT:\t\t{odtName}")
            make_pdf(odtName)

    # write JSON
    if gets_json and needs_rebuilt(web_section_list, json_file):
        madeSomething = True
        with open(json_file, 'w', encoding='utf-8') as json_outfile:
            print(f'\tElectronic playbook from text:\t\t{" ".join(web_section_list)}')
            json_outfile.write(dump_json(for_web, human_name, metadata['PDFSERVER'] + pdf_basename, metadata['HOMEPAGE'], game_title))

    # build PDF
    final_deps = list(pdfs)
    if gets_json:
        final_deps.append(json_file)

    if needs_rebuilt(pdfs, pdf_file):
        madeSomething = True
        print(f'\tMerging final PDF:\t\t\t{" ".join(final_deps)}')
        pdf_merger = PdfFileMerger()
        for pdf in pdfs:
            pdf_merger.append(pdf)

        if gets_json:
            print(f'\tAttaching electronic playbook:\t\t{json_file}')
            # reach into the pdf writer to attach our compressed electronic playbook.
            pdf_merger.output.addAttachment(f'{pb_name}.zip', compress_json(json_file))

        pdf_merger.addMetadata({
            '/Author': author_info,
            '/Title': human_name,
            '/Subject': game_title,
            '/CreationDate': _build_time,
            '/Keywords': 'MutagenRPG.com'
        })

        pdf_merger.write(pdf_file)
        pdf_merger.close()

        if gets_json:
            with open(json_file, 'rb') as check_file:
                print(f'\tChecking PDF:', end='')
                if check_file.read() != recover_json_from_pdf(pdf_file):
                    raise RuntimeError("Recovered JSON doesn't match.")
                print(f'\t\t\t\tOK.')
    
    if not madeSomething: 
        print("\tUp to date. Nothing done.")
    else:
        print('\t*')
    print('*')


##
## BUILD SCRIPT BELOW HERE
##

_build_start = time.time()

# set up
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
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

game_title = 'UNTITLED GAME'
game_prefix = '00ug'
author_info = 'ANONYMOUS GAME DESIGNER'

metadata = {
    'PDFSERVER': '',
    'HOMEPAGE': 'https://www.mutagenrpg.com'
}

import re

S_TO_S_RE = re.compile(r'\s+')

def space_to_score(s):
    return S_TO_S_RE.sub('_', s.lower())

with open(pb_def_file, encoding='utf-8-sig') as pb_defs:
    lines = pb_defs.readlines()

    for line in lines:
##        try:
        stripped = line.strip()
        if stripped.startswith('#'): continue
        if '=' not in stripped: continue
        splits = stripped.split('=')
        human_name = splits[0].strip()
        pb_name = splits[1].strip()

        if human_name == 'GAME':
            game_title = pb_name
            continue
        if human_name == 'GAMESHORT':
            game_prefix = space_to_score(pb_name)
            continue
        if human_name == 'AUTHOR':
            author_info = pb_name
            continue
        if human_name in ('PDFSERVER', 'HOMEPAGE'):
            trailing = "" if human_name != 'PDFSERVER' or pb_name.endswith('/') else "/"
            metadata[human_name] = f'{pb_name}{trailing}'
            continue

        pb_list = [s.strip() for s in splits[2].split()]
        full_pb_name = f'{game_prefix}_{pb_name}'

        make_playbook(full_pb_name, human_name, pb_list, game_title, author_info, metadata)
        # except Exception as ex:
        #     print(ex)
        #     print("Error in playbook definition file", pb_def_file, "line:", line)
        #     exit(1)

tracker_templates = os.listdir(JSON_DIR)

tracker_filename = os.path.join(OUT_DIR, 'tracker_templates.zip')

print(f'Zipping tracker templates into {tracker_filename}. Send this to `mutagenrpg.com` if you want.')
with zipfile.ZipFile(tracker_filename, 'w', compression=zipfile.ZIP_DEFLATED) as tracker_zip:
    for tt in tracker_templates:
        tracker_zip.writestr(tt, open(os.path.join(JSON_DIR, tt), 'rb').read())

_build_finished = time.time()

total_elapsed = _build_finished - _build_start
script_time = total_elapsed - _time_rendering_pdfs

print(f'\nBuild took {total_elapsed:.2f}s. Spent {_time_rendering_pdfs:.2f}s waiting for LibreOffice. {script_time:.2f}s in this script.')

