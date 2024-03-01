#!/usr/bin/env sh

python -m build
pydoc-markdown --render-toc > docs/src/api.md
