# PROGRAMS
PYTHON=/usr/bin/python3
SHELL=/bin/bash
SED=gsed


include Makefile.USER

BOOK_META:=newdemocracy.metadata.txt
BOOK_SOURCE:=${BOOK_NAME}.asc
BUILD_EXEC=bundle exec 
BUILD_BOOK=$(BUILD_EXEC) asciidoctor$(ASC_EXT)
BUILD_PARAMS=
ifeq (${MAJOR_VERSION},)
START_YEAR=2025
YEAR:=$(shell date +"%Y")
MAJOR_VERSION:=$(shell echo $$((${YEAR} - ${START_YEAR} + 1)))
endif

ifeq (${MINOR_VERSION},)
MINOR_VERSION:=$(shell date +"%m")
endif

DATE_VERSION=$(shell date +"%Y-%m-%d")

VERSION_PARAMS:=\
--attribute revnumber='${MAJOR_VERSION}.${MINOR_VERSION}' \
--attribute revdate='${DATE_VERSION}'


###
# Preamble in order. To reorder the preamble pages change this list order.

PREAMBLE:=\
	book/license.asc \
	book/dedication.asc \
	book/preface_mybrid.asc

# 	book/license.asc:book/dedication.asc:book/preface_mybrid.asc

###
# Chapters in order. To reorder chapters just change this list order.
NOT_USED:=\
	book/chapters/glossary.asc \
	book/chapters/introduction.asc \
	book/chapters/desire.asc \
	book/chapters/war.asc

CHAPTERS:=\
	book/chapters/biography.asc

# book/chapters/glossary.asc:book/chapters/introduction.asc:book/chapters/desire.asc:book/chapters/war.asc

default: epub

test:
	source ~/etc/ruby_bashrc; which bundle

book_compile: ${BOOK_META}
	preamble=$$(echo ${PREAMBLE} | ${SED} -e 's/\s\+/:/g');chapters=$$(echo ${CHAPTERS} | ${SED} -e 's/\s\+/:/g'); echo $$preamble $$chapters;  ${PYTHON} bin/book_compile.py $$preamble $$chapters

pub: book_compile
	source ~/etc/ruby_bashrc; $(BUILD_BOOK) ${VERSION_PARAMS} ${BUILD_PARAMS} ${BOOK_SOURCE}; 

epub:
	export ASC_EXT="-epub3"; make pub
	${BUILD_EXEC} epubcheck ${BOOK_NAME}.epub

html:
	export BUILD_PARAMS="-a data-uri "; make pub
	${BUILD_EXEC} htmlproofer ${BOOK_NAME}.html
