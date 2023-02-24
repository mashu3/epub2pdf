import io
import os
import re
import img2pdf
import pikepdf
import zipfile
import argparse
import warnings
from bs4 import BeautifulSoup
from pikepdf import OutlineItem

warnings.filterwarnings('ignore', category=UserWarning)
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

class EpubToPdfConverter:
    def __init__(self, input_path: str, output_path: str, pagelayout:str, direction:str):
        self.epub_path = input_path
        self.output_path = output_path
        self.pagelayout = pagelayout
        self.direction = direction

    def extract_contents(self, epub):
        contents = epub.namelist()
        page_names = []
        cover_name = []
        copyright_name = []
        for item in contents:
            extension = item.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png']:
                page_names.append(item)
                if re.search(r'cover', item, re.IGNORECASE):
                    cover_name.append(item)
                elif re.search(r'copyright', item, re.IGNORECASE):
                    copyright_name.append(item)
            if extension == 'ncx':
                ncx_name = item
            if extension == 'opf':
                opf_name = item
        page_names = sorted(set(page_names) - set(cover_name) - set(copyright_name))
        page_names = cover_name + sorted(page_names, key=lambda name: [int(x) if x.isdigit() else x for x in re.compile(r'(\d+)').split(name)]) + copyright_name
        page_items = []
        for page_name in page_names:
            page_items.append(epub.open(page_name))
        return page_names, page_items, ncx_name, opf_name

    def extract_index(self, epub, page_names, ncx_name: str):
        page_index = []
        with epub.open(ncx_name) as ncx_file:
            ncx_content = ncx_file.read()
        ncx_soup = BeautifulSoup(ncx_content, 'lxml')
        navpoints = ncx_soup.find_all('navpoint')
        ncx_path = os.path.dirname(ncx_name) + '/'
        for navpoint in navpoints:
            nav_label = navpoint.navlabel.text.strip()
            nav_text = navpoint.content['src']
            if nav_text.startswith(ncx_path):
                nav_text = nav_text[len(ncx_path):]
            else:
                nav_text = os.path.join(ncx_path, nav_text)
            if nav_text.endswith('.xhtml'):
                with epub.open(nav_text) as xhtml_file:
                    xhtml_content = xhtml_file.read()
                xhtml_soup = BeautifulSoup(xhtml_content, 'html.parser')
                img_tags = xhtml_soup.find_all('image')
                if len(img_tags) == 0:
                    img_tags = xhtml_soup.find_all('img')
                for img_tag in img_tags:
                    try:
                        img_link = img_tag['xlink:href']
                    except KeyError:
                        img_link = img_tag['src']
                    image_href = os.path.abspath(os.path.join(os.path.dirname(nav_text), img_link))
                    image_href = os.path.relpath(image_href, os.getcwd())

                    index_number = page_names.index(image_href)
                    page_index.append([nav_label, index_number])
            else:
                index_number = page_names.index(nav_text)
                page_index.append([nav_label, index_number])
        return page_index

    def extract_metadata(self, epub, opf_name: str):
        with epub.open(opf_name) as opf_file:
            opf_content = opf_file.read()
        opf_soup = BeautifulSoup(opf_content, 'lxml')
        metadata = opf_soup.find('metadata')    
        epub_metadata = {}
        for key in ['title', 'creator', 'publisher', 'date', 'language']:
            values = metadata.find_all('dc:'+key)
            if key == 'creator':
                if values:
                    epub_metadata[key] = [value for value in values]
            else:
                if values:
                    epub_metadata[key] = values[0].text
                else:
                    epub_metadata[key] = None
        return epub_metadata

    def convert(self):
        with zipfile.ZipFile(self.epub_path) as epub:
            page_names = self.extract_contents(epub)[0]
            page_items = self.extract_contents(epub)[1]
            ncx_name = self.extract_contents(epub)[2]
            opf_name = self.extract_contents(epub)[3]
            page_index = self.extract_index(epub, page_names, ncx_name)
            epub_metadata = self.extract_metadata(epub, opf_name)
            
        pdf_obj = io.BytesIO(img2pdf.convert(page_items))
            
        with pikepdf.Pdf.open(pdf_obj) as pdf:
            with pdf.open_metadata(set_pikepdf_as_editor=False) as pdf_metadata:
                pdf_metadata['dc:title'] = epub_metadata['title'] if epub_metadata['title'] else ''
                pdf_metadata['dc:creator'] = epub_metadata['creator'] if epub_metadata['creator'] else ''
                pdf_metadata['dc:publisher'] = epub_metadata['publisher'] if epub_metadata['publisher'] else ''
                pdf_metadata['xmp:CreateDate'] = epub_metadata['date'] if epub_metadata['date'] else ''
                pdf_metadata['pdf:Language'] = epub_metadata['language'] if epub_metadata['language'] else ''
                pdf_metadata['pdf:Producer'] = ''
            pdf_index = []
            for index in page_index:
                pdf_index.append(OutlineItem(index[0], index[1]))
            with pdf.open_outline() as outline:
                outline.root.extend(pdf_index)
            if self.pagelayout is not None:
                if not hasattr(pdf.Root, 'PageLayout') \
                or pdf.Root.PageLayout != '/' + self.pagelayout:
                    pdf.Root.PageLayout = pikepdf.Name('/' + self.pagelayout)
            if self.direction is not None:
                if not hasattr(pdf.Root, 'ViewerPreferences'):
                    pdf.Root.ViewerPreferences = pikepdf.Dictionary()
                if not hasattr(pdf.Root.ViewerPreferences, 'Direction') \
                    or pdf.Root.ViewerPreferences.Direction != '/' + self.direction:
                        pdf.Root.ViewerPreferences.Direction = pikepdf.Name('/' + self.direction)
            if self.output_path is None:
                filename, _ = os.path.splitext(self.epub_path)
                output_path = f"{filename}.pdf"
            else:
                output_path = self.output_path
            pdf.save(output_path, linearize=True)

