# -*- coding: utf-8 -*-
# Copyright (c) 2023 mashu3
# This software is released under the GNU General Public License v3, see LICENSE.

import io
import os
import sys
import mobi
import shutil
import img2pdf
import pikepdf
import zipfile
import argparse
import warnings
from lxml import etree
warnings.filterwarnings('ignore', category=UserWarning)

class EpubPdfConverter(): 
    def __init__(self, input_path: str, output_path: str, pagelayout:str, pagemode:str, direction:str):
        self.input_path = input_path
        self.output_path = output_path
        self.pagelayout = pagelayout
        self.pagemode = pagemode
        self.direction = direction
    
    # Function to determine whether the given path is a mobi filr or azw file or not
    def is_mobi_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in ['.mobi', '.azw3', '.azw']
    
    # Function to determine whether the given path is an epub file or not
    def is_epub_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in ['.epub']
    
    # Function to extract the contents of an EPUB file
    def extract_epub_contents(self, epub):
        contents = epub.namelist()
        ncx_names = []
        opf_names = []
        for item in contents:
            extension = item.split('.')[-1].lower()
            if extension == 'ncx':
                ncx_names.append(item)
            if extension == 'opf':
                opf_names.append(item)
        flag = False
        for ncx in ncx_names:
            if 'standard' in ncx:
                ncx_name = ncx
                flag = True
        if not flag:
            ncx_name = ncx_names[0]
        flag = False
        for opf in opf_names:
            if 'standard' in opf:
                opf_name = opf
                flag = True
        if not flag:
            opf_name = opf_names[0]
        page_names = []
        with epub.open(opf_name) as opf:
            opf_content = opf.read()
            opf_tree = etree.fromstring(opf_content)
            namespace = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}
            manifest = opf_tree.find('opf:manifest', namespaces=namespace)
            for item in manifest.findall('opf:item[@media-type="image/jpeg"]', namespaces=namespace):
                page_names.append(os.path.join(os.path.dirname(opf_name), item.get('href').replace('/', os.sep)).replace(os.sep, '/'))
            for item in manifest.findall('opf:item[@media-type="image/png"]', namespaces=namespace):
                page_names.append(os.path.join(os.path.dirname(opf_name), item.get('href').replace('/', os.sep)).replace(os.sep, '/'))
        page_items = []
        for page_name in page_names:
            page_items.append(epub.open(page_name))
        return page_names, page_items, ncx_name, opf_name

    # Function to extract the index of an EPUB file
    def extract_epub_index(self, epub, page_names, ncx_name: str):
        page_index = []
        with epub.open(ncx_name) as ncx_file:
            ncx_content = ncx_file.read()
        ncx_tree = etree.fromstring(ncx_content)
        namespace = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/', 'html': 'http://www.w3.org/1999/xhtml', 'svg':'http://www.w3.org/2000/svg'}
        navmap = ncx_tree.find('ncx:navMap', namespaces=namespace)
        navpoints = navmap.findall('ncx:navPoint', namespaces=namespace)
        ncx_path = os.path.dirname(ncx_name) + '/'
        for navpoint in navpoints:
            nav_label = navpoint.find('ncx:navLabel/ncx:text', namespaces=namespace).text.strip()
            nav_text = navpoint.find('ncx:content', namespaces=namespace).get('src')
            if nav_text.startswith(ncx_path):
                nav_text = nav_text[len(ncx_path):]
            else:
                nav_text = os.path.join(ncx_path, nav_text)
            if nav_text.endswith('.xhtml'):
                with epub.open(nav_text) as xhtml_file:
                    xhtml_content = xhtml_file.read()
                xhtml_tree = etree.fromstring(xhtml_content)
                img_tags = xhtml_tree.findall('.//svg:image', namespaces=namespace)
                if len(img_tags) == 0:
                    img_tags = img_tags = xhtml_tree.findall('.//svg:img', namespaces=namespace)
                for img_tag in img_tags:
                    img_link = img_tag.get('{http://www.w3.org/1999/xlink}href', img_tag.get('src'))
                    image_href = os.path.abspath(os.path.join(os.path.dirname(nav_text), img_link))
                    image_href = os.path.relpath(image_href, os.getcwd()).replace(os.sep, '/')
                    index_number = page_names.index(image_href)
                    page_index.append([nav_label, index_number])
            else:
                index_number = page_names.index(nav_text)
                page_index.append([nav_label, index_number])
        return page_index

    # Function to extract the metadata of an EPUB file
    def extract_epub_metadata(self, epub, opf_name: str):
        with epub.open(opf_name) as opf_file:
            opf_content = opf_file.read()
        opf_tree = etree.fromstring(opf_content)
        namespace = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}
        metadata = opf_tree.find('opf:metadata', namespaces=namespace)    
        epub_metadata = {}
        for key in ['title', 'creator', 'publisher', 'date', 'language']:
            values = metadata.xpath('./dc:' + key, namespaces=namespace)
            if key == 'creator':
                if values:
                    epub_metadata[key] = [value.text for value in values]
            else:
                if values:
                    epub_metadata[key] = values[0].text
                else:
                    epub_metadata[key] = None
        return epub_metadata

    # Function to convert input files to a PDF file
    def convert(self):
        if self.is_mobi_file(self.input_path):
            try:
                sys.stdout = open(os.devnull, 'w')
                tmpfile, self.epub_path = mobi.extract(self.input_path)
                sys.stdout.close()
                sys.stdout = sys.__stdout__
                if self.is_epub_file(self.epub_path):
                    with zipfile.ZipFile(self.epub_path) as epub:
                        page_names = self.extract_epub_contents(epub)[0]
                        page_items = self.extract_epub_contents(epub)[1]
                        ncx_name = self.extract_epub_contents(epub)[2]
                        opf_name = self.extract_epub_contents(epub)[3]
                        page_index = self.extract_epub_index(epub, page_names, ncx_name)
                        epub_metadata = self.extract_epub_metadata(epub, opf_name)
                shutil.rmtree(tmpfile)
            except Exception as e:
                print(f"Error extracting the MOBI file: {e}")
        elif self.is_epub_file(self.input_path):
            with zipfile.ZipFile(self.input_path) as epub:
                page_names = self.extract_epub_contents(epub)[0]
                page_items = self.extract_epub_contents(epub)[1]
                ncx_name = self.extract_epub_contents(epub)[2]
                opf_name = self.extract_epub_contents(epub)[3]
                page_index = self.extract_epub_index(epub, page_names, ncx_name)
                epub_metadata = self.extract_epub_metadata(epub, opf_name)
        else:
            raise('Error: The input file format is not supported. The currently supported formats are: .mobi, .azw3, .azw, and .epub.')
        
        pdf_obj = io.BytesIO(img2pdf.convert(page_items))
        
        with pikepdf.Pdf.open(pdf_obj) as pdf:
            if self.is_epub_file(self.input_path) or self.is_epub_file(self.epub_path):
                with pdf.open_metadata(set_pikepdf_as_editor=False) as pdf_metadata:
                    pdf_metadata['dc:title'] = epub_metadata['title'] if epub_metadata['title'] else ''
                    pdf_metadata['dc:creator'] = epub_metadata['creator'] if epub_metadata['creator'] else ''
                    pdf_metadata['dc:publisher'] = epub_metadata['publisher'] if epub_metadata['publisher'] else ''
                    pdf_metadata['xmp:CreateDate'] = epub_metadata['date'] if epub_metadata['date'] else ''
                    pdf_metadata['pdf:Language'] = epub_metadata['language'] if epub_metadata['language'] else ''
                    pdf_metadata['pdf:Producer'] = ''
                pdf_index = []
                for index in page_index:
                    pdf_index.append(pikepdf.OutlineItem(index[0], index[1]))
                with pdf.open_outline() as outline:
                    outline.root.extend(pdf_index)
            if self.pagelayout is not None:
                if not hasattr(pdf.Root, 'PageLayout') \
                or pdf.Root.PageLayout != '/' + self.pagelayout:
                    pdf.Root.PageLayout = pikepdf.Name('/' + self.pagelayout)
            if self.pagemode is not None:
                if not hasattr(pdf.Root, 'PageMode') \
                or pdf.Root.PageMode != '/' + self.pagemodet:
                    pdf.Root.PageMode = pikepdf.Name('/' + self.pagemode)
            if self.direction is not None:
                if not hasattr(pdf.Root, 'ViewerPreferences'):
                    pdf.Root.ViewerPreferences = pikepdf.Dictionary()
                if not hasattr(pdf.Root.ViewerPreferences, 'Direction') \
                    or pdf.Root.ViewerPreferences.Direction != '/' + self.direction:
                        pdf.Root.ViewerPreferences.Direction = pikepdf.Name('/' + self.direction)
            if self.output_path is None:
                if os.path.isdir(self.input_path):
                    pdf_filename = os.path.basename(self.input_path) + '.pdf'
                    output_path = os.path.join(self.input_path, pdf_filename).replace(os.sep, '/')
                else:
                    pdf_filename, _ = os.path.splitext(self.input_path)
                    output_path = f"{pdf_filename}.pdf"
            else:
                output_path = self.output_path
            if os.path.exists(output_path):
                os.remove(output_path)
            pdf.save(output_path, linearize=True)
        return None

