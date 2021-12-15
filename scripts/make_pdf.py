from odf.opendocument import OpenDocumentText
from odf.style import PageLayout, MasterPage, Header, Footer, PageLayoutProperties, Style, TextProperties, ParagraphProperties, Columns, Column
from odf.text import P, PageNumber, A, Span
import lxml.etree as ET
import zipfile

import os.path
import sys
import os

xslt_file = os.path.join(os.path.dirname(__file__), "pb2odt.xsl")

def dom_transform(xml_file):
    dom = ET.parse(xml_file)
    xslt = ET.parse(xslt_file)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)

    domString = ET.tostring(newdom, pretty_print=True, encoding='unicode').replace("---", ":")
    return domString

def build_skeleton_odt(filename):
    textdoc = OpenDocumentText()
    pl = PageLayout(name="pagelayout")
    plp = PageLayoutProperties(pagewidth='11in', pageheight='8.5in', printorientation="landscape",
                                    margintop='0.25in', marginleft='0.25in', marginbottom='0.25in',
                                    marginright='0.25in', numformat='1', writingmode='lr-tb')
    
    
    columnsStyle = Columns(columncount=3)
    plp.addElement(columnsStyle)
    
    pl.addElement(plp)
    textdoc.automaticstyles.addElement(pl)

    mp = MasterPage(name="Standard", pagelayoutname=pl)
    textdoc.masterstyles.addElement(mp)

    secTitle = Style(name="SECTION_TITLE", family="paragraph")
    secTitle.addElement(TextProperties(attributes={'fontsize': '16.1pt', 'fontweight': 'bold', 'fontfamily': "DejaVu Sans"}))
    textdoc.styles.addElement(secTitle)

    itemDesc = Style(name="ITEM_DESC", family="text")
    itemDesc.addElement(TextProperties(attributes={'fontsize': '9pt', 'fontfamily': "DejaVu Sans"}))
    textdoc.styles.addElement(itemDesc)

    itemTitle = Style(name="ITEM_TITLE", family="text")
    itemTitle.addElement(TextProperties(attributes={'fontsize': '9pt', 'fontweight': 'bold', 'fontfamily': "DejaVu Sans"}))
    textdoc.styles.addElement(itemTitle)

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


def build_odt(in_xml, out_filename):
    build_skeleton_odt(out_filename)
    replace_odt_content(out_filename, '<office:text><text:p>replace_me</text:p></office:text>', dom_transform(in_xml))

if __name__ == '__main__':
    build_odt(sys.argv[1], sys.argv[2])