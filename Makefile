SHELL=/bin/bash

include Makefile.USER

BOOK_SOURCE=${BOOK_NAME}.asc
BUILD_EXEC:=bundle exec 
BUILD_BOOK=${BUILD_EXEC} asciidoctor$(ASC_EXT)
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


default: epub

test:
	echo "${MAJOR_VERSION}.${MINOR_VERSION}"

pub:
	source ~/etc/ruby_bashrc; $(BUILD_BOOK) ${VERSION_PARAMS} ${BUILD_PARAMS} ${BOOK_SOURCE}; 

epub:
	export ASC_EXT="-epub3"; make pub
	${BUILD_EXEC} epubcheck ${BOOK_NAME}.epub

html:
	export BUILD_PARAMS="-a data-uri "; make pub
	${BUILD_EXEC} htmlproofer ${BOOK_NAME}.html
