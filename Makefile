NAME=dfman
VERSION=$(shell PYTHONPATH=. python -c "from $(NAME).__pkginfo__ import version; print(version)")
VENV=venv
PIP=$(VENV)/bin/pip
PYLINT=$(VENV)/bin/pylint
SDIR=$(NAME)
TDIR=tests
BUILD_DIR=build/lib

help:
	@echo "Use: \`make <target>' where <target> is one of"
	@echo "  deb         build .deb package (only on Debian based distros)"
	@echo "  dev         setup dev environment with virtualenv"
	@echo "  docs        generate all docs including man pages"
	@echo "  lint        check $(NAME) sources with pylint"
	@echo "  sdist       build source .tar.gz package"
	@echo "  rpm         build .rpm package (only on RH based distros)"
	@echo "  sdist       build source .tar.gz package"
	@echo "  test        run whole test suit of $(NAME)"
	@echo "  venv        setup virtualenv"

$(PIP):
	virtualenv $(VENV)

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install -Ur requirements.txt

build:
	python setup.py build

clean:
	git clean -fdx

deb:
	echo 'nothing here yet'

dev: venv
	$(PIP) install -Ur requirements.devel

docs:
	echo 'nothing here yet'

lint: build
	$(PYLINT) $(BUILD_DIR)/$(NAME)

localinstall:
	$(PIP) install . --upgrade

rpm:
	echo 'nothing here yet'

sdist:
	python setup.py sdist

test:
	python -m unittest discover -v --start-directory=$(TDIR) --pattern=*_test.py

all: clean lint test docs sdist deb rpm

.PHONY: help build clean dev init lint localinstall sdist test all