class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=6, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
    def _split_lines(self, text, _):
        return text.splitlines()

def main():
    parser = argparse.ArgumentParser(description='Convert fixed-layout EPUB file such as comics and manga to PDF file', formatter_class=HelpFormatter)
    parser.add_argument('input_path', nargs='?', metavar='input_path', type=str,
                        help='path to the input EPUB file')
    parser.add_argument('-o', '--output', dest='output_path', type=str, default=None,
                        help='''\
path to the output PDF file. 
If not specified, the output file name is generated from the input EPUB file name.''')
    parser.add_argument('-p', '--pagelayout', type=str, default='TwoPageRight', 
                        choices=['SinglePage', 'OneColumn', 'TwoColumnLeft', 'TwoColumnRight', 'TwoPageLeft', 'TwoPageRight'],
                        help='''\
SinglePage -> Single page display
OneColumn -> Enable scrolling
TwoPageLeft -> Spread view
TwoColumnLeft -> Spread view with scrolling
(default) TwoPageRight -> Separate Cover, Spread View
TwoColumnRight -> Separate Cover, Scrolling Spread View''')
    parser.add_argument('-d', '--direction', type=str, default='R2L', choices=['L2R', 'R2L'],
                        help='''\
L2R -> Left Binding
(default)R2L -> Right Binding''')

    args = parser.parse_args()
    if args.input_path is None:
        parser.print_usage()
        parser.print_help()
        exit()
    if not args.input_path.endswith('.epub'):
        print('Error: The input file must be an EPUB file.')
        exit()
    if args.output_path is not None:
        if not args.output_path.endswith('.pdf'):
            print('Error: The output file must be an PDF file.')
            exit()
    
    converter = EpubToPdfConverter(args.input_path, args.output_path, args.pagelayout, args.direction)
    converter.convert()

if __name__ == '__main__':
    main()