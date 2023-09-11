from setuptools import setup, find_packages

VERSION = "0.1.0"

INSTALL_REQUIRES = (
    "lxml",
    "mobi",
    "Pillow",
    "pikepdf",
    "img2pdf"
)
CLASSIFIERS=[
    'License :: OSI Approved :: GNU General Public License v3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11'
]

setup(
    name="epub2pdf",
    version=VERSION,
    author="mashu3",
    description="Convert fixed-layout manga/comic files(epub, azw3, mobi) to PDF file.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="epub mobi azw3 pdf converter",
    license='GPLv3',
    url="https://github.com/mashu3/epub2pdf",
    package_dir={"": "src"},
    py_modules=["epub2pdf"],
    packages = find_packages("src"),
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "epub2pdf=epub2pdf:main",
        ]
    }
)