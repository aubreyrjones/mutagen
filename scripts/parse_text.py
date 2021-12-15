import re

def parse_moves(pbs_filename, keep_unheadered=False):
    '''
    Parse all the moves out of a plaintext playbook.
    '''
    if not pbs_filename.endswith('.txt'):
        pbs_filename += '.txt'
    with open(pbs_filename, encoding='utf8') as f:
        lines = f.readlines()
    
    moves = [""] if keep_unheadered else [] # []
    latch = keep_unheadered # False

    for l in lines:
        if '►' in l or '§' in l:
            moves.append(l)  # add a new move to the end of the list.
            latch = True
        elif latch:
            moves[-1] += l  # append to the existing last move.

    wrapped_moves = moves
    
    # Strip leading and trailing whitespace from the move descriptions.
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

RESULTS_RE = re.compile(r'$\s*([🡕🡒🡖🡓]+)(.+?)($|\Z)', re.MULTILINE)
RESULTS_REPLACE = r'\n<m-res><m-s>\1</m-s>\2</m-res>'

LI_RE = re.compile(r'$\s*([○△●]\s+)?([•\d])+(.+?)($|\Z)', re.MULTILINE)
LI_REPLACE = r'\n<m-li>\1\2\3</m-li>'

MOVE_RE = re.compile(r'^\s*(([○△▢●]\s*)*)(.+?)(\s*([○△▢●]\s*?)*)\s*►\s*(.+)\Z', re.MULTILINE | re.DOTALL)
MOVE_REPLACE = r'<m-i><m-ih>\1<m-it>\3</m-it>\4 ► </m-ih><m-id>\6</m-id></m-i>'

#SECTION_RE = re.compile(r'^\s*§\s*(.+?)$\s*(.*)', re.MULTILINE | re.DOTALL)
SECTION_RE = re.compile(r'^.*?§\s*(.+?)$\s*(.*)', re.MULTILINE | re.DOTALL)

CLICKABLE_RE = re.compile(r'([○△▢])')
CLICKABLE_REPLACE = r'<m-c>\1</m-c>'

SYM_RE = re.compile(r'([●])')
SYM_REPLACE = r'<m-s>\1</m-s>'

# this is matching the unicode bracket write-in fields from the playbooks
# the ⎪ below is not a pipe; that's the middle of the bracket
INPUT_RE = re.compile(r'^\s*(⎧[\s\n⎪]*?⎩)\s*$', re.MULTILINE)
INPUT_REPLACE = r'<m-in><m-inv>🖉</m-inv></m-in>'
XML_INPUT_REPLACE = r'<box-input>\1</box-input>'

# this is for the strict 3-line variety with stuff appearing in the center line
LABELED_INPUT_RE = re.compile(r'^\s*⎧\s*\n(.*)\n\s*⎩\s*$', re.MULTILINE)
LABELED_INPUT_REPLACE = r'<m-in><m-il>\1</m-il><m-inv>🖉</m-inv></m-in>'
XML_LABELED_INPUT_REPLACE = r'<labeled-input><m-il>\1</m-il></labeled-input>'

# this is a (partial) fixup for linebreaks -> paragraphs so that we can use
# standard HTML white-space rules. Why not just <p>? Because this one's mine. :)
LINE_RE = re.compile(r'(<m-id>|\n\n)(.+?)(</m-id>|$|\Z)', re.MULTILINE)
LINE_REPLACE = r'\1<m-p>\2</m-p>\3'


def section_replace(move_text, debug=False):
    m = SECTION_RE.match(move_text)
    if not m:
        return move_text
    desc = ''
    if m.group(2):
        desc = f'\n<m-sdesc>{m.group(2)}</m-sdesc>'
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
    move_text.replace('\ufeff', '')
    move_text.replace('\ubbef', '')
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
        (SYM_RE, SYM_REPLACE),
        (LINE_RE, LINE_REPLACE)]

    for regex, repl in filters:
        move_text = markup_with_regex(regex, repl, move_text)

    return move_text

def markup_moves(move_list):
    return [markup_move(m) for m in move_list]

