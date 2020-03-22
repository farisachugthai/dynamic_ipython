# You can set these variables from the command line.

SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
SPHINXOPTS    =
SPHINXAUTOGEN = sphinx-autogen


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


generate:
	@$(SPHINXAUTOGEN) -t source/_templates -o source/generated source/*.rst

.PHONY: help Makefile generate
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# Vim: set noet
