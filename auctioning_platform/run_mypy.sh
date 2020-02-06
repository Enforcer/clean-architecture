#!/bin/bash
EXIT_STATUS=0
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
        mypy --ignore-missing-imports $dirname
        if [[ $? -ne 0 ]]; then
            EXIT_STATUS=1
        fi
    fi
done

exit $EXIT_STATUS
