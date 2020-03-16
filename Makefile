.PHONY: build

build:
	@echo "build"
	python setup.py sdist bdist_wheel

check:
	twine check dist/*

clean:
	@echo "clean"
	rm -rf dist/*
	rm -rf build/*

test:
	@echo "test"
	python -m tests.test_hca_util

publish:
	@echo "publish"
	twine upload dist/*
