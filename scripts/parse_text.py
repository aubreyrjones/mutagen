import re

def parse_moves(pbs_filename, do_wrap=False):
    '''
    Parse all the moves out of a plaintext playbook.
    '''
    with open(pbs_filename + '.txt', encoding='utf8') as f:
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

# tag names:
# m-r : roll
# m-m : math
# m-s : symbol
# m-c : clickable symbol
# m-res : roll result entry
# m-li : bulletpoint/numbered list
# m-i: item
# m-ih : item header
# m-it : item title
# m-id : item description
# m-stitle : section title
# m-sdesc : section description
# m-in : input field
# m-il : input label
# m-inv : input value

ROLL_RE = re.compile(r'⊞⌊(.+?)⌋')
ROLL_REPLACE = r'<m-r>⊞⌊\1⌋</m-r>'

MATH_RE = re.compile(r'⌊(.+?)⌋')
MATH_REPLACE = r'<m-m>⌊\1⌋</m-m>'

RESULTS_RE = re.compile(r'\n\s*([🡕🡒🡖🡓]+)(.+?)($|\Z)', re.MULTILINE)
RESULTS_REPLACE = r'<m-res><m-s>\1</m-s>\2</m-res>'

LI_RE = re.compile(r'\n\s*([•\d])+(.+?)($|\Z)', re.MULTILINE)
LI_REPLACE = r'<m-li>\1\2</m-li>'

MOVE_RE = re.compile(r'^\s*(([○△▢●]\s*)*)(.+?)(\s*([○△▢●]\s*?)*)\s*►(.+)\Z', re.MULTILINE | re.DOTALL)
MOVE_REPLACE = r'<m-i><m-ih>\1<m-it>\3</m-it>\4 ►</m-ih><m-id>\6</m-id></m-i>'

SECTION_RE = re.compile(r'^\s*§\s*(.+?)$\s*(.*)', re.MULTILINE | re.DOTALL)

CLICKABLE_RE = re.compile(r'([○△▢])')
CLICKABLE_REPLACE = r'<m-c>\1</m-c>'

SYM_RE = re.compile(r'([●])')
SYM_REPLACE = r'<m-s>\1</m-s>'

# this is matching the unicode bracket write-in fields from the playbooks
# the ⎪ below is not a pipe; that's the middle of the bracket
INPUT_RE = re.compile(r'^\s*⎧[\s\n⎪]*?⎩\s*$', re.MULTILINE)
INPUT_REPLACE = r'<m-in><m-inv>🖉</m-inv></m-in>'

# this is for the strict 3-line variety with stuff appearing in the center line
LABELED_INPUT_RE = re.compile(r'^\s*⎧\s*\n(.*)\n\s*⎩\s*$', re.MULTILINE)
LABELED_INPUT_REPLACE = r'<m-in><m-il>\1</m-il><m-inv>🖉</m-inv></m-in>'

def section_replace(move_text, debug=False):
    m = SECTION_RE.match(move_text)
    if not m:
        return move_text
    desc = ''
    if m.group(2):
        desc = f'<m-sdesc>{m.group(2)}</m-sdesc>'
    rval = f'<m-stitle>§ {m.group(1)}</m-stitle>{desc}'
    if debug:
        print(rval)
        return move_text
    else:
        return rval

def markup_with_regex(regex, replacement, move_text, debug=False):
    rval = regex.sub(replacement, move_text)
    if debug:
        print(rval)
        return move_text
    else:
        return rval

def markup_move(move_text):
    # escape HTML tag markers.
    move_text = move_text.replace(">", "&gt;")
    move_text = move_text.replace("<", "&lt;")

    move_text = section_replace(move_text)

    filters = [
        (INPUT_RE, INPUT_REPLACE),
        (LABELED_INPUT_RE, LABELED_INPUT_REPLACE),
        (LI_RE, LI_REPLACE),
        (RESULTS_RE, RESULTS_REPLACE),
        (MOVE_RE, MOVE_REPLACE),
        (ROLL_RE, ROLL_REPLACE),
        (MATH_RE, MATH_REPLACE),
        (CLICKABLE_RE, CLICKABLE_REPLACE),
        (SYM_RE, SYM_REPLACE)]

    for regex, repl in filters:
        move_text = markup_with_regex(regex, repl, move_text)

    return move_text

def markup_moves(move_list):
    return [markup_move(m) for m in move_list]

def render_xml(markedup_move_list):
    header = '<?xml version="1.0" encoding="utf8"?>'
    stylesheet = '<?xml-stylesheet type="text/xsl" href="pb2odt.xsl"?>'
    content = [header, stylesheet]
    content.append('<playbook>')
    sectionLatched = False
    for m in markedup_move_list:
        if m.startswith('<m-stitle>'):
            if sectionLatched:
                content.append("</section>")
            content.append("<section>")
            content.append(m)
            sectionLatched = True
        else:
            content.append(m)
    if sectionLatched: # close the final section
        content.append("</section>")
    content.append('</playbook>')
    return "\n".join(content)