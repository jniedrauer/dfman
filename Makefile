NAME=dfman
SDIR=./$(NAME)
TDIR=./tests

dev:
	pip install -r requirements.devel

init:
	pip install -r requirements.txt

lint:
	pylint $(SDIR)

test:
	cd $(TDIR); python -m unittest discover -v --pattern=*_test.py

.PHONY: dev init lint test
