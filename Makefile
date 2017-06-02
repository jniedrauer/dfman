NAME=dfman
VERSION=$(shell PYTHONPATH=. python -c "from $(NAME).__pkginfo__ import version; print(version)")
VENV=venv
PYTHON=python3
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
	@echo "  rpm         build .rpm package (only on RH based distros)"
	@echo "  sdist       build source .tar.gz package"
	@echo "  test        run whole test suit of $(NAME)"
	@echo "  venv        setup virtualenv"

$(PIP):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(PIP) install -Ur requirements.txt

clean:
	git clean -fdx

deb:
	python setup.py bdist_deb

dev: venv
	$(PIP) install -Ur requirements.devel

docs:
	echo 'nothing here yet'

lint:
	$(PYLINT) $(NAME)

rpm:
	python setup.py bdist_rpm

sdist:
	python setup.py sdist

test:
	python -m unittest discover -v --start-directory=$(TDIR) --pattern=*_test.py

all: clean lint test docs sdist deb rpm

.PHONY: help clean dev lint sdist test all
