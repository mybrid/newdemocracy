#/usr/bin/env python3

import argparse
import glob
import logging
import os
from pathlib import Path
import re
import sys

logger = logging.getLogger(__file__)

class BookCompile():
    """Preprocess ASC fies and compile into final ASC content."""
    
    MODULE_PATH = Path(__file__).parent
    BOOK_PATH = Path().cwd()
    BOOK_NAME = BOOK_PATH.parts[-1]
    BOOK_FILE = Path(BOOK_NAME + ".asc")
    BOOK_META_FILE = Path(BOOK_NAME + ".metadata.txt")
    
    def __init__(self):
        self.chapter = {}
        self.preamble = {}
    
    def init_args(self, argv):
        """argparse.ArgumentParser"""
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument(
            'preamble',
            help="Preamble files before chapters in order of inclusion, colon separated."
        )
        parser.add_argument(
            "chapters",
            help="Chapter files in order of inclusion, colon separated."
        )
        self.argparser = parser
        self.args = parser.parse_args(args=argv)
        
        self.preamble['files'] = self.args.preamble.split(':')
        self.chapter['files'] = self.args.chapters.split(':')
        validated = True
        for validate_file in (self.preamble['files'] + self.chapter['files']):
            if not Path(validate_file).exists():
                validated = False
                logger.warning(f"{validate_file} input file not found.")
                
        if not validated:
            logger.warning("Fatal error: missing input file[s].")
            sys.exit(-1)

        return
    
    def clean(self):
        """Clean output files."""
        
        # Chapter files are sym links.
        chapter_files = glob.glob("ch*.asc")
        for chapter_file in chapter_files:
            Path(chapter_file).unlink()
            print(f"{chapter_file} sym link removed") 
        
        # Compiled book file
        if self.BOOK_FILE.exists():
            self.BOOK_FILE.unlink()
            print(f"{self.BOOK_FILE} removed")         


    def run(self, argv):
        """quick script"""
        
        self.init_args(argv)
        self.clean()
        self.preamble['includes'] = [f"include::{x}[]"
                                     for x in self.preamble['files']]
        self.chapter['links'] = []
        self.chapter['includes'] = []
        for (i, chapter_file) in enumerate(self.chapter['files']):
            file_name = Path(chapter_file).name
            j = i + 1
            self.chapter['links'].append(f"ch{j:02}-{file_name}")
            self.chapter['includes'].append(f"include::{self.chapter['links'][-1]}[]")
            
        for include in (self.preamble['includes'] + self.chapter['includes']):
            print(include)
            
        for (i, chapter_file) in enumerate(self.chapter['links']):
            os.symlink(self.chapter['files'][i], chapter_file)
            print(f"Link: {self.chapter['files'][i]} -> {chapter_file}")
            with Path(chapter_file).open('r', encoding='utf8') as chapter_fh:
                chapter_lines = chapter_fh.readlines()
            chapter_name = chapter_file.split('.')[0]
            chapter_lines[0] = f"[[{chapter_name}]]\n"
            with Path(self.chapter['files'][i]).open('w', encoding='utf8') as chapter_fh:
                chapter_fh.writelines(chapter_lines)
                
        with self.BOOK_META_FILE.open('r', encoding='utf8') as meta_fh:
            meta_lines = meta_fh.readlines()
        with self.BOOK_FILE.open('w', encoding='utf8') as book_fh:
            for meta_line in meta_lines:
                if meta_line.find('{CHAPTERS}') > -1:
                    for chapter_file in self.chapter['includes']:
                        book_fh.write(chapter_file + '\n')
                        book_fh.write('\n')
                elif meta_line.find('{PREAMBLE}') > -1:
                    for preamble_file in self.preamble['includes']:
                        book_fh.write(preamble_file + '\n')
                        book_fh.write('\n')
                else:
                    book_fh.write(meta_line)
        print(f"{self.BOOK_FILE} created.")


# -----------------------------------------------------------------------------
#
#  main
# -----------------------------------------------------------------------------

def main(argv):

    book_compile = BookCompile()
    book_compile.run(argv)

# end main
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    main(sys.argv[1:])

# -----------------------------------------------------------------------------
#                              EOF