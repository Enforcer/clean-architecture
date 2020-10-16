#!/bin/bash
MODULES_PATHS=""
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
	MODULES_PATHS="$MODULES_PATHS $dirname/$dirname"
    fi
done

exec python -m pylint $MODULES_PATHS
