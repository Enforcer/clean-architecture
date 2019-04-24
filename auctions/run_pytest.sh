#!/bin/bash
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
        pytest $dirname
    fi
done
pytest web_app