# This is very similar to the MOVE_RE above, except this only captures the first paragraph.
# It also doesn't wrap the rest of the move in any semantic markup.
FIRST_ITEM_PARAGRAPH_RE = re.compile(r'^\s*(([○△▢●]\s*)*)(.+?)(\s*([○△▢●]\s*?)*)\s*►')
FIRST_ITEM_PARAGRAPH_REPLACE = r'<m-ih>\1\3\4 ► </m-ih>'

ALREADY_STITLE_RE = re.compile(r'^\s*<m-stitle')
ALREADY_SDESC_RE = re.compile(r'^\s*<m-sdesc')
ALREADY_LABELED_INPUT = re.compile(r'^\s*<labeled-input')
ALREADY_RESULT = re.compile(r'^\s*<m-res')
ITEM_HEADER_LINE_RE = re.compile(r'^\s*\.*?►')
BOX_INPUT_START_RE = re.compile(r'^\s*⎧')
BOX_INPUT_CONT_RE = re.compile(r'^\s*⎪')
BOX_INPUT_END_RE = re.compile(r'^\s*⎩')
RES_INPUT_LINE_RE = re.compile(r'^\s*[🡕🡒🡖🡓]')
LINE_ITEM_LINE_RE = re.compile(r'^\s*•')

LINE_TABLE = [
    (ALREADY_STITLE_RE, None),
    (ALREADY_SDESC_RE, None),
    (ALREADY_LABELED_INPUT, 'DO-NOTHING'),
    (ALREADY_RESULT, 'DO-NOTHING'),
    (BOX_INPUT_START_RE, 'box-start'),
    (BOX_INPUT_CONT_RE, 'box-cont'),
    (BOX_INPUT_END_RE, 'box-end'),
    (RES_INPUT_LINE_RE, 'roll-result'),
    (LINE_ITEM_LINE_RE, 'line-item')
]

LAST_TAG_STOP_RE = re.compile(r'^<([\w\-]+)>(.*?)</[\w\-]+>$')
LAST_TAG_STOP_REPLACE = r'<\1-stop>\2</\1-stop>'

def paragraph_type(line):
    for regex, _type in LINE_TABLE:
        if regex.match(line):
            return _type
    return 'm-p'

def no_stop(line):
    if paragraph_type(line) is None: return True
    return False

def markup_paragraphs(move_text):
    lines = move_text.replace("\n\n", "\n").split("\n")

    listTypeLatch = None
    for i, l in enumerate(lines):
        pType = paragraph_type(l)
        if pType not in (None, 'DO-NOTHING'):
            lines[i] = f'<{pType}>{l}</{pType}>'
        else:
            pass

    if not no_stop(lines[-1]):
        lines[-1] = LAST_TAG_STOP_RE.sub(LAST_TAG_STOP_REPLACE, lines[-1])

    return "\n".join(lines)

def markup_to_xml(move_text):
    move_text = section_replace(move_text)

    filters = [
        (FIRST_ITEM_PARAGRAPH_RE, FIRST_ITEM_PARAGRAPH_REPLACE),
        # (INPUT_RE, XML_INPUT_REPLACE),
        (LABELED_INPUT_RE, XML_LABELED_INPUT_REPLACE),
        # (LI_RE, LI_REPLACE),
        (RESULTS_RE, RESULTS_REPLACE),
        (ROLL_RE, ROLL_REPLACE),
        (MATH_RE, MATH_REPLACE),
        (CLICKABLE_RE, CLICKABLE_REPLACE),
        (SYM_RE, SYM_REPLACE)]
    
    for regex, repl in filters:
        move_text = markup_with_regex(regex, repl, move_text)
    
    move_text = markup_paragraphs(move_text)

    return move_text

def render_xml(move_list):
    header = '<?xml version="1.0" encoding="utf8"?>'
    content = [header]
    content.append('<playbook>')
    sectionLatched = False
    for m in move_list:
        if m.startswith('<m-stitle>'):
            if sectionLatched:
                content.append("</section>")
            content.append("<section>")
            content.append(markup_to_xml(m))
            sectionLatched = True
        else:
            content.append(markup_to_xml(m))
    if sectionLatched: # close the final section
        content.append("</section>")
    content.append('</playbook>')
    return "\n".join(content)
