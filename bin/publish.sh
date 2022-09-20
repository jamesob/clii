#!/usr/bin/env bash

set -e

rm -rf ./dist/
python3 setup.py sdist
twine upload ./dist/*
