#!/bin/bash
EXIT_STATUS=0
i=0
for dirname in $(ls); do
    if [ -d "$dirname" ] && [ -e "$dirname/setup.py" ]; then
	echo "Typechecking $dirname..."
        python -m mypy --ignore-missing-imports $dirname &
	pids[${i}]=$!
	i=$i+1
    fi
done

for pid in ${pids[*]}; do
    wait $pid || let "EXIT_STATUS=1"
done

exit $EXIT_STATUS
