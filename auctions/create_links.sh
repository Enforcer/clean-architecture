#!/bin/bash
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
        cd $dirname
        pip uninstall $(python setup.py --name) -y
        pip install -e .
        cd ..
    fi
done

