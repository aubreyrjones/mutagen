import re

MARKUP_VERSION = 7

LINE_HEADER_MATCH = re.compile(r'(►|-->)')
SEC_HEADER_MATCH = re.compile(r'^\s*(~~~)?(\$|§)')

COMMENT_LINE = re.compile(r'^\s*##')

def is_header(line):
    if LINE_HEADER_MATCH.search(line):
        return True
    if SEC_HEADER_MATCH.search(line):
        return True
    return False

def parse_moves(pbs_filename, keep_unheadered=False):
    '''
    Parse all the moves out of a plaintext playbook.
    '''
    if not pbs_filename.endswith('.txt'):
        pbs_filename += '.txt'
    with open(pbs_filename, encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    moves = [""] if keep_unheadered else [] # []
    latch = keep_unheadered # False

    for l in lines:
        if COMMENT_LINE.match(l): continue
        if is_header(l):
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

# m-i: item
# m-ih : item header
# m-it : item title
# m-id : item description

# m-stitle : section title
# m-sdesc : section description

# m-in : input field
# m-il : input label
# m-inv : input value
# m-res : roll result entry
# m-p: paragraph
# m-li : line item
# m-br: line-break paragraph


EASY_MOVE_DEF_RE = re.compile(r'-->')
EASY_MOVE_DEF_REPLACE = r'►'

ROLL_RE = re.compile(r'⊞⌊(.+?)⌋')
ROLL_REPLACE = r'<m-r><m-s>⊞</m-s>⌊\1⌋</m-r>'

MATH_RE = re.compile(r'⌊(.+?)⌋')
MATH_REPLACE = r'<m-m>⌊\1⌋</m-m>'

RESULTS_RE = re.compile(r'$\s*([🡕🡒🡖🡐]+)(.+?)($|\Z)', re.MULTILINE)
RESULTS_REPLACE = r'\n<m-res>\1 \2</m-res>'

EASY_LI_REPLACE_RE = re.compile(r'^\s*\*(.+)$', re.MULTILINE)
EASY_LI_REPLACE_REPLACE = r'  •\1'

LI_RE = re.compile(r'$\s*(\s+)?([•\d])+(.+?)($|\Z)', re.MULTILINE)
LI_REPLACE = r'\n<m-li>\1\2\3</m-li>'

MOVE_RE = re.compile(r'^\s*(([○△▢●]\s*)*)(.+?)(\s*([○△▢●]\s*?)*)\s*►\s*(.+)\Z', re.MULTILINE | re.DOTALL)
MOVE_REPLACE = r'<m-i><m-ih>\1<m-it>\3</m-it>\4 ► </m-ih><m-id>\n\6\n</m-id></m-i>'

EASY_SECTION_RE = re.compile(r'^\s*(~~~)?\$', re.MULTILINE)
EASY_SECTION_REPLACE = r'\1§'

SECTION_RE = re.compile(r'^\s*(~~~)?§\s*(.+?)$\s*(.*)', re.MULTILINE | re.DOTALL)

CLICKABLE_RE = re.compile(r'([○△▢])')
CLICKABLE_REPLACE = r'<m-c>\1</m-c>'

# pick up all the symbols that we've given special meaning to so that we can lex
# them for screen readers.
# ⌊⌋ in here makes screen readers hiccup, but also lexes the symbols... dunno what to do.
SYM_RE = re.compile(r'([●🗣🡕🡒🡖🡐►👎])')
SYM_REPLACE = r'<m-s>\1</m-s>'

MATH_SYM_RE = re.compile(r'([⌊⌋])')

BOLD_RE = re.compile(r'!!(.+?)!!')
BOLD_REPLACE = r'<b>\1</b>'

ITALICS_RE = re.compile(r'\/\/(.+?)\/\/')
ITALICS_REPLACE = r'<i>\1</i>'

UNDERLINE_RE = re.compile(r'__(.+?)__')
UNDERLINE_REPLACE = r'<em>\1</em>'

CALLOUT_RE = re.compile(r'\{\{(.+?)\}\}')
CALLOUT_REPLACE = r'⌞\1⌝'

EASY_MATH_RE = re.compile(r'_\[(.+?)\]_')
EASY_MATH_REPLACE = r'⌊\1⌋'

EASY_ROLL_RE = re.compile(r'!\+\[(.+?)\]')
EASY_ROLL_REPLACE = r'⊞⌊\1⌋'



# this is matching the unicode bracket write-in fields from the playbooks
# the ⎪ below is not a pipe; that's the middle of the bracket
INPUT_RE = re.compile(r'^\s*(\[\[[\s\n\|\|]*?\]\])\s*$', re.MULTILINE)
INPUT_REPLACE = r'<m-in><m-inv>🖉</m-inv></m-in>'
XML_INPUT_REPLACE = r'<box-input>\1</box-input>'

# this is for the strict 3-line variety with stuff appearing in the center line
LABELED_INPUT_RE = re.compile(r'^\s*\[\[\s*\n(.*)\n\s*\]\]\s*$', re.MULTILINE)
LABELED_INPUT_REPLACE = r'<m-in><m-il>\1</m-il><m-inv>🖉</m-inv></m-in>'
XML_LABELED_INPUT_REPLACE = r'\n<labeled-input><m-il>\1</m-il></labeled-input>'

# replace line continuations with nothing.
CONTINUE_LINE_RE = re.compile(r'\n\s*\\')
CONTINUE_LINE_REPLACE = r''

# replace newline runs with 1 newline
COALESCE_LINES_RE = re.compile(r'\n(\s*\n)+')
COALESCE_LINES_REPLACE = '\n'

# here's non-paragraph line break items. Starts with a single pipe.
LINE_BREAK_RE = re.compile(r'^\s*\|(?!\|)(.+?)$', re.MULTILINE)
LINE_BREAK_REPLACE = r'<m-br>\1</m-br>'

# these are line-start tags that are okay to wrap in paragraph tags.
PARAGRAPH_GREENLIST = ['m-c', 'm-r', 'm-m', 'm-s', 'u', 'i', 'b']
PARAGRAPH_GREENLIST_FRAGMENT = "|".join([f'<{p}>' for p in PARAGRAPH_GREENLIST])

# this is a (partial) fixup for linebreaks -> paragraphs so that we can use
# standard HTML white-space rules. Why not just <p>? Because this one's mine. :)
_line_re_string = r'^\s*(?!\[\[|\]\]|\|\|)(?=[^<]|' + PARAGRAPH_GREENLIST_FRAGMENT + r')(.+)$'
LINE_RE = re.compile(_line_re_string, re.MULTILINE)
LINE_REPLACE = r'<m-p>\1</m-p>'



def section_replace(move_text, debug=False, print_mode=False):
    m = SECTION_RE.match(move_text)
    if not m:
        return move_text, False
    desc = ''
    attr = ''
    if print_mode and m.group(1):
        attr = ' colbreak="true"'
    if m.group(3):
        if print_mode:
            desc = f'\n{m.group(3)}'
        else:
            desc = f'\n<m-sdesc>\n\n{m.group(3)}\n</m-sdesc>'
    rval = f'<m-stitle{attr}>§ {m.group(2)}</m-stitle>{desc}'
    if debug:
        print(rval)
        return move_text, True
    else:
        return rval, True

def markup_with_regex(regex, replacement, move_text, debug=False):
    rval = regex.sub(replacement, move_text)
    if debug:
        print(rval)
        return move_text
    else:
        return rval

def apply_regex_filters(filters: list, move_text, debug=False):
    for regex, repl in filters:
        move_text = markup_with_regex(regex, repl, move_text, debug)
    return move_text

EZ_REWRITE_FILTERS = [
    (EASY_SECTION_RE, EASY_SECTION_REPLACE),
    (COALESCE_LINES_RE, COALESCE_LINES_REPLACE),
    (CONTINUE_LINE_RE, CONTINUE_LINE_REPLACE),
    (EASY_MOVE_DEF_RE, EASY_MOVE_DEF_REPLACE),
    (EASY_LI_REPLACE_RE, EASY_LI_REPLACE_REPLACE),
    (CALLOUT_RE, CALLOUT_REPLACE),
    (EASY_MATH_RE, EASY_MATH_REPLACE),
    (EASY_ROLL_RE, EASY_ROLL_REPLACE)
]

def do_ez_rewrites(move_text):
    '''
    Do ascii digraph -> unicode glyph rewrites.

    These are not permitted to generate any XHTML markup, just replace ascii shortcuts with unicode stuff.
    '''
    return apply_regex_filters(EZ_REWRITE_FILTERS, move_text)


def preprocess_and_escape(move_text):
    # rewrite ASCII digraphs and shortcuts into unicode for later parser passes
    move_text = do_ez_rewrites(move_text)

    # escape trash and HTML tag markers.
    move_text.replace('\ufeff', '')
    move_text.replace('\ubbef', '')
    move_text = move_text.replace(">", "&gt;")
    move_text = move_text.replace("<", "&lt;")
    
    return move_text

def markup_move(move_text):
    '''
    Mark up a move for web. This is semantic markup, not formatting markup for print.
    '''
    
    move_text = preprocess_and_escape(move_text)

    move_text, isSection = section_replace(move_text)

    filters = [
        (INPUT_RE, INPUT_REPLACE),
        (LABELED_INPUT_RE, LABELED_INPUT_REPLACE),
        (EASY_LI_REPLACE_RE, EASY_LI_REPLACE_REPLACE),
        (LI_RE, LI_REPLACE),
        (RESULTS_RE, RESULTS_REPLACE),
        (MOVE_RE, MOVE_REPLACE),
        (ROLL_RE, ROLL_REPLACE),
        (MATH_RE, MATH_REPLACE),
        (CLICKABLE_RE, CLICKABLE_REPLACE),
        (SYM_RE, SYM_REPLACE),
        (MATH_SYM_RE, SYM_REPLACE),
        (BOLD_RE, BOLD_REPLACE),
        (ITALICS_RE, ITALICS_REPLACE),
        (UNDERLINE_RE, UNDERLINE_REPLACE),
        (LINE_BREAK_RE, LINE_BREAK_REPLACE),
        (LINE_RE, LINE_REPLACE)]

    move_text = apply_regex_filters(filters, move_text)

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
ALREADY_BREAK = re.compile(r'^\s*<m-br')
ITEM_HEADER_LINE_RE = re.compile(r'^.*?►')
BOX_INPUT_START_RE = re.compile(r'^\s*\[\[')
BOX_INPUT_CONT_RE = re.compile(r'^\s*\|\|')
BOX_INPUT_END_RE = re.compile(r'^\s*\]\]')
RES_INPUT_LINE_RE = re.compile(r'^\s*[🡕🡒🡖🡐]')

LINE_ITEM_LINE_RE = re.compile(r'^\s*(•|\d+\.)')

LINE_TABLE = [
    (ALREADY_STITLE_RE, None),
    (ALREADY_SDESC_RE, None),
    (ALREADY_LABELED_INPUT, 'DO-NOTHING'),
    (ALREADY_RESULT, 'DO-NOTHING'),
    (ALREADY_BREAK, 'DO-NOTHING'),
    (ITEM_HEADER_LINE_RE, 'item-start'),
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

def markup_paragraphs(move_text, skip_stop):
    lines = move_text.replace("\n\n", "\n").split("\n")

    listTypeLatch = None
    for i, l in enumerate(lines):
        pType = paragraph_type(l)
        if pType not in (None, 'DO-NOTHING'):
            lines[i] = f'<{pType}>{l}</{pType}>'
        else:
            # don't fix up
            pass

    if not (skip_stop or no_stop(lines[-1])):
        lines[-1] = LAST_TAG_STOP_RE.sub(LAST_TAG_STOP_REPLACE, lines[-1])

    return "\n".join(lines)

def markup_to_xml(move_text):
    '''
    Markup for print. This is formatting markup, not semantic markup for data processing.
    '''
    move_text =  preprocess_and_escape(move_text)

    move_text, isSection = section_replace(move_text, print_mode=True)

    filters = [
        (FIRST_ITEM_PARAGRAPH_RE, FIRST_ITEM_PARAGRAPH_REPLACE),
        (LABELED_INPUT_RE, XML_LABELED_INPUT_REPLACE),
        (RESULTS_RE, RESULTS_REPLACE),
        (LINE_BREAK_RE, LINE_BREAK_REPLACE),
        (ROLL_RE, ROLL_REPLACE),
        (MATH_RE, MATH_REPLACE),
        (CLICKABLE_RE, CLICKABLE_REPLACE),
        (SYM_RE, SYM_REPLACE),
        (BOLD_RE, BOLD_REPLACE),
        (ITALICS_RE, ITALICS_REPLACE),
        (UNDERLINE_RE, UNDERLINE_REPLACE)]
    
    move_text = apply_regex_filters(filters, move_text)
    
    move_text = markup_paragraphs(move_text, isSection)

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
