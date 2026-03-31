# Run all code style checks.
checks: style-fix style-check

# Code style; defines `style-check` and `style-fix`.
# TODO: I'm not sure why `style.yml` and `test.yml` GitHub workflow actions don't verify.
CODE_STYLE_EXCLUSIONS_USER := --exclude-dir data --exclude __init__.py
ifeq (,$(wildcard .plume-scripts))
dummy := $(shell git clone --depth=1 -q https://github.com/plume-lib/plume-scripts.git .plume-scripts)
endif
include .plume-scripts/code-style.mak

# ${PYTHON_FILES} is defined by the above style checking.
TAGS: tags
tags:
	etags ${PYTHON_FILES}
