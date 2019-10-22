#!/bin/bash
set -e
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
        mypy --ignore-missing-imports $dirname
    fi
done
