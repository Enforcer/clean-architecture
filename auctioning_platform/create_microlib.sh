#!/usr/bin/env bash
read -p "Please enter name of a new microlib: "  NAME
echo "Creating $NAME"

NORMALIZED_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]')

mkdir -p $NORMALIZED_NAME/$NORMALIZED_NAME
touch $NORMALIZED_NAME/$NORMALIZED_NAME/__init__.py
mkdir $NORMALIZED_NAME/tests
touch $NORMALIZED_NAME/tests/__init__.py
echo "[pytest]" > $NORMALIZED_NAME/pytest.ini
touch $NORMALIZED_NAME/requirements.txt
echo """from setuptools import find_packages, setup

setup(
    name=\"$NORMALIZED_NAME\",
    packages=find_packages(),
    install_requires=[],
    extra_requires=[],
    python_requires=\">=3.6\"
)""" > $NORMALIZED_NAME/setup.py
