#!/usr/bin/env bash
set -e
for d in day-*; do echo "== $d"; PYTHONPATH=. python3 -m unittest discover -s "$d" ; done
