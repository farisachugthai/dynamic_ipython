PYTEST_EXE ?= $(shell which py.test)
PYTHON_EXE ?= $(shell which python3)
SPHINXBUILD   = sphinx-build
SOURCEDIR     = docs/source
BUILDDIR      = docs/build
SPHINXOPTS    =

.PHONY: help html pytest clean clean-all install test setup

help:
	@echo "Please use one of the following targets.:"
	@echo "html"
	@echo "dirhtml"
	@echo "singlehtml"
	@echo "text"
	@echo "man"
	@echo "info"
	@echo "changes"
	@echo "linkcheck"
	@echo "doctest"
	@echo "coverage"
	@echo "pytest"
	@echo "clean"
	@echo "clean-all"
	@echo "install"
	@echo "test"
	@echo "setup"

html:
	@cd docs && make html

pytest:
	$(PYTEST_EXE) -v -s test

clean:
	@find . -name \*.py[cod] -delete
	@find . -name __pycache__ -delete
	@rm -rf .cache build
	@rm -f .coverage .coverage.* junit.xml tmpfile.rc conda/.version tempfile.rc coverage.xml
	@rm -rf auxlib bin conda/progressbar
	@rm -rf conda-build conda_build_test_recipe record.txt
	@rm -rf .pytest_cache

clean-all: clean
	@rm -rf *.egg-info*
	@rm -rf dist build

install:
	$(PYTHON_EXE) setup.py build
	$(PYTHON_EXE) -m pip install -U -e .

test:
	$(PYTHON_EXE) -m unittest discover

setup:
	$(PYTHON_EXE) setup.py

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