class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=6, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
    def _split_lines(self, text, _):
        return text.splitlines()

def main():
    parser = argparse.ArgumentParser(description='Convert fixed-layout manga/comic files(epub, azw3, mobi) to PDF file.', formatter_class=HelpFormatter)
    parser.add_argument('input_path', nargs='?', metavar='input_path', type=str,
                        help='input file path or directory path')
    parser.add_argument('-o', '--output', dest='output_path', type=str, default=None,
                        help='''\
path to the output PDF file. 
If not specified, the output file name is generated from the input file or directory name.''')
    parser.add_argument('-l', '--pagelayout', type=str, default='TwoPageRight', 
                        choices=['SinglePage', 'OneColumn', 'TwoColumnLeft', 'TwoColumnRight', 'TwoPageLeft', 'TwoPageRight'],
                        help='''\
SinglePage -> Single page display
OneColumn -> Enable scrolling
TwoPageLeft -> Spread view
TwoColumnLeft -> Spread view with scrolling
(default) TwoPageRight -> Separate Cover, Spread View
TwoColumnRight -> Separate Cover, Scrolling Spread View''')
    parser.add_argument('-m', '--pagemode', type=str, default='UseNone', 
                        choices=['UseOutlines', 'UseThumbs', 'FullScreen', 'UseOC', 'UseAttachments'],
                        help='''\
(default) UseNone -> Neither document outline nor thumbnail images visible
UseOutlines -> Document outline visible
UseThumbs -> Thumbnail images visible
FullScreen -> Full-screen mode
UseOC -> Optional content group panel visible
UseAttachments -> Attachments panel visible''')
    parser.add_argument('-d', '--direction', type=str, default='R2L', choices=['L2R', 'R2L'],
                        help='''\
L2R -> Left Binding
(default) R2L -> Right Binding''')

    args = parser.parse_args()
    if args.input_path is None:
        parser.print_usage()
        parser.print_help()
        sys.exit(1)
    if not os.path.isdir(args.input_path):
        ext = os.path.splitext(args.input_path)[1].lower()
        if not ext in ['.epub', '.mobi', '.azw3', '.azw']:
            print('Error: The input file format is not supported. The currently supported formats are: .mobi, .azw3, .azw, and .epub.')
            sys.exit(1)
    if args.output_path is not None:
        if not args.output_path.endswith('.pdf'):
            print('Error: The output file must be an PDF file.')
            sys.exit(1)
    
    converter = EpubPdfConverter(args.input_path, args.output_path, args.pagelayout, args.pagemode, args.direction)
    converter.convert()

if __name__ == '__main__':
    main()