# epub2pdf
## Overview
This is a Python script for converting fixed-layout EPUB/MOBI files such as comics and manga to PDF file, which can be executed from the command line with some arguments.
This Python script only supports DRM-free EPUB/MOBI files of a specific format.

## Requirement
The script uses the Python libraries **[img2pdf](https://pypi.org/project/img2pdf/)** and **[pikepdf](https://pypi.org/project/pikepdf/)** to do the conversion.
Moreover, it uses **[lxml](https://pypi.org/project/lxml/)** to read the EPUB files and  **[mobi](https://pypi.org/project/mobi/)** to handle both MOBI and AZW files.

It requires the installation of these packages in order to work properly.

## Usage
The program can be executed from the command line with the following options:
- The `input_path` argument is the path to the input file. To execute the Python script correctly, specify the `input_path` argument as the path to the input file containing manga or comic images in one of the supported formats, such as `epub`, `mobi`, or  `azw`.
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

### Installing directly from the Git repository
To install the package directly from the Git repository, run the following command:
```
$ pip install git+https://github.com/mashu3/epub2pdf.git
```
### Installing by cloning the Git repository
To install the package by cloning the Git repository, follow these steps:
```
$ git clone https://github.com/mashu3/epub2pdf.git
$ cd epub2pdf/
$ pip install .
```

## Examples
- To convert `my_manga.epub` to `my_manga.pdf` using the default settings:

    `$ epub2pdf my_manga.epub`

- To convert `my_manga.epub` to `my_manga_spread.pdf` with a spread view and right binding:

    `$ epub2pdf my_manga.epub -o my_manga_spread.pdf`

- To convert `my_comic.epub` to `my_comic.pdf` with a TwoPage view and left binding:

    `$ epub2pdf my_comic.epub -o my_comic.pdf -p TwoPageLeft -d L2R`

Once the arguments are given, the program will convert the EPUB file to PDF.

## Credits
[KindleUnpack](https://github.com/kevinhendricks/KindleUnpack)

## Author
[mashu3](https://github.com/mashu3)

[![Authors](https://contrib.rocks/image?repo=mashu3/epub2pdf)](https://github.com/mashu3/epub2pdf/graphs/contributors)
