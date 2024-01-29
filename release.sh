#!/usr/bin/env sh

./build.sh
python -m twine upload --repository pypi dist/*$1*.whl
