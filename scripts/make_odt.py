from odf.opendocument import OpenDocumentText
from odf.style import PageLayout, MasterPage, Header, Footer, PageLayoutProperties, Style, TextProperties, ParagraphProperties, Columns, Column, DefaultStyle, ColumnSep
from odf.text import P, PageNumber, A, Span
import lxml.etree as ET
import zipfile

import os.path
import sys
import os

xslt_file = os.path.join(os.path.dirname(__file__), "pb2odt.xsl")

def dom_transform(xml_file):
    dom = ET.fromstring(bytes(xml_file, encoding='utf8'))
    xslt = ET.parse(xslt_file)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)

    domString = ET.tostring(newdom, pretty_print=True, encoding='unicode').replace("---", ":")
    return domString

def make_paragraph_style(textdoc, stylename, pAttr=None, tAttr=None):
    s = Style(name=stylename, family="paragraph")
    if pAttr:
        s.addElement(ParagraphProperties(attributes=pAttr))
    if tAttr:
        s.addElement(TextProperties(attributes=tAttr))
    
    textdoc.styles.addElement(s)

def make_with_stop(textdoc, stylename, pAttr=None, tAttr=None):
    make_paragraph_style(textdoc, stylename, pAttr, tAttr)
    if not pAttr:
        pAttr = {}
    pAttr.update({'keepwithnext': 'auto'})
    make_paragraph_style(textdoc, stylename + '_STOP', pAttr, tAttr)

def make_span_style(textdoc, stylename, tAttr):
    s = Style(name=stylename, family="text")
    s.addElement(TextProperties(attributes=tAttr))
    textdoc.styles.addElement(s)


def build_skeleton_odt(filename, title_text=''):
    textdoc = OpenDocumentText()
    pl = PageLayout(name="pagelayout")
    plp = PageLayoutProperties(pagewidth='11in', pageheight='8.5in', printorientation="landscape",
                                    margintop='0.58in', marginleft='0.25in', marginbottom='0.25in',
                                    marginright='0.25in', numformat='1', writingmode='lr-tb')
    
    
    columnsStyle = Columns(columncount=3, columngap="0.2in")
    columnsStyle.addElement(ColumnSep(attributes={'style':'solid', 'width':'0.25pt'}))
    plp.addElement(columnsStyle)
    
    pl.addElement(plp)
    textdoc.automaticstyles.addElement(pl)

    mp = MasterPage(name="Standard", pagelayoutname=pl)
    textdoc.masterstyles.addElement(mp)

    MAIN_FONT_SIZE = '9pt'
    HEADING_FONT_SIZE = '14pt'

    defaultPStyle = DefaultStyle(family="paragraph")
    defaultPStyle.addElement(TextProperties(attributes={'fontsize': MAIN_FONT_SIZE, 'fontfamily': "MutagenSans"}))
    defaultPStyle.addElement(ParagraphProperties(attributes={'margintop': '2mm', 'keeptogether': 'always', 'keepwithnext': 'auto', 'registertrue': 'true'}))
    textdoc.styles.addElement(defaultPStyle)

    make_paragraph_style(textdoc, "SECTION_TITLE_BREAK", pAttr={'keepwithnext': 'always', 'breakbefore': 'column'}, tAttr={'fontsize': HEADING_FONT_SIZE, 'fontweight': 'bold'})
    make_paragraph_style(textdoc, "SECTION_TITLE", pAttr={'keepwithnext': 'always'}, tAttr={'fontsize': HEADING_FONT_SIZE, 'fontweight': 'bold'})
    
    make_with_stop(textdoc, "ITEM_DESC", pAttr={'keepwithnext': 'always'})
    make_with_stop(textdoc, "ITEM_HEADING", pAttr={'keepwithnext': 'always', 'margintop': '3mm'})

    make_span_style(textdoc, "ITEM_TITLE", {'fontsize': MAIN_FONT_SIZE, 'fontweight': 'bold'})
    make_span_style(textdoc, "BOLD_SYMBOL", {'fontsize': MAIN_FONT_SIZE, 'fontweight': 'bold'})
    make_span_style(textdoc, "GENERIC_BOLD", {'fontsize': MAIN_FONT_SIZE, 'fontweight': 'bold'})
    make_span_style(textdoc, "GENERIC_ITALIC", {'fontsize': MAIN_FONT_SIZE, 'fontstyle': 'italic'})
    make_span_style(textdoc, "GENERIC_UNDERLINE", {'fontsize': MAIN_FONT_SIZE, 'textunderlinetype': 'single'})

    make_paragraph_style(textdoc, "FIRST_INPUT_LINE", pAttr={'margintop': '1mm', 'keepwithnext': 'always'})
    make_paragraph_style(textdoc, "INPUT_LINE", pAttr={'margintop': '0mm', 'keepwithnext': 'always'})
    make_with_stop(textdoc, "LAST_INPUT_LINE", pAttr={'margintop': '0mm', 'keepwithnext': 'always'})

    make_with_stop(textdoc, "LINE_ITEM", pAttr={'margintop': '1mm', 'marginleft': '2mm', 'keepwithnext': 'always'})
    make_with_stop(textdoc, "RESULT_ITEM", pAttr={'margintop': '1mm', 'keepwithnext': 'always'})

    make_paragraph_style(textdoc, "FOOTER_PAGE_NUMBER", pAttr={'textalign': 'right'}, tAttr={'fontsize': '8pt', 'fontweight': 'bold'})

    f = Footer()
    fp = P(stylename='FOOTER_PAGE_NUMBER')
    fp.addElement(Span(text=f'{title_text} ⌬ '))
    fp.addElement(PageNumber(text="1"))
    f.addElement(fp)
    mp.addElement(f)

    replace_target = P(text="replace_me")
    textdoc.text.addElement(replace_target)
    textdoc.save(filename)

def read_odt_contents(filename):
    with zipfile.ZipFile(filename, mode='r') as zf:
        with zf.open('content.xml', mode='r') as content:
            return content.read().decode(encoding='utf8')

def replace_odt_content(filename, replace_target, new_content):
    tempname = f'{filename}-full.zip'
    zin = zipfile.ZipFile (filename, 'r')
    zout = zipfile.ZipFile (tempname, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if item.filename == 'content.xml':
            buffer = buffer.decode('utf8').replace(replace_target, new_content).encode("utf8")
        zout.writestr(item, buffer)
    zout.close()
    zin.close()
    os.rename(tempname, filename)


def build_odt(in_xml, out_filename, human_title_text=''):
    build_skeleton_odt(out_filename, human_title_text)
    replace_odt_content(out_filename, '<office:text><text:p>replace_me</text:p></office:text>', dom_transform(in_xml))
