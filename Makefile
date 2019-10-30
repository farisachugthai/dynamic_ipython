PYTEST_EXE ?= $(shell which py.test)

help:
	@echo "Please use one of the following targets.:"
	@echo "html"
	@echo "pytest"
	@echo "clean"
	@echo "clean-all"

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

.PHONY: help html pytest clean clean-all
