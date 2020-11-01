#!/bin/bash
flake8 ./
black -l 120 ./
isort ./
./run_mypy.sh
./run_pylint.sh
pytest
