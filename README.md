# epub2pdf.py
## Overview
This is a Python script for converting fixed-layout EPUB files such as comics and manga to PDF file, which can be executed from the command line with some arguments.
This Python script only supports DRM-free EPUB files of a specific format.

## Requirement
The script uses the Python libraries **[img2pdf](https://pypi.org/project/img2pdf/)** and **[pikepdf](https://pypi.org/project/pikepdf/)** to do the conversion.
Moreover, it uses **[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)** to read the EPUB files.

It requires the installation of these packages in order to work properly.

## Usage
The program can be executed from the command line with the following options:
- The `input_path` argument is the path to the input EPUB file. To correctly execute the Python script, the `input_path` argument must be set to the path of the input EPUB file.
- The `output_path` argument is the path to the output PDF file. To use the script, simply run the Python script with the path to the input EPUB file as the argument. If the `--output` option is not specified, the output file name will be generated from the input EPUB file name.
- The `pagelayout` argument is the page layout of the PDF file. The `pagelayout` parameter can take in the following values:
    - `SinglePage` -> Single page display
    - `OneColumn` -> Enable scrolling
    - `TwoPageLeft` -> Spread view
    - `TwoColumnLeft` -> Spread view with scrolling
    - (default) `TwoPageRight` -> Separate Cover, Spread View
    - `TwoColumnRight` -> Separate Cover, Scrolling Spread View
- The `direction` argument is the reading direction of the PDF file. The `direction` parameter can take in the following values:
    - `L2R` -> Left Binding
    - (default) `R2L` -> Right Binding

By default, the page layout is set to `TwoPageRight` and the reading direction to `R2L`, which are suitable for Japanese manga.

There is a possibility that the script will not run correctly if an unexpected EPUB format is encountered, as the script may not be able to handle it correctly.

## Examples
- To convert `my_manga.epub` to `my_manga.pdf` using the default settings:

    `$ python epub2pdf.py my_manga.epub`

- To convert `my_manga.epub` to `my_manga_spread.pdf` with a spread view and right binding:

    `$ python epub2pdf.py my_manga.epub -o my_manga_spread.pdf`

- To convert `my_comic.epub` to `my_comic.pdf` with a TwoPage view and left binding:

    `$ python epub2pdf.py my_comic.epub -o my_comic.pdf -p TwoPageLeft -d L2R`

Once the arguments are given, the program will convert the EPUB file to PDF.