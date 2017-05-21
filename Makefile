NAME=dfman

VERSION=$(shell PYTHONPATH=. python -c "from $(NAME).__pkginfo__ import version; print version")

SDIR=$(NAME)
TDIR=tests
BUILD_DIR=build/lib
DIST_DIR=dist

help:
	@echo "Use: \`make <target>' where <target> is one of"
	@echo "  deb         build .deb package (only on Debian based distros)"
	@echo "  docs        generate all docs including man pages"
	@echo "  lint        check $(NAME) sources with pylint"
	@echo "  sdist       build source .tar.gz package"
	@echo "  rpm         build .rpm package (only on RH based distros)"
	@echo "  sdist       build source .tar.gz package"
	@echo "  test        run whole test suit of $(NAME)"

build:
	python setup.py build

clean:
	git clean -fd

deb:
	echo 'nothing here yet'

dev:
	pip install -r requirements.devel

docs:
	echo 'nothing here yet'

init:
	pip install -r requirements.txt

lint: build
	pylint $(BUILD_DIR)/$(NAME)

rpm:
	echo 'nothing here yet'

sdist:
	python setup.py sdist

test:
	cd $(TDIR); python -m unittest discover -v --pattern=*_test.py

all: clean lint test docs sdist deb rpm

.PHONY: help build clean dev init lint sdist test all
