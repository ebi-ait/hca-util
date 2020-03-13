.DEFAULT_GOAL := build_pkg

build_pkg: # use build_pkg as build is a folder name in dir
	@echo "Build"
	python setup.py sdist bdist_wheel

check:
	twine check dist/*

clean:
	@echo "Clean"
	rm -rf dist/*

test:
	@echo "Test"
	python -m tests.test_hca_util

publish:
	@echo "Publish"
	twine upload dist/*
