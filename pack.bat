#!/bin/sh
rm -r -f ./dist ./build
python.exe pack.py py2exe
release_dist.py
