from setuptools import setup, find_packages

VERSION = "0.0.1"

INSTALL_REQUIRES = (
    "Pillow",
    "pikepdf",
    "img2pdf",
    "beautifulsoup4"
)
setup(
    name="epub2pdf",
    version=VERSION,
    author="mashu3",
    description="Convert fixed-layout EPUB file such as manga to PDF file.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="epub pdf converter",
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