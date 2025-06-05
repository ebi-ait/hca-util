.PHONY: build

VENV = .venv
PYTHON = $(VENV)/bin/python
NOSETESTS = $(VENV)/bin/nosetests
PIP = $(VENV)/bin/pip
TWINE = $(VENV)/bin/twine
ROOT := $(shell pwd)

setup:
	$(PIP) install -r requirements-dev.txt

build:
	@echo "build"
	$(PYTHON) setup.py sdist bdist_wheel

check:
	$(TWINE) check dist/*

clean:
	@echo "clean"
	rm -rf dist/*
	rm -rf build/*

test:
	@echo "test"
	$(NOSETESTS)

publish:
	@echo "publish"
	$(TWINE) upload dist/*

