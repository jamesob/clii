#!/usr/bin/env bash

set -e

rm -rf ./dist/
python3.8 setup.py sdist
twine upload ./dist/*
